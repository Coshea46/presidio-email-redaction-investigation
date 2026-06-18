from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import os
from email import message_from_string

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
TARGET_ENTITIES = ["PERSON", "PHONE_NUMBER", "CREDIT_CARD", "EMAIL_ADDRESS"]


BASE_INPUT_DIR = '/home/conor/Desktop/phishing-internship-2026/presidio-based-approach/presidio-email-redaction-investigation/spam-assassin-samples'
NO_ASSISTANCE_BASE_OUTPUT_DIR = '/home/conor/Desktop/phishing-internship-2026/presidio-based-approach/presidio-email-redaction-investigation/presidio-output/mime-header-experiment/no-formatting-assistance'
WITH_ASSISTANCE_BASE_OUTPUT_DIR = '/home/conor/Desktop/phishing-internship-2026/presidio-based-approach/presidio-email-redaction-investigation/presidio-output/mime-header-experiment/with-formatting-assistance'


# Loop directly over dir names to preserve the parent directory context
for dir_name in os.listdir(BASE_INPUT_DIR):
    input_dir = os.path.join(BASE_INPUT_DIR, dir_name, "extracted-mime-headers")
    
    # Skip if it's a file or the extracted-mime-headers dir doesn't exist
    if not os.path.isdir(input_dir):
        continue

    # Setup the output directories for this specific parent folder
    no_assist_out_dir = os.path.join(NO_ASSISTANCE_BASE_OUTPUT_DIR, dir_name + "-output")
    with_assist_out_dir = os.path.join(WITH_ASSISTANCE_BASE_OUTPUT_DIR, dir_name + "-output")
    
    # Ensure output directories exist before writing
    os.makedirs(no_assist_out_dir, exist_ok=True)
    os.makedirs(with_assist_out_dir, exist_ok=True)

    for header_file in os.listdir(input_dir):
        header_file_path = os.path.join(input_dir, header_file)

        no_formatting_assistance_output_file_path = os.path.join(no_assist_out_dir, "NO-ASSISTANCE-REDACTED-" + header_file)
        with_formatting_assistance_output_file_path = os.path.join(with_assist_out_dir, "WITH-ASSISTANCE-REDACTED-" + header_file)
        
        # ---------------------------------------------------------
        # EXPERIMENT 1: Try without assistance first
        # ---------------------------------------------------------
        with open(header_file_path, mode='r', encoding='utf-8') as input_file:
            header_file_contents_string = input_file.read()

        # Find the PII locations using presidio
        no_assistance_analyzer_results = analyzer.analyze(text=header_file_contents_string, language="en", entities=TARGET_ENTITIES)

        # Have presidio redact with placeholders
        no_assistance_anonymized_result = anonymizer.anonymize(
            text=header_file_contents_string,
            analyzer_results=no_assistance_analyzer_results
        )

        # Output to file
        with open(no_formatting_assistance_output_file_path, mode='w', encoding='utf-8') as no_assistance_output_file:
            no_assistance_output_file.write(no_assistance_anonymized_result.text)

        # ---------------------------------------------------------
        # EXPERIMENT 2: Now try with parsing assistance
        # ---------------------------------------------------------
        header_text_as_dict = message_from_string(header_file_contents_string)
    
        # Using a list of tuples instead of a dict to preserve duplicate headers like "Received"
        redacted_headers = []

        # .items() on an email.Message object handles duplicates natively
        for key, value in header_text_as_dict.items():
            
            # Catch edge cases where value might be None
            safe_value = str(value) if value is not None else ""

            value_analyzer_result = analyzer.analyze(text=safe_value, language="en", entities=TARGET_ENTITIES)

            # Fixed copy-paste errors: Passing the specific value and specific results
            anonymized_value = anonymizer.anonymize(
                text=safe_value,
                analyzer_results=value_analyzer_result
            )

            # Extract the string using .text
            redacted_headers.append((key, anonymized_value.text))

        # Write redacted data to output file
        with open(with_formatting_assistance_output_file_path, mode='w', encoding='utf-8') as with_assistance_output_file:
            for key, value in redacted_headers:
                with_assistance_output_file.write(f"{key}: {value}\n")