import os
import shutil
import sys


def rename_files(source_dir_path, target_dir_path):

    eml_files_list = os.listdir(source_dir_path)


    for eml_file in eml_files_list:

        shutil.copy2(os.path.join(source_dir_path,eml_file), os.path.join(target_dir_path,eml_file))


    txt_dir_contents = os.listdir(target_dir_path)

    #print(txt_dir_contents)

    for txt_file in txt_dir_contents:
        txt_new_name = txt_file[:-4] + ".txt"

        os.rename(os.path.join(target_dir_path,txt_file), os.path.join(target_dir_path,txt_new_name))


# expects source directory and target directory paths as arguments
def main(args):
    
    rename_files(args[0],args[1])



if __name__ == "__main__":
    main(sys.argv[1:])