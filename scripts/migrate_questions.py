#!/usr/bin/env python3
"""One-shot migration to canonical question schemas.

Converts two non-canonical shapes to the canonical form so the runtime
adapters can be deleted (see ``IMPROVEMENT_TASKS.md`` → "Unify question-JSON
schemas"):

1. ``multiple_choice`` ``options`` as a dict ``{"A": "..."}`` →
   list ``["A's text", "B's text", ...]`` ordered by sorted letter key.
   ``correct_answer`` is left unchanged (already a letter that indexes the
   resulting list).

2. ``fill_blanks`` legacy nested ``questions: [{id, text, blanks: [...]}]`` →
   canonical dict shape: a single ``description`` with ``{blank1}`` /
   ``{blank2}`` placeholders, plus ``blanks: {blank1: {correct, options},
   ...}``. Each ``___`` marker (2+ underscores) in legacy ``text`` becomes a
   ``{blankN}`` placeholder. Sub-questions are flattened into a numbered
   list joined onto the original ``description``.

Run with ``--dry-run`` first to see what would change.

Idempotent: re-running on already-canonical files is a no-op.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_UNDERSCORE_RE = re.compile(r'_{2,}')


def migrate_options_dict(question: dict) -> bool:
    """multiple_choice options dict → list. Returns True if mutated."""
    if question.get('type') != 'multiple_choice':
        return False
    options = question.get('options')
    if not isinstance(options, dict):
        return False
    question['options'] = [options[key] for key in sorted(options.keys())]
    return True


def migrate_legacy_fill_blanks(question: dict) -> bool:
    """fill_blanks legacy nested → canonical dict shape. Returns True if mutated."""
    if question.get('type') != 'fill_blanks':
        return False
    nested = question.get('questions')
    if not isinstance(nested, list) or not nested:
        return False

    blanks_dict: dict[str, dict] = {}
    sub_lines: list[str] = []
    counter = 1

    for sub_index, sub in enumerate(nested, start=1):
        text = (sub.get('text') or '').rstrip()
        sub_blanks = sub.get('blanks') or []

        new_text = text
        for blank in sub_blanks:
            marker = f'{{blank{counter}}}'
            new_text, n_subs = _UNDERSCORE_RE.subn(marker, new_text, count=1)
            if n_subs == 0:
                # Defensive: if a sub-blank doesn't have a corresponding ___ marker,
                # tack the placeholder onto the end so the question is still gradable.
                new_text = f'{new_text} {marker}'
            entry: dict = {'correct': blank.get('correct', '')}
            if isinstance(blank.get('options'), list):
                entry['options'] = blank['options']
            blanks_dict[f'blank{counter}'] = entry
            counter += 1

        sub_lines.append(f'{sub_index}. {new_text}')

    intro = (question.get('description') or '').rstrip()
    body = '\n'.join(sub_lines)
    question['description'] = f'{intro}\n\n{body}' if intro else body
    question['blanks'] = blanks_dict
    del question['questions']
    return True


def migrate_question(question: dict) -> list[str]:
    """Apply every migration. Returns names of migrations that fired."""
    applied: list[str] = []
    if migrate_options_dict(question):
        applied.append('options_dict_to_list')
    if migrate_legacy_fill_blanks(question):
        applied.append('fill_blanks_nested_to_canonical')
    return applied


def migrate_file(path: Path, dry_run: bool) -> dict:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    questions = data.get('questions') or []
    counts: dict[str, int] = {}
    for q in questions:
        if not isinstance(q, dict):
            continue
        for name in migrate_question(q):
            counts[name] = counts.get(name, 0) + 1
    if counts and not dry_run:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
    return counts


def _wired_exam_dirs() -> set[str]:
    with open(REPO_ROOT / 'exams.json', encoding='utf-8') as f:
        exams = json.load(f).get('exams', [])
    return {e['id'] for e in exams if isinstance(e, dict) and 'id' in e}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true',
                        help='report what would change without writing')
    parser.add_argument('--root', default=str(REPO_ROOT / 'questions'),
                        help='questions root directory')
    parser.add_argument('--include-archive', action='store_true',
                        help='also migrate top-level dirs not in exams.json (e.g. old_categories)')
    args = parser.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f'questions root not found: {root}', file=sys.stderr)
        return 2

    if args.include_archive:
        ignored: set[str] = set()
    else:
        wired = _wired_exam_dirs()
        all_top = {name for name in os.listdir(root) if (root / name).is_dir()}
        ignored = all_top - wired
        if ignored:
            print(f'(skipping unwired dirs: {", ".join(sorted(ignored))})', file=sys.stderr)

    totals: dict[str, int] = {}
    files_touched = 0
    for dirpath, dirnames, filenames in os.walk(root):
        if Path(dirpath) == root:
            dirnames[:] = [d for d in dirnames if d not in ignored]
        for name in sorted(filenames):
            if not name.endswith('.json'):
                continue
            path = Path(dirpath) / name
            counts = migrate_file(path, dry_run=args.dry_run)
            if counts:
                files_touched += 1
                rel = path.relative_to(REPO_ROOT)
                pretty = ', '.join(f'{k}={v}' for k, v in sorted(counts.items()))
                print(f'{rel}: {pretty}')
                for k, v in counts.items():
                    totals[k] = totals.get(k, 0) + v

    verb = 'would migrate' if args.dry_run else 'migrated'
    summary = ', '.join(f'{k}={v}' for k, v in sorted(totals.items())) or 'nothing'
    print(f'\n{verb} {files_touched} file(s): {summary}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
