#!/usr/bin/env python3
"""Validate the question JSON tree against the canonical schema.

Usage:
    python scripts/validate_questions.py            # only fail on ERRORs
    python scripts/validate_questions.py --strict   # also fail on WARNINGs

Walks every directory listed under ``exams[].id`` in ``exams.json``. Other
top-level directories (e.g. ``old_categories``) are intentionally skipped
because they are not wired into the runtime.

Exit codes:
    0 — clean (or only warnings, in non-strict mode)
    1 — at least one ERROR (always) or WARNING (with ``--strict``)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from services.question_validator import (  # noqa: E402
    LEVEL_ERROR,
    LEVEL_WARNING,
    validate_questions_root,
)


def _wired_exam_dirs(repo_root: Path) -> set[str]:
    with open(repo_root / 'exams.json', encoding='utf-8') as f:
        exams = json.load(f).get('exams', [])
    return {e['id'] for e in exams if isinstance(e, dict) and 'id' in e}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true',
                        help='exit non-zero on warnings as well')
    parser.add_argument('--root', default=str(REPO_ROOT / 'questions'),
                        help='questions root directory')
    parser.add_argument('--include-archive', action='store_true',
                        help='also validate top-level directories not in exams.json')
    args = parser.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f'questions root not found: {root}', file=sys.stderr)
        return 2

    if args.include_archive:
        ignore: list[str] = []
    else:
        wired = _wired_exam_dirs(REPO_ROOT)
        all_top = {name for name in os.listdir(root) if (root / name).is_dir()}
        ignore = sorted(all_top - wired)
        if ignore:
            print(f'(skipping unwired dirs: {", ".join(ignore)})', file=sys.stderr)

    issues = validate_questions_root(str(root), ignore_top_level=ignore)
    errors = [i for i in issues if i.level == LEVEL_ERROR]
    warnings = [i for i in issues if i.level == LEVEL_WARNING]

    for issue in issues:
        print(issue.format())

    print(f'\n{len(errors)} error(s), {len(warnings)} warning(s).', file=sys.stderr)

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
