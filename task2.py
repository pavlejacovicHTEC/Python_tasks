import os
import sys
import subprocess

#conditions for command line arguments, regarding if they exist
sys.exit("Please provide command line arguments (1.directory location 2.ignore file location 3.depth level 4.git operation)") if len(sys.argv) < 5 else print("All arguments are provided")
master_directory_location = sys.argv[1] if os.path.isdir(sys.argv[1]) and (sys.argv[1])[-1]==os.sep else sys.exit("Please provide valid directory! ")
ignore_file = sys.argv[2] if os.path.isfile(sys.argv[2]) else sys.exit("Please provide valid ignore file!")
depth_level = sys.argv[3] if int(sys.argv[3])>=1 else sys.exit("Minimal value for depth level is 1")
git_operation = sys.argv[4] if sys.argv[4] == "pull" or sys.argv[4] == "branch" else sys.exit("Please provide valid git operation! Valid operations: pull, branch")
script_path = os.getcwd()
current_number_of_file_separators = master_directory_location.count(os.sep)

def get_wanted_git_folders(main_directory, exclude_file):

    wanted_git_folders = []

    with open(exclude_file) as f:
        ignore_file_list = f.readlines()

    for path, currentDirectory, files in os.walk(main_directory):
        if path.count(os.sep) <= current_number_of_file_separators+int(depth_level)-1:
            if os.path.isdir(path + os.sep + ".git"):
                if path.split(os.sep)[-1] not in ignore_file_list and path.split(os.sep)[-1] + "\n" not in ignore_file_list:
                    wanted_git_folders.append(path + os.sep)

    #print(wanted_git_folders)
    return wanted_git_folders


for element in get_wanted_git_folders(master_directory_location,ignore_file):
    os.chdir(element)
    print("Operation git "+git_operation+"in process for directory "+ element)
    subprocess.call(["git", git_operation])

os.chdir(script_path)