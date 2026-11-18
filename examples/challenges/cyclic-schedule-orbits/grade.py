"""Check numerical claims; missing/invalid output is not a demonstrated math error."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def extract_object(text):
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char == '{':
            try:
                value, _ = decoder.raw_decode(text[index:])
            except ValueError:
                continue
            if isinstance(value, dict) and 'dihedral_orbits' in value:
                return value
    raise ValueError('No result JSON; review prose manually before assigning an outcome')


def grade(answer, reference):
    mistakes, missing = [], []
    for field in ('rooted_gap_sequences', 'labelled_binary_schedules', 'dihedral_orbits'):
        if field not in answer:
            missing.append(field)
        elif answer[field] != reference[field]:
            mistakes.append({'field': field, 'expected': reference[field], 'actual': answer[field]})
    profiles = {(x['r'], x['f']): x['orbits'] for x in answer.get('profiles', [])}
    for item in reference['profiles']:
        key = item['r'], item['f']
        if key not in profiles:
            missing.append('profiles' + str(key))
        elif profiles[key] != item['orbits']:
            mistakes.append({'field': 'profiles' + str(key), 'expected': item['orbits'], 'actual': profiles[key]})
    return {'verdict': 'flawed' if mistakes else 'incomplete' if missing else 'correct',
            'model_break_candidate': bool(mistakes), 'semantic_mismatches': mistakes,
            'missing_fields': missing}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('answer', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        report = grade(extract_object(args.answer.read_text()), json.loads((ROOT / 'reference-output.json').read_text()))
    except (ValueError, KeyError, TypeError) as exc:
        report = {'verdict': 'ungraded', 'model_break_candidate': False, 'reason': str(exc)}
    result = json.dumps(report, indent=2) + '\n'
    if args.output:
        args.output.write_text(result)
    print(result, end='')


if __name__ == '__main__':
    main()
