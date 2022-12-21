import argparse
import os
import subprocess
import string

parser = argparse.ArgumentParser()
parser.add_argument('-dl','--directory_location', type=str, required=True, help="location of a directory you would wish to execute git operation on")
parser.add_argument('-ifl','--ignore_file_location', type=str, required=True, help="excluded directories file location that you do not wish to run git operation on")
args = parser.parse_args()
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

for element in get_wanted_git_folders(args.directory_location,args.ignore_file_location):
    os.chdir(element)

    subprocess.call(["git","branch"])

    #Catch output of subprocess
    #WAY 1
    x=subprocess.check_output(["git","branch"])
    #WAY 2
    command = "git branch"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
    output = process.communicate()[0]
    print (output)



os.chdir(script_path)