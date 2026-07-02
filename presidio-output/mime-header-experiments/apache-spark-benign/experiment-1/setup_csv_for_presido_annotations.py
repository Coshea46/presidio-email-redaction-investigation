import json
import csv

def json_to_csv(input_filepath, output_filepath):
    # Load the JSON data
    with open(input_filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Define the CSV headers
    headers = ['sample', 'email_id', 'annotation_id', 'start', 'end', 'entity_type', 'text', 'score']
    
    # Open the output CSV file
    with open(output_filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        # Loop through each document record in the JSON array
        for record in data:
            # Safely get the email_id from the "data" dictionary
            email_id = record.get('data', {}).get('email_id', '')
            
            # Loop through the "predictions" array
            for prediction in record.get('predictions', []):
                
                # Loop through the actual annotations inside "result"
                for annotation in prediction.get('result', []):
                    val = annotation.get('value', {})
                    
                    sample = "apache_spark"
                    annotation_id = annotation.get('id', '')
                    
                    start = val.get('start', '')
                    end = val.get('end', '')
                    text = val.get('text', '')
                    score = val.get('score', '')
                    
                    # Extract the first label as entity_type if it exists
                    labels = val.get('labels', [])
                    entity_type = labels[0] if labels else ''
                    
                    # Write the row to the CSV
                    writer.writerow([
                        sample, 
                        email_id, 
                        annotation_id, 
                        start, 
                        end, 
                        entity_type, 
                        text, 
                        score
                    ])

    print(f"Successfully converted {input_filepath} to {output_filepath}")

# Execute the conversion (make sure your input file is named 'data.json')
json_to_csv('./SAMPLE_OF_20_label_studio_tasks.json', 'SAMPLE_OF_20_presidio_found_spans.csv')