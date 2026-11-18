"""Compare complete migration states; parsing/omissions alone are not a break."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = ('parent', 'child', 'fk_target', 'violations', 'foreign_keys', 'defer_foreign_keys', 'in_transaction')


def extract_object(text):
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != '{':
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except ValueError:
            continue
        if isinstance(value, dict) and isinstance(value.get('cases'), dict):
            return value
    raise ValueError('No JSON cases object; manually assess the answer rather than claim a factual failure')


def grade(answer, reference):
    mistakes, missing = [], []
    for name, expected in reference['cases'].items():
        actual = answer['cases'].get(name)
        if not isinstance(actual, dict):
            missing.append(name)
            continue
        if 'commit' not in actual:
            missing.append(name + '.commit')
        elif actual['commit'] != expected['commit']:
            mistakes.append({'case': name, 'field': 'commit', 'expected': expected['commit'], 'actual': actual['commit']})
        for stage in ('before_commit', 'after_commit'):
            found = actual.get(stage)
            if not isinstance(found, dict):
                missing.append(name + '.' + stage)
                continue
            for field in FIELDS:
                if field not in found:
                    missing.append(name + '.' + stage + '.' + field)
                    continue
                want, got = expected[stage][field], found[field]
                if isinstance(want, list) and isinstance(got, list):
                    want, got = sorted(want), sorted(got)
                if want != got:
                    mistakes.append({'case': name, 'stage': stage, 'field': field,
                                     'expected': expected[stage][field], 'actual': found[field]})
    return {'verdict': 'flawed' if mistakes else 'incomplete' if missing else 'correct',
            'model_break_candidate': bool(mistakes), 'semantic_mismatches': mistakes,
            'missing_fields': missing, 'review_required': 'Review the actual response and pinned-runtime evidence; syntax or schema differences alone do not establish a factual break.'}


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
