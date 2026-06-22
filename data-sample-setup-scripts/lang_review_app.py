import streamlit as st
import os
import email
import csv
from email.policy import default

# --- Configuration ---
OUTPUT_CSV = "subject_lang_human_review.csv"

# Initialize CSV if it doesn't exist to ensure headers are present
if not os.path.exists(OUTPUT_CSV):
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["sample", "email_id", "keep_or_delete"])

# --- Callbacks ---
def record_decision(sample_name, email_id, decision):
    """Saves the decision to the CSV and advances the index."""
    # Strip any literal quotation marks the user might have typed into the input
    clean_sample = sample_name.strip("\"'")
    
    with open(OUTPUT_CSV, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([clean_sample, email_id, decision])
    
    st.session_state.current_idx += 1

# --- Main App ---
st.title("📧 Email Subject Reviewer")

# Initialize session state variables
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0
if 'files' not in st.session_state:
    st.session_state.files = []
if 'last_dir' not in st.session_state:
    st.session_state.last_dir = ""

# Inputs for sample name and directory path
sample_name = st.text_input("Enter the sample name:")
directory = st.text_input("Enter the absolute or relative path to your emails directory:")

if directory and os.path.isdir(directory):
    # If a new directory is entered, load the files and reset progress
    if st.session_state.last_dir != directory:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        st.session_state.files = sorted(files)
        st.session_state.current_idx = 0
        st.session_state.last_dir = directory

    total_files = len(st.session_state.files)

    if total_files == 0:
        st.warning("No files found in the specified directory.")
    elif not sample_name:
        st.info("Please enter a sample name above to begin reviewing.")
    elif st.session_state.current_idx < total_files:
        current_file = st.session_state.files[st.session_state.current_idx]
        file_path = os.path.join(directory, current_file)

        # Parse the email file
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                msg = email.message_from_file(f, policy=default)
                subject = msg.get('subject', '(No Subject Found)')
        except Exception as e:
            subject = f"(Error reading file: {e})"

        # UI: Progress and Current Subject
        st.write(f"**Reviewing {st.session_state.current_idx + 1} of {total_files}**")
        st.caption(f"File: `{current_file}` | Sample: `{sample_name}`")
        
        st.markdown("### Subject Line:")
        st.info(subject)

        # UI: Action Buttons
        col1, col2 = st.columns(2)
        with col1:
            st.button("Keep", on_click=record_decision, args=(sample_name, current_file, "keep"), use_container_width=True, type="primary")
        with col2:
            st.button("Delete", on_click=record_decision, args=(sample_name, current_file, "delete"), use_container_width=True)
    else:
        st.success("🎉 You've reviewed all the emails in this directory!")
        st.write(f"Results have been saved to `{OUTPUT_CSV}` in your working directory.")
        
elif directory:
    st.error("Directory not found. Please enter a valid path.")