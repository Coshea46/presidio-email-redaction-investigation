from presidio_analyzer import AnalyzerEngine
import os
import yaml
import csv
import json

analyzer = AnalyzerEngine()

YAML_FILE_PATH = './defining-pii-cats-for-experiment/english_presidio_entities.yaml'

BASE_INPUT_DIR = '/home/conor/Desktop/phishing-internship-2026/presidio-based-approach/presidio-email-redaction-investigation/spam-assassin-samples'
BASE_OUTPUT_DIR = '/home/conor/Desktop/phishing-internship-2026/presidio-based-approach/presidio-email-redaction-investigation/presidio-output/mime-header-experiment/no-formatting-assistance'
OUTPUT_CSV_PATH = os.path.join(BASE_OUTPUT_DIR,'presidio_found_span_details.csv')
OUTPUT_JSON_PATH = os.path.join(BASE_OUTPUT_DIR,'presidio_found_span_objects.json')
LABEL_STUDIO_JSON_PATH = os.path.join(BASE_OUTPUT_DIR, 'label_studio_tasks.json')


with open(YAML_FILE_PATH, 'r') as stream:
    YAML_AS_DICT = yaml.safe_load(stream)

TARGET_ENTITIES = YAML_AS_DICT['entities']['en']


flat_predictions = []     # mirrors the CSV, kept in memory for the flat JSON
label_studio_tasks = []   # one entry per email, for Label Studio import



with open(OUTPUT_CSV_PATH,mode='w',encoding='utf-8') as f:
    writer = csv.writer(f)

    
    # write header for output csv        
    csv_header = ['sample','email_id', 'start', 'end', 'entity_type', 'text', 'score']

    writer.writerow(csv_header)


    # Loop directly over dir names to preserve the parent directory context
    for dir_name in os.listdir(BASE_INPUT_DIR):
        input_dir = os.path.join(BASE_INPUT_DIR, dir_name, "extracted-mime-headers")
        
        # Skip if it's a file or the extracted-mime-headers dir doesn't exist
        if not os.path.isdir(input_dir):
            continue


        for header_file in os.listdir(input_dir):
            header_file_path = os.path.join(input_dir, header_file)
            
            email_id = os.path.splitext(header_file)[0]

            with open(header_file_path, mode='r', encoding='utf-8') as input_file:
                header_file_contents_string = input_file.read()

            # Find the PII locations using presidio
            no_assistance_analyzer_results = analyzer.analyze(text=header_file_contents_string, language="en", entities=TARGET_ENTITIES)


            label_studio_results = []

            for pii_index, result in enumerate(no_assistance_analyzer_results):
                
                span_text = header_file_contents_string[result.start:result.end]  # the text that presidio picked up as PII
                
                span_id = f"{email_id}_{pii_index}"

                # write each result to the output csv
                row_to_write = [
                    dir_name,
                    email_id,
                    result.start,
                    result.end,
                    result.entity_type,
                    span_text,
                    result.score
                ]

                writer.writerow(row_to_write)

                # now get in format needed for label studio jsons

                flat_predictions.append({
                    "email_id": email_id, "start": result.start, "end": result.end,
                    "entity_type": result.entity_type, "text": span_text, "score": result.score,
                })


                label_studio_results.append({
                    "id": span_id,
                    "from_name": "label", "to_name": "text", "type": "labels",
                    "value": {"start": result.start, "end": result.end, "text": span_text,
                              "labels": [result.entity_type], "score": result.score},
                })

            label_studio_tasks.append({
                "data": {"text": header_file_contents_string, "email_id": email_id},
                "predictions": [{"result": label_studio_results}],
            })


# Write both JSON files once, after the loop is completely finished
with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(flat_predictions, f, indent=2)

with open(LABEL_STUDIO_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(label_studio_tasks, f, indent=2)