import json
import csv

def json_to_csv(input_filepath, output_filepath):
    # Load the JSON data
    with open(input_filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Define the CSV headers (without the score column)
    headers = ['sample', 'email_id', 'annotation_id', 'start', 'end', 'entity_type', 'text']
    
    # Open the output CSV file
    with open(output_filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        # Loop through each document record in the JSON array
        for record in data:
            # Safely get the email_id from the "data" dictionary
            email_id = record.get('data', {}).get('email_id', '')
            
            # For ground truths, annotations are under the "annotations" key, not "predictions"
            for annotation_block in record.get('annotations', []):
                
                # Loop through the actual annotations inside "result"
                for annotation in annotation_block.get('result', []):
                    val = annotation.get('value', {})
                    
                    sample = "apache_spark"
                    annotation_id = annotation.get('id', '')
                    
                    start = val.get('start', '')
                    end = val.get('end', '')
                    text = val.get('text', '')
                    
                    # Extract the first label as entity_type if it exists
                    labels = val.get('labels', [])
                    entity_type = labels[0] if labels else ''
                    
                    # Write the row to the CSV (excluding score)
                    writer.writerow([
                        sample, 
                        email_id, 
                        annotation_id, 
                        start, 
                        end, 
                        entity_type, 
                        text
                    ])

    print(f"Successfully converted {input_filepath} to {output_filepath}")

if __name__ == '__main__':
    # Execute the conversion
    json_to_csv('./SAMPLE_OF_20_ground_truth_spans.json', 'SAMPLE_OF_20_ground_truths.csv')