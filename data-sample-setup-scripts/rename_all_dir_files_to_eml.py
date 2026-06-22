import sys
from pathlib import Path

def append_eml_extensions(directory_path):
    target_dir = Path(directory_path)
    
    if not target_dir.is_dir():
        print(f"Error: '{directory_path}' is not a valid directory.")
        return

    count = 0
    
    for item in target_dir.iterdir():
        if item.is_file():
            # Check if it already ends with .eml to avoid double-appending
            if not item.name.lower().endswith('.eml'):
                # Safely append .eml to the exact existing filename
                new_path = item.with_name(f"{item.name}.eml")
                item.rename(new_path)
                count += 1
                print(f"Renamed: {item.name} -> {new_path.name}")

    print(f"\nDone! Successfully appended .eml to {count} files in '{target_dir}'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 rename_all_dir_files_to_eml.py /full/path/to/directory")
    else:
        append_eml_extensions(sys.argv[1])