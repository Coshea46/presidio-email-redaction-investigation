import json
import csv
import argparse

def main():
    # 1. Set up the argument parser for CLI inputs
    parser = argparse.ArgumentParser(description="Parse nested JSON annotations into a flat CSV format.")
    parser.add_argument("input_json", help="Path to the input JSON file (e.g., input.json)")
    parser.add_argument("output_csv", help="Path for the output CSV file (e.g., output.csv)")
    
    args = parser.parse_args()

    # 2. Load the JSON data safely
    try:
        with open(args.input_json, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{args.input_json}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{args.input_json}' does not contain valid JSON.")
        return

    # 3. Prepare a list to hold the extracted rows
    extracted_rows = []

    # 4. Iterate through the nested JSON structure
    for item in data:
        #sample_id = item.get("id")
        
        for annotation in item.get("annotations", []):
            for res in annotation.get("result", []):
                val = res.get("value", {})
                
                # Extract the label (entity_type). Grab the first item if it exists.
                labels = val.get("labels", [])
                entity_type = labels[0] if labels else ""
                
                extracted_rows.append({
                    "sample": "apache_spark",
                    "email_id": res.get("id", ""),
                    "start": val.get("start", ""),
                    "end": val.get("end", ""),
                    "entity_type": entity_type,
                    "text": val.get("text", ""), 
                })

    # 5. Define the CSV columns in the exact order requested
    csv_columns = ["sample", "email_id", "start", "end", "entity_type", "text"]

    # 6. Write the extracted data to the CSV file
    try:
        with open(args.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            writer.writerows(extracted_rows)
            
        print(f"Success! {len(extracted_rows)} rows have been written to {args.output_csv}")
    except Exception as e:
        print(f"Error writing to CSV: {e}")

if __name__ == "__main__":
    main()