"""Schema validator for question JSON files.

Two passes:

* :func:`validate_question` — structural validation. Every issue here is an
  ``ERROR``: missing or unknown ``type``, missing ``id``, missing required
  per-type fields, malformed payloads. The runtime cannot grade these.
* :func:`lint_question` — style/canonical-shape lint. Issues here are
  ``WARNING``: legitimate today (the loader / grader / template have adapters
  for them), but they represent migration debt that we want to drive to zero
  so the adapters can be deleted. See the "Unify question-JSON schemas" entry
  in ``IMPROVEMENT_TASKS.md``.

Canonical shapes chosen here are based on the dominant in-tree variant:

* ``multiple_choice``: ``options: list[str]`` (1588 questions canonical vs.
  329 in the dict variant) and ``correct_answer: str`` containing a single
  uppercase letter ``A``..``Z`` indexing into ``options``.
* ``fill_blanks``: dict-with-placeholders shape — ``description`` carries
  ``{blank1}`` style placeholders and ``blanks`` is
  ``{blank_id: {"correct": ..., "options": [...]}}``. The legacy nested
  ``questions[].blanks[]`` shape is a warning.

File- and tree-level helpers also catch duplicate ``id`` collisions within a
file and across the whole questions tree.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterable
from dataclasses import dataclass

LEVEL_ERROR = 'ERROR'
LEVEL_WARNING = 'WARNING'

KNOWN_TYPES = frozenset({
    'code_output',
    'bug_finding',
    'code_completion',
    'code_writing',
    'multiple_choice',
    'multiple_select',
    'memory_tracing',
    'struct_size',
    'fill_blanks',
    'drag_drop',
    'recursive_trace',
})

_BLANK_PLACEHOLDER_RE = re.compile(r'\{(blank\d+)\}')
_LETTER_RE = re.compile(r'^[A-Z]$')


@dataclass(frozen=True)
class Issue:
    level: str
    code: str
    message: str
    question_id: str | None = None
    file_path: str | None = None

    def format(self) -> str:
        loc_parts: list[str] = []
        if self.file_path:
            loc_parts.append(self.file_path)
        if self.question_id:
            loc_parts.append(f'id={self.question_id}')
        loc = ' '.join(loc_parts)
        prefix = f'[{self.level}] {self.code}'
        if loc:
            return f'{prefix} ({loc}): {self.message}'
        return f'{prefix}: {self.message}'


def _err(code: str, message: str, qid: str | None = None) -> Issue:
    return Issue(LEVEL_ERROR, code, message, qid)


def _warn(code: str, message: str, qid: str | None = None) -> Issue:
    return Issue(LEVEL_WARNING, code, message, qid)


def _require_str(question: dict, field: str, qid: str | None) -> Issue | None:
    value = question.get(field)
    if not isinstance(value, str) or not value.strip():
        return _err('missing_field', f'missing or empty required string field {field!r}', qid)
    return None


def _validate_common(question: dict) -> tuple[list[Issue], str | None]:
    """Validate fields every question must carry. Returns (issues, qid)."""
    issues: list[Issue] = []
    qid = question.get('id') if isinstance(question.get('id'), str) else None
    if not qid or not qid.strip():
        issues.append(_err('missing_field', "missing or empty required string field 'id'"))
        qid = None

    qtype = question.get('type')
    if not isinstance(qtype, str) or not qtype.strip():
        issues.append(_err('missing_field', "missing or empty required string field 'type'", qid))
    elif qtype not in KNOWN_TYPES:
        issues.append(_err('unknown_type', f'unknown question type {qtype!r}', qid))

    for field in ('title', 'description'):
        err = _require_str(question, field, qid)
        if err:
            issues.append(err)
    return issues, qid


def _validate_multiple_choice(q: dict, qid: str | None) -> list[Issue]:
    issues: list[Issue] = []
    options = q.get('options')
    if isinstance(options, dict):
        # Pre-2026-04-28 the loader normalised dict→list at runtime. The data
        # has since been migrated; reject the dict shape outright.
        return [_err('non_canonical_options_dict',
                     'multiple_choice options must be list[str], not dict; run scripts/migrate_questions.py', qid)]
    if not isinstance(options, list):
        return [_err('bad_options', 'multiple_choice missing options (list[str])', qid)]
    if len(options) < 2:
        issues.append(_err('bad_options', f'multiple_choice expects ≥2 options, got {len(options)}', qid))
    if not all(isinstance(o, str) for o in options):
        issues.append(_err('bad_options', 'multiple_choice options must all be strings', qid))

    correct = q.get('correct_answer')
    if not isinstance(correct, str) or not _LETTER_RE.match(correct.strip().upper()):
        issues.append(_err('bad_correct_answer', 'multiple_choice correct_answer must be a single A-Z letter', qid))
    else:
        idx = ord(correct.strip().upper()) - ord('A')
        if not (0 <= idx < len(options)):
            issues.append(_err('correct_answer_out_of_range', f'correct_answer {correct!r} indexes outside options[0..{len(options) - 1}]', qid))
    return issues


def _validate_multiple_select(q: dict, qid: str | None) -> list[Issue]:
    issues: list[Issue] = []
    options = q.get('options')
    if not isinstance(options, list) or len(options) < 2 or not all(isinstance(o, str) for o in options):
        issues.append(_err('bad_options', 'multiple_select expects options as a list[str] with ≥2 entries', qid))
        options_len = 0
    else:
        options_len = len(options)

    correct = q.get('correct_answer')
    if isinstance(correct, str):
        letters = [a.strip().upper() for a in correct.split(',') if a.strip()]
    elif isinstance(correct, list):
        letters = [str(a).strip().upper() for a in correct]
    else:
        issues.append(_err('bad_correct_answer', 'multiple_select correct_answer must be CSV string or list[str]', qid))
        return issues

    if not letters:
        issues.append(_err('bad_correct_answer', 'multiple_select correct_answer is empty', qid))
    for letter in letters:
        if not _LETTER_RE.match(letter):
            issues.append(_err('bad_correct_answer', f'multiple_select correct_answer entry {letter!r} is not A-Z', qid))
        elif options_len:
            idx = ord(letter) - ord('A')
            if not (0 <= idx < options_len):
                issues.append(_err('correct_answer_out_of_range', f'correct_answer {letter!r} indexes outside options', qid))
    return issues


def _validate_fill_blanks(q: dict, qid: str | None) -> list[Issue]:
    issues: list[Issue] = []
    blanks = q.get('blanks')
    description = q.get('description') or ''
    placeholders = set(_BLANK_PLACEHOLDER_RE.findall(description))

    if 'questions' in q:
        # Pre-2026-04-28 the grader handled a legacy nested ``questions[].blanks[]``
        # shape. Migration flattened those into the canonical dict shape; the
        # legacy field is now an error.
        return [_err('non_canonical_fill_blanks_nested',
                     "fill_blanks must use the dict shape with {blankN} placeholders, not legacy 'questions[]'; "
                     "run scripts/migrate_questions.py", qid)]
    if not isinstance(blanks, dict):
        return [_err('bad_fill_blanks', 'fill_blanks requires a non-empty blanks dict', qid)]
    if not blanks:
        issues.append(_err('bad_blanks', 'fill_blanks requires non-empty blanks dict', qid))
    for blank_id, blank_data in blanks.items():
        if not isinstance(blank_data, dict):
            issues.append(_err('bad_blank_entry', f'blank {blank_id!r} must be an object', qid))
            continue
        if 'correct' not in blank_data or not isinstance(blank_data.get('correct'), str):
            issues.append(_err('bad_blank_entry', f'blank {blank_id!r} missing string field correct', qid))
        options = blank_data.get('options')
        if options is not None and (not isinstance(options, list) or not all(isinstance(o, str) for o in options)):
            issues.append(_err('bad_blank_entry', f'blank {blank_id!r} options must be list[str]', qid))
    declared = set(blanks.keys())
    if placeholders and not placeholders.issubset(declared):
        missing = sorted(placeholders - declared)
        issues.append(_err('placeholder_mismatch', f'description references blanks not declared: {missing}', qid))
    return issues


def _validate_drag_drop(q: dict, qid: str | None) -> list[Issue]:
    issues: list[Issue] = []
    if not isinstance(q.get('code_template'), str):
        issues.append(_err('missing_field', "drag_drop missing required string 'code_template'", qid))
    blanks = q.get('blanks')
    if not isinstance(blanks, dict) or not blanks:
        issues.append(_err('bad_blanks', 'drag_drop expects non-empty blanks dict', qid))
        return issues
    for blank_id, blank_data in blanks.items():
        if not isinstance(blank_data, dict):
            issues.append(_err('bad_blank_entry', f'blank {blank_id!r} must be an object', qid))
            continue
        if not isinstance(blank_data.get('correct'), str):
            issues.append(_err('bad_blank_entry', f'blank {blank_id!r} missing string correct', qid))
    return issues


def _validate_recursive_trace(q: dict, qid: str | None) -> list[Issue]:
    issues: list[Issue] = []
    test_cases = q.get('test_cases')
    if not isinstance(test_cases, list) or not test_cases:
        issues.append(_err('bad_test_cases', 'recursive_trace requires non-empty test_cases list', qid))
        return issues
    for idx, tc in enumerate(test_cases):
        if not isinstance(tc, dict):
            issues.append(_err('bad_test_cases', f'test_cases[{idx}] must be an object', qid))
            continue
        if 'correct_answer' not in tc:
            issues.append(_err('bad_test_cases', f'test_cases[{idx}] missing correct_answer', qid))
    return issues


def _validate_code_writing(q: dict, qid: str | None) -> list[Issue]:
    issues: list[Issue] = []
    if not isinstance(q.get('code_template'), str):
        issues.append(_err('missing_field', "code_writing/code_completion missing 'code_template'", qid))
    test_cases = q.get('test_cases')
    if isinstance(test_cases, list):
        if not test_cases and 'expected_output' not in q:
            issues.append(_err('bad_test_cases', 'code_writing needs test_cases or top-level expected_output', qid))
    elif test_cases is None:
        if 'expected_output' not in q:
            issues.append(_err('bad_test_cases', 'code_writing needs test_cases or top-level expected_output', qid))
    else:
        issues.append(_err('bad_test_cases', 'code_writing test_cases must be a list', qid))
    return issues


def _validate_code_output(q: dict, qid: str | None) -> list[Issue]:
    if not isinstance(q.get('correct_answer'), str):
        return [_err('bad_correct_answer', 'code_output requires string correct_answer', qid)]
    return []


def _validate_bug_finding(q: dict, qid: str | None) -> list[Issue]:
    correct = q.get('correct_answer')
    if not isinstance(correct, list) or not all(isinstance(n, int) for n in correct):
        return [_err('bad_correct_answer', 'bug_finding correct_answer must be list[int] of line numbers', qid)]
    return []


def _validate_memory_tracing(q: dict, qid: str | None) -> list[Issue]:
    if not isinstance(q.get('correct_answer'), str):
        return [_err('bad_correct_answer', 'memory_tracing requires string correct_answer', qid)]
    return []


def _validate_struct_size(q: dict, qid: str | None) -> list[Issue]:
    correct = q.get('correct_answer')
    if isinstance(correct, int):
        return []
    if isinstance(correct, str):
        try:
            int(correct)
            return []
        except ValueError:
            pass
    return [_err('bad_correct_answer', 'struct_size correct_answer must be an int (or numeric string)', qid)]


_TYPE_VALIDATORS = {
    'multiple_choice': _validate_multiple_choice,
    'multiple_select': _validate_multiple_select,
    'fill_blanks': _validate_fill_blanks,
    'drag_drop': _validate_drag_drop,
    'recursive_trace': _validate_recursive_trace,
    'code_writing': _validate_code_writing,
    'code_completion': _validate_code_writing,
    'code_output': _validate_code_output,
    'bug_finding': _validate_bug_finding,
    'memory_tracing': _validate_memory_tracing,
    'struct_size': _validate_struct_size,
}


def validate_question(question: dict) -> list[Issue]:
    """Structural validation. Every returned issue is an ERROR."""
    if not isinstance(question, dict):
        return [_err('not_an_object', 'question entry must be a JSON object')]
    issues, qid = _validate_common(question)
    qtype = question.get('type')
    type_validator = _TYPE_VALIDATORS.get(qtype) if isinstance(qtype, str) else None
    if type_validator is not None:
        issues.extend(type_validator(question, qid))
    return issues


def lint_question(question: dict) -> list[Issue]:
    """Project-style lint hook. Currently a no-op — the previously-warned
    non-canonical shapes (``multiple_choice`` options dict, ``fill_blanks``
    legacy nested) are now structural ERRORs in :func:`validate_question`.

    This function is retained as a stable extension point for future
    style checks (e.g. id-namespacing per exam, language consistency).
    """
    del question
    return []


def validate_question_file(file_path: str) -> list[Issue]:
    """Validate a single question file. Catches:

    * JSON parse errors
    * Missing or non-list ``questions`` root
    * Per-question structural errors (see :func:`validate_question`)
    * Per-question lint warnings (see :func:`lint_question`)
    * Duplicate ``id`` within the same file
    """
    issues: list[Issue] = []
    try:
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        issues.append(Issue(LEVEL_ERROR, 'invalid_json', f'JSON parse error: {exc}', file_path=file_path))
        return issues
    except OSError as exc:
        issues.append(Issue(LEVEL_ERROR, 'io_error', f'cannot read file: {exc}', file_path=file_path))
        return issues

    if not isinstance(data, dict):
        issues.append(Issue(LEVEL_ERROR, 'bad_root', "file root must be a JSON object with 'questions'", file_path=file_path))
        return issues
    questions = data.get('questions')
    if not isinstance(questions, list):
        issues.append(Issue(LEVEL_ERROR, 'bad_root', "missing or non-list 'questions' field", file_path=file_path))
        return issues

    seen_ids: dict[str, int] = {}
    for index, q in enumerate(questions):
        for raw in validate_question(q) + lint_question(q):
            issues.append(Issue(raw.level, raw.code, raw.message,
                                question_id=raw.question_id, file_path=file_path))
        if isinstance(q, dict):
            qid = q.get('id')
            if isinstance(qid, str) and qid:
                if qid in seen_ids:
                    issues.append(Issue(LEVEL_ERROR, 'duplicate_id',
                                        f'duplicate id within file (also at index {seen_ids[qid]})',
                                        question_id=qid, file_path=file_path))
                else:
                    seen_ids[qid] = index
    return issues


def validate_questions_root(root: str, *, ignore_top_level: Iterable[str] = ()) -> list[Issue]:
    """Walk every ``*.json`` under ``root`` and aggregate issues.

    Also detects duplicate ``id``\u00a0values across files within the same exam
    directory (the directory containing the file).

    ``ignore_top_level`` is a set of directory names directly under ``root``
    that should be skipped — e.g. ``{"old_categories"}`` for archived data
    that is no longer wired up in ``exams.json``.
    """
    issues: list[Issue] = []
    ids_per_dir: dict[str, dict[str, str]] = {}
    ignore = {name.strip(os.sep) for name in ignore_top_level}

    if not os.path.isdir(root):
        return [Issue(LEVEL_ERROR, 'bad_root', f'questions root does not exist: {root}')]

    root_real = os.path.realpath(root)

    for dirpath, dirnames, filenames in os.walk(root):
        if os.path.realpath(dirpath) == root_real:
            dirnames[:] = [d for d in dirnames if d not in ignore]
        for name in sorted(filenames):
            if not name.endswith('.json'):
                continue
            file_path = os.path.join(dirpath, name)
            file_issues = validate_question_file(file_path)
            issues.extend(file_issues)

            try:
                with open(file_path, encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            if not isinstance(data, dict):
                continue
            for q in data.get('questions') or []:
                if not isinstance(q, dict):
                    continue
                qid = q.get('id')
                if not (isinstance(qid, str) and qid):
                    continue
                bucket = ids_per_dir.setdefault(dirpath, {})
                prior = bucket.get(qid)
                if prior is not None and prior != file_path:
                    issues.append(Issue(LEVEL_ERROR, 'duplicate_id_cross_file',
                                        f'duplicate id across files (also in {prior})',
                                        question_id=qid, file_path=file_path))
                else:
                    bucket[qid] = file_path
    return issues


def filter_errors(issues: Iterable[Issue]) -> list[Issue]:
    return [i for i in issues if i.level == LEVEL_ERROR]


def filter_warnings(issues: Iterable[Issue]) -> list[Issue]:
    return [i for i in issues if i.level == LEVEL_WARNING]
