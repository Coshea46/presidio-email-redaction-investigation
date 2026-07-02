import argparse
import csv
import re
import shutil
from pathlib import Path

# Byte-level regex to avoid Unicode decoding crashes.
# Looks for the strict opening signature: =?charset?B/Q?
ENCODED_WORD_RE = re.compile(b"=\\?[^?\\s]+\\?[bBqQ]\\?")

def sort_headers(input_dir: str, output_dir: str, csv_path: str) -> None:
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.is_dir():
        print(f"Error: '{input_dir}' is not a valid directory.")
        return

    if input_path.resolve() == output_path.resolve():
        print("Error: input_dir and output_dir must be different directories.")
        return

    # Set up the routing directories
    encoded_dir = output_path / "encoded"
    no_encoding_dir = output_path / "no_encoding"
    
    encoded_dir.mkdir(parents=True, exist_ok=True)
    no_encoding_dir.mkdir(parents=True, exist_ok=True)

    csv_data = []
    encoded_count = 0
    unencoded_count = 0

    for file_path in sorted(input_path.iterdir()):
        if not file_path.is_file():
            continue

        try:
            # Read as raw bytes so we don't accidentally modify or crash on bad text
            with open(file_path, "rb") as f:
                content = f.read()

            # Route the file based on the regex search
            if ENCODED_WORD_RE.search(content):
                shutil.copy2(file_path, encoded_dir / file_path.name)
                contained_encoding = True
                encoded_count += 1
            else:
                shutil.copy2(file_path, no_encoding_dir / file_path.name)
                contained_encoding = False
                unencoded_count += 1

            csv_data.append({
                "email_id": file_path.name,
                "contained_encoding": contained_encoding
            })
                
        except Exception as e:
            print(f"Failed to process {file_path.name}: {e}")

    # Write the CSV report
    if csv_data:
        try:
            csv_file_path = Path(csv_path)
            csv_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["email_id", "contained_encoding"])
                writer.writeheader()
                writer.writerows(csv_data)
                
        except Exception as e:
            print(f"\nFailed to write CSV: {e}")

    # Print the final counts
    print("\n--- Routing Complete ---")
    print(f"Total files processed:       {encoded_count + unencoded_count}")
    print(f"Files routed to /encoded:    {encoded_count}")
    print(f"Files routed to /no_encoding: {unencoded_count}")
    print(f"CSV report saved to:         {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort raw email headers based on RFC 2047 encoding presence and generate a CSV report.")
    parser.add_argument("input_dir", help="Directory containing raw email headers.")
    parser.add_argument("output_dir", help="Base directory to save the sorted files.")
    parser.add_argument("--csv", default="encoding_report.csv", help="Path for output CSV.")
    
    args = parser.parse_args()
    sort_headers(args.input_dir, args.output_dir, args.csv)