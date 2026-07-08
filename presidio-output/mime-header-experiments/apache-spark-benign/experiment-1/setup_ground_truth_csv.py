import json
import csv
from collections import Counter

def json_to_csv(input_filepath, output_filepath):
    with open(input_filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # --- Diagnostic: check what origin values exist in this file ---
    origins = Counter(
        ann.get('origin', 'NONE')
        for record in data
        for block in record.get('annotations', [])
        for ann in block.get('result', [])
    )
    print(f"Origin counts: {origins}")

    # Check for duplicate annotation IDs within ALL ground truth
    all_ids = [
        ann.get('id')
        for record in data
        for block in record.get('annotations', [])
        for ann in block.get('result', [])
    ]
    dupes = [item for item, count in Counter(all_ids).items() if count > 1]
    print(f"Total annotations: {len(all_ids)}, unique: {len(set(all_ids))}, duplicate IDs: {dupes}")
    
    # -----------------------------------------------------------

    # Add 'origin' column to help track source if needed later
    headers = ['sample', 'email_id', 'annotation_id', 'start', 'end', 'entity_type', 'text', 'origin']

    with open(output_filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for record in data:
            email_id = record.get('data', {}).get('email_id', '')

            for annotation_block in record.get('annotations', []):
                for annotation in annotation_block.get('result', []):
                    # KEEP ALL annotations - they're all valid ground truth
                    # Remove the filter entirely
                    
                    val = annotation.get('value', {})
                    sample = "apache_spark"
                    annotation_id = annotation.get('id', '')
                    start = val.get('start', '')
                    end = val.get('end', '')
                    text = val.get('text', '')
                    labels = val.get('labels', [])
                    entity_type = labels[0] if labels else ''
                    origin = annotation.get('origin', '')

                    writer.writerow([sample, email_id, annotation_id, start, end, entity_type, text, origin])

    print(f"Successfully converted {input_filepath} to {output_filepath}")
    print(f"Total annotations exported: {len(all_ids)}")

if __name__ == '__main__':
    json_to_csv('./SAMPLE_OF_20_ground_truth_spans.json', 'SAMPLE_OF_20_ground_truths.csv')