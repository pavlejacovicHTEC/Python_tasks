import os
import sys
import subprocess

#conditions for command line arguments, regarding if they exist
sys.exit("Please provide command line arguments (1.directory location 2.ignore file location)") if len(sys.argv) < 3 else print("All arguments are provided")
master_directory_location = sys.argv[1] if os.path.isdir(sys.argv[1]) and (sys.argv[1])[-1]==os.sep else sys.exit("Please provide valid directory! ")
ignore_file = sys.argv[2] if os.path.isfile(sys.argv[2]) else sys.exit("Please provide valid ignore file!")
script_path = os.getcwd()

def get_wanted_git_folders(main_directory, exclude_file):

    wanted_git_folders = []

    with open(exclude_file) as f:
        ignore_file_list = f.readlines()

    for file in os.listdir(main_directory):
        directory = os.path.join(main_directory, file)

        if os.path.isdir(directory) and os.path.isdir(directory+os.sep+".git"):
            if directory.split(os.sep)[-1] not in ignore_file_list and directory.split(os.sep)[-1]+"\n" not in ignore_file_list:
                wanted_git_folders.append(directory+os.sep)

    return wanted_git_folders

for element in get_wanted_git_folders(master_directory_location,ignore_file):
    os.chdir(element)
    print("Pulling changes on "+element)
    subprocess.call(["git","pull"])

os.chdir(script_path)


#test1