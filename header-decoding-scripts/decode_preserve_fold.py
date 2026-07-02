import argparse
import csv
import re
from email.header import decode_header
from pathlib import Path

# Matches the OPENING structure of an RFC 2047 encoded-word: =?charset?B/Q?
ENCODED_WORD_OPEN_RE = re.compile(r"=\?[^?\s]+\?[bBqQ]\?")

# RFC 5322 recommends physical header lines stay at or under 78 characters.
MAX_FOLD_LENGTH = 78


def unfold_header(raw_text: str) -> list:
    """
    Splits raw file content into logical (unfolded) header lines per RFC 5322.
    A line that starts with whitespace is a continuation of the previous line.
    """
    logical_lines = []
    current = None

    # Python's splitlines() over-splits on exotic Unicode characters (\v, \f, etc). 
    # This regex strictly limits splitting to standard RFC line endings 
    # (\r\n, \n, or \r), preserving exact byte payloads.
    lines = [m.group(0) for m in re.finditer(r'[^\r\n]*(\r\n|\n|\r)?', raw_text) if m.group(0)]

    for line in lines:
        is_continuation = (
            current is not None
            and line
            and line[0] in (" ", "\t")
        )
        if is_continuation:
            current = current.rstrip("\r\n") + line
        else:
            if current is not None:
                logical_lines.append(current)
            current = line

    if current is not None:
        logical_lines.append(current)

    return logical_lines


def fold_header(decoded_line: str) -> str:
    """
    Re-folds a decoded logical header line back into RFC 5322-compliant
    physical lines, preserving original internal whitespace and preventing
    whitespace duplication upon future unfolding.
    """
    if decoded_line.endswith("\r\n"):
        ending = "\r\n"
        body = decoded_line[:-2]
    elif decoded_line.endswith("\n"):
        ending = "\n"
        body = decoded_line[:-1]
    elif decoded_line.endswith("\r"):
        ending = "\r"
        body = decoded_line[:-1]
    else:
        ending = ""
        body = decoded_line

    if len(body) <= MAX_FOLD_LENGTH:
        return body + ending

    # Split while keeping the whitespace as separate tokens in the list
    tokens = [t for t in re.split(r'(\s+)', body) if t]
    if not tokens:
        return body + ending

    physical_lines = []
    current_line = ""

    for token in tokens:
        if not current_line:
            current_line = token
            continue

        if len(current_line) + len(token) <= MAX_FOLD_LENGTH:
            current_line += token
        elif token.isspace():
            # If a whitespace token pushes us over the limit, we break 
            # BEFORE it, letting it act as the leading fold space.
            physical_lines.append(current_line)
            current_line = token
        else:
            # A word pushed us over. 
            # Steal the trailing whitespace from current_line to use as the 
            # mandatory folding prefix for the next line, preventing space duplication.
            match = re.search(r'(\s+)$', current_line)
            if match:
                trailing_ws = match.group(1)
                stripped_line = current_line[:-len(trailing_ws)]
                if stripped_line:
                    physical_lines.append(stripped_line)
                    current_line = trailing_ws + token
                else:
                    # current_line was entirely whitespace; just append to it
                    current_line += token
            else:
                # Fallback if there was no trailing whitespace
                physical_lines.append(current_line)
                current_line = " " + token

    physical_lines.append(current_line)

    line_sep = ending if ending else "\n"
    return line_sep.join(physical_lines) + ending


def decode_rfc2047_string(text: str) -> tuple:
    try:
        fragments = decode_header(text)
    except Exception:
        return text, False, True

    decoded_text = ""
    contained_encoding = False
    bogus_charset = False
    truncated_encoded_word = False

    for fragment, charset in fragments:
        if charset is not None:
            contained_encoding = True

        if isinstance(fragment, bytes):
            use_charset = charset if charset else "utf-8"
            try:
                decoded_text += fragment.decode(use_charset)
            except (LookupError, UnicodeDecodeError):
                decoded_text += fragment.decode("utf-8", errors="replace")
                bogus_charset = True
        else:
            decoded_text += fragment
            if ENCODED_WORD_OPEN_RE.search(fragment):
                truncated_encoded_word = True

    # Account for standard and lone \r in the restoration logic
    if text.endswith(("\r\n", "\n", "\r")) and not decoded_text.endswith(("\r\n", "\n", "\r")):
        if text.endswith("\r\n"):
            decoded_text += "\r\n"
        elif text.endswith("\n"):
            decoded_text += "\n"
        else:
            decoded_text += "\r"

    malformed = truncated_encoded_word or bogus_charset

    return decoded_text, contained_encoding, malformed


def process_directory(input_dir: str, output_dir: str, csv_path: str) -> None:
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.is_dir():
        print(f"Error: '{input_dir}' is not a valid directory.")
        return

    if input_path.resolve() == output_path.resolve():
        print("Error: input_dir and output_dir must be different directories.")
        return

    output_path.mkdir(parents=True, exist_ok=True)
    csv_data = []

    for file_path in sorted(input_path.iterdir()):
        if not file_path.is_file():
            continue

        try:
            with open(file_path, "r", encoding="utf-8", errors="surrogateescape", newline="") as f:
                raw_text = f.read()

            logical_lines = unfold_header(raw_text)
            decoded_lines = []
            file_contained_encoding = False
            file_had_malformed = False

            for line in logical_lines:
                decoded_line, line_had_encoding, line_malformed = decode_rfc2047_string(line)
                decoded_lines.append(fold_header(decoded_line))
                
                if line_had_encoding:
                    file_contained_encoding = True
                if line_malformed:
                    file_had_malformed = True

            out_file = output_path / file_path.name
            with open(out_file, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
                f.writelines(decoded_lines)

            if file_had_malformed:
                status = "malformed"
            elif file_contained_encoding:
                status = "true"
            else:
                status = "false"

            csv_data.append({
                "email_id": file_path.name,
                "contained_encoding": status,
                "error": "",
            })
            print(f"Processed: {file_path.name} | Encoding status: {status}")

        except Exception as e:
            csv_data.append({
                "email_id": file_path.name,
                "contained_encoding": "error",
                "error": str(e),
            })
            print(f"Failed to process {file_path.name}: {e}")

    if csv_data:
        try:
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["email_id", "contained_encoding", "error"])
                writer.writeheader()
                writer.writerows(csv_data)
            print(f"\nSuccess! CSV report saved to: {csv_path}")
        except Exception as e:
            print(f"\nFailed to write CSV: {e}")
    else:
        print("\nNo files were processed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode email headers and output a CSV report.")
    parser.add_argument("input_dir", help="Directory containing raw email headers.")
    parser.add_argument("output_dir", help="Directory to save decoded headers.")
    parser.add_argument("--csv", default="encoding_report.csv", help="Path for output CSV.")
    
    args = parser.parse_args()
    process_directory(args.input_dir, args.output_dir, args.csv)