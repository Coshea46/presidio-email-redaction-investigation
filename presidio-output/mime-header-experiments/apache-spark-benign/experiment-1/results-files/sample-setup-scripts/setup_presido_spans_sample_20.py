import json

def filter_flat_json_by_ids(txt_filepath, input_json_filepath, output_json_filepath):
    # 1. Read and clean the target IDs from the text file
    with open(txt_filepath, 'r', encoding='utf-8') as f:
        # .strip() handles the trailing spaces in your text file
        target_ids = {line.strip() for line in f if line.strip()}
        
    print(f"Loaded {len(target_ids)} unique target IDs from {txt_filepath}.")

    # 2. Load the original JSON file
    with open(input_json_filepath, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    print(f"Loaded {len(original_data)} entries from {input_json_filepath}.")

    # 3. Filter the entries
    filtered_data = []
    for entry in original_data:
        # Extract the email_id directly from the top level of the object
        email_id = entry.get("email_id")
        
        if email_id in target_ids:
            filtered_data.append(entry)

    # 4. Write the filtered result to a new JSON file
    with open(output_json_filepath, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=2)

    print(f"Successfully saved {len(filtered_data)} matching entries to {output_json_filepath}.")

# --- Execution ---
if __name__ == "__main__":
    # Update these file names to match the files on your system
    TXT_FILE = "sub_sample_of_20_ids.txt"
    INPUT_JSON = "presidio_found_span_objects.json"
    OUTPUT_JSON = "SAMPLE_OF_20_presidio_found_span_objects.json"
    
    filter_flat_json_by_ids(TXT_FILE, INPUT_JSON, OUTPUT_JSON)