# this script is to be used for extracting the MIME headers of all .eml files in a given directory
# output is a .txt file for each ,eml file containing the MIME header from that .eml file
# should preserve the id's (file names without extension) of the .eml files

# target directory name should be provided as command line argument

import os
import sys

def extract_mime_headers(input_directory_path, output_directory_path):
    
    # extract id's of all .eml files
    # making sure to not take file extension

    # get all .eml files in target dir
    eml_file_names_in_dir = [
        possible_eml_file for possible_eml_file in os.listdir(input_directory_path)
        if possible_eml_file[-4:].lower() == ".eml"
    ]

    eml_paths_in_dir = [
        os.path.join(input_directory_path,eml_file) for eml_file in eml_file_names_in_dir
    ]


    for eml_path in eml_paths_in_dir:

        # construct txt file path for current eml
        output_txt_name = os.path.basename(eml_path[:-4])+".txt"
        output_txt_path = os.path.join(output_directory_path,output_txt_name)

        with open(eml_path,mode='r',encoding='utf-8',errors='ignore') as input_file, open(output_txt_path,mode='w',encoding='utf-8') as output_file:
            
            while True:
                line = input_file.readline()

                # if line is empty, exit loop
                if line.strip() == "":
                    break
            
                else:
                    output_file.write(line)
                
                    

# first arg should be input dir, 2nd path shoud be output dir
def main(args):

    # input argument validation
    if not os.path.exists(args[0]):
        print(f"error: could not find first argument {args[0]} directory")
        sys.exit(1)
    
    if not os.path.isdir(args[0]):
        print(f"error: first argument is not a directory")
        sys.exit(1)


    if not os.path.exists(args[1]):
        print(f"error: could not find second argument {args[1]} directory")
        sys.exit(1)

    if not os.path.isdir(args[1]):
        print(f"error: second argument is not a directory")
        sys.exit(1)


    extract_mime_headers(args[0],args[1])


if __name__ == "__main__":
    main(sys.argv[1:])