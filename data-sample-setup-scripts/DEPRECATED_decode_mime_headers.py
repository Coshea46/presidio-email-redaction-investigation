import argparse
import csv
from email.header import decode_header
from pathlib import Path

def decode_rfc2047_string(text: str) -> tuple:
    """
    Decodes RFC 2047 encoded words in a string.
    Returns a tuple of (decoded_text, contained_encoding_flag).
    """
    try:
        fragments = decode_header(text)
        decoded_text = ""
        contained_encoding = False
        
        for fragment, charset in fragments:
            # If charset is not None, it means the fragment was encoded (Base64/Quoted-Printable)
            if charset is not None:
                contained_encoding = True
                
            if isinstance(fragment, bytes):
                charset = charset if charset else 'utf-8'
                try:
                    decoded_text += fragment.decode(charset, errors='replace')
                except LookupError:
                    decoded_text += fragment.decode('utf-8', errors='replace')
            else:
                decoded_text += fragment
                
        return decoded_text, contained_encoding
    except Exception:
        # If structural decoding fails, return untouched text and False
        return text, False

def process_directory(input_dir: str, output_dir: str, csv_path: str) -> None:
    """Iterates through directory, decodes files, and writes a CSV report."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.is_dir():
        print(f"Error: '{input_dir}' is not a valid directory.")
        return

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    csv_data = []
    
    for file_path in input_path.iterdir():
        if file_path.is_file():
            try:
                # surrogateescape ensures we handle weird binary artifacts smoothly
                with open(file_path, 'r', encoding='utf-8', errors='surrogateescape') as f:
                    lines = f.readlines()
                
                decoded_lines = []
                file_contained_encoding = False
                
                # Decode line-by-line and track if ANY line contained encoding
                for line in lines:
                    decoded_line, line_had_encoding = decode_rfc2047_string(line)
                    decoded_lines.append(decoded_line)
                    if line_had_encoding:
                        file_contained_encoding = True
                
                # Write decoded file
                out_file = output_path / file_path.name
                with open(out_file, 'w', encoding='utf-8') as f:
                    f.writelines(decoded_lines)
                
                # Append result for CSV
                csv_data.append({
                    "email_id": file_path.name,
                    "contained_encoding": str(file_contained_encoding).lower()
                })
                    
                print(f"Processed: {file_path.name} | Encoded: {file_contained_encoding}")
                
            except Exception as e:
                print(f"Failed to process {file_path.name}: {e}")

    # Write the CSV report
    if csv_data:
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["email_id", "contained_encoding"])
                writer.writeheader()
                writer.writerows(csv_data)
            print(f"\nSuccess! CSV report saved to: {csv_path}")
        except Exception as e:
            print(f"\nFailed to write CSV: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode email headers and output a CSV report.")
    parser.add_argument("input_dir", help="Directory containing the raw email header files.")
    parser.add_argument("output_dir", help="Directory to save the decoded header files.")
    parser.add_argument("--csv", default="encoding_report.csv", help="Path for the output CSV file (default: encoding_report.csv)")
    
    args = parser.parse_args()
    process_directory(args.input_dir, args.output_dir, args.csv)