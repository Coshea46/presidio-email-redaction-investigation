import os
import email
from email import policy
import fasttext
import shutil
import sys


# expects full directory path
def find_likely_english_samples(input_dir_path, num_samples_desired):

    model = fasttext.load_model('models/lid.176.ftz')

    # ensure we only grab files
    all_file_paths_in_dir = [
        os.path.join(input_dir_path,eml_file) for eml_file in os.listdir(input_dir_path)
        if os.path.isfile(os.path.join(input_dir_path, eml_file))
    ]


    likely_english_list = []

    for eml_file in all_file_paths_in_dir:

        # read in binary to avoid unicode errors
        with open(eml_file,mode='rb') as input_file:
            input_file_contents_bytes = input_file.read()

        # parse from bytes
        eml_as_dict = email.message_from_bytes(input_file_contents_bytes, policy=policy.default)

        subject = eml_as_dict['Subject']
        
        # handle missing subjects
        if not subject:
            continue

        # remove newlines so fasttext doesnt crash
        subject = str(subject).replace('\n', ' ').replace('\r', '')

        # detect language
        labels, probabilities = model.predict(subject, k=1) # k=1 means return top 1 result

        if probabilities[0] >= 0.7  and labels[0] == "__label__en":
            likely_english_list.append(eml_file)

        if len(likely_english_list) >= num_samples_desired:
            break


    return likely_english_list


def copy_files_to_target_dir(english_emails, target_dir_path):
    
    # ensure target dir exists
    os.makedirs(target_dir_path, exist_ok=True)

    for eng_email in english_emails:
        # extract just the file name
        file_name = os.path.basename(eng_email)
        shutil.copy2(eng_email,os.path.join(target_dir_path,file_name))

    
def main(args):
    
    # check for correct args
    if len(args) < 2:
        print("Usage: python script.py <input_directory> <target_directory>")
        sys.exit(1)
        
    input_dir_path = args[0]
    target_dir_path = args[1]

    NUM_SAMPLES_DESIRED = 110

    candidate_emails = find_likely_english_samples(input_dir_path,NUM_SAMPLES_DESIRED)

    copy_files_to_target_dir(candidate_emails,target_dir_path)


if __name__ == "__main__":
    main(sys.argv[1:])