"""Compare substantive model trace fields with the executed reference.

Formatting/parse failures are ungraded, not evidence of a factual model break.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = ('parent', 'child', 'audit', 'in_transaction', 'foreign_keys', 'changes', 'total_delta', 'fk_violations')


def extract_object(text):
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != '{':
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except ValueError:
            continue
        if isinstance(value, dict) and isinstance(value.get('snapshots'), list):
            return value
    raise ValueError('No JSON trace object found; inspect the answer manually instead of claiming a factual break')


def normalize(field, value):
    if field in ('parent', 'child', 'fk_violations', 'audit') and isinstance(value, list):
        try:
            return sorted(value)
        except TypeError:
            return value
    return value


def grade(answer, reference):
    mistakes, incomplete = [], []
    observed = {row.get('checkpoint'): row for row in answer['snapshots'] if isinstance(row, dict)}
    for expected in reference['snapshots']:
        checkpoint = expected['checkpoint']
        actual = observed.get(checkpoint)
        if actual is None:
            incomplete.append(checkpoint)
            continue
        for field in FIELDS:
            if field not in actual:
                incomplete.append(checkpoint + '.' + field)
                continue
            if normalize(field, actual[field]) != normalize(field, expected[field]):
                mistakes.append({'checkpoint': checkpoint, 'field': field,
                                 'expected': expected[field], 'actual': actual[field]})
    if 'errors' in answer:
        if answer['errors'] != reference['errors']:
            mistakes.append({'field': 'errors', 'expected': reference['errors'], 'actual': answer['errors']})
    else:
        incomplete.append('errors')
    if 'base_total_changes' in answer and answer['base_total_changes'] != reference['base_total_changes']:
        mistakes.append({'field': 'base_total_changes', 'expected': reference['base_total_changes'], 'actual': answer['base_total_changes']})
    elif 'base_total_changes' not in answer:
        incomplete.append('base_total_changes')
    return {'verdict': 'flawed' if mistakes else 'incomplete' if incomplete else 'correct',
            'model_break_candidate': bool(mistakes),
            'semantic_mismatches': mistakes, 'missing_fields': incomplete,
            'review_required': 'Confirm mismatches against the actual answer, pinned runtime, and official rules; do not treat formatting alone as a factual error.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('answer', type=Path)
    parser.add_argument('--reference', type=Path, default=ROOT / 'reference-output.json')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        report = grade(extract_object(args.answer.read_text()), json.loads(args.reference.read_text()))
    except ValueError as exc:
        report = {'verdict': 'ungraded', 'model_break_candidate': False, 'reason': str(exc)}
    text = json.dumps(report, indent=2) + '\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
