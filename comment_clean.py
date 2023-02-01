import os #module that is used for operating system dependent functionality
import pandas #python library used for working with data sets
import pathlib #module for filesystem paths and operations with them
import argparse #module for operations with command line arguments
import numpy #library for working with arrays

#variables for table symbols
s_green = ":white_check_mark:"
s_red = ":red_circle:"
s_yellow = ":high_brightness:"
s_nok = ":x:"

#command line arguments
#TODO explain each one of them
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--test', type=str, required=True, help="Path to test results")
parser.add_argument('-r', '--range', type=str, help="Path to threshold config")
parser.add_argument('-n', '--number', type=int, required=True, help="Number of results for calculation")
parser.add_argument('-s', '--std_dev', action='store_true', help="Calculate standard deviation of last n results")
parser.add_argument('-m', '--max_value', action='store_true', help="Compare to max value from last n results")
parser.add_argument('-p', '--pr', action='store_true', help="Triggered inside PR - use PR_ID")
args = parser.parse_args()

#function that returns last nth path
#key=os.path.getmtime ----> argument in sorted function that servers to sort files by some criteria, in this case last modification time
#Finds all the files with prefix perf and takes last nth
def get_last_nth(n,path):
    new_path = sorted(pathlib.Path(path).glob('perf*'), key=os.path.getmtime)[-n]
    return new_path

#function that returns commit id
#each commit has unique id
def get_commit(path):
    #changes directory to path argument
    os.chdir(path)
    # opens commit.txt on the path location and extracts commit_id
    with open('commit.txt') as git:
        commit_id = str(git.readlines(1))[9:15]
    git.close()
    return commit_id

#function that returns csv file that is loaded into a variable with only third column without header
def get_result(path):
    # changes directory to path argument
    os.chdir(path)
    #load csv file into a variable
    result_data = pandas.read_csv('results.csv', header=None, usecols=[2])
    return result_data

#function that returns csv file that is loaded into a variable with only first and second column without header
def get_name(path):
    # changes directory to path argument
    os.chdir(path)
    # load csv file into a variable
    test_names = pandas.read_csv('results.csv', header=None, usecols=[0,1])
    return test_names

#get script path and put it into a variable script_path
script_path = os.path.dirname(os.path.realpath(__file__))

#variables declaration
# {} ---> dictionary  dict = { one: 1, two: 2 }
# [] ---> list  list = ['one', 'two', 3, 4]
commits = {}
performance_data = {}
performance_tests = {}
stdev = []
max_val = []
std_mean = []

#if command line argument pr is present(not empty or provided) variable n will be equal to the number of arguments+2,
#else it will be num of arguments+1
if args.pr:
    n = args.number + 2
else:
    n = args.number + 1

#variable sucesfull will be int and it is set to 0
#As we can see from below, sucessfull is variable that is used as indicator ????????????????/
succesfull = 0
#variable i is 1
i = 1
#while loop will be executed until i reaches n
while i < n:
    #if variable i is 1 and pull request is provided
    if (i==1) and (args.pr):
        #create path as formatted string from PR ID that is created if args.pr is provided
        path = f"{args.test}-{os.environ.get('PR_ID')}"
        x = i
    #else if pull request is provided
    elif args.pr:
        x = i-1
        # create path as formatted string without PR ID
        path = f"{args.test}"
    #If there is no pull request (pr command line argument)
    else:
        # create path as formatted string without PR ID
        path = f"{args.test}"
        x = i

    #change directory to location that is returned by function (x determines the last nth path)
    #in short words change location to latest created/modified folder which will be perf-{some_number}
    os.chdir(get_last_nth(x,path))
    #if file results.csv exist in the current directory
    if os.path.exists('results.csv'):
        #increment sucesfull by 1
        succesfull+=1
        #if sucesfull is equal to 1
        if succesfull==1:
            #populate dictionary performance_tests with key tests and value that is going to be entire csv.
            #Do that by using combination of get_name and get_last_nth function that will return csv loaded into a dictionary
            performance_tests[f'tests'] = get_name(get_last_nth(x,path))
            # populate dictionary performance_data with key data_{sucesfull} by using combination of get_result and get_last_nth function that will return csv file and that will be value
            performance_data[f'data_{succesfull}'] = get_result(get_last_nth(x,path))
            # populate dictionary commits with key commit_{sucesfull} by using combination of get_commit and get_last_nth function that will return commit id
            commits[f'commit{succesfull}'] = get_commit(get_last_nth(x,path))
        #If sucesfull is 2
        elif succesfull==2:
            # populate dictionary performance_data with key data_{sucesfull} by using get_result function that will return csv file
            performance_data[f'data_{succesfull}'] = get_result(get_last_nth(x,path))
            # populate dictionary commits with key commit_{sucesfull with get commit function that will return commit id
            commits[f'commit{succesfull}'] = get_commit(get_last_nth(x,path))
        #If sucesfull is 3 or greater
        elif succesfull>=3:
            # populate dictionary performance_data with key data_{sucesfull} with get result function that will return csv file
            performance_data[f'data_{succesfull}'] = get_result(get_last_nth(x,path))
    #if results.csv does not exist
    else:
        #increment n by 1
        n+=1
    #increment i by 1 either way
    i+=1

#Iterate through performance_data dictionary and find those with data_1 key (1 is sucesfull marker)
#performance_data['data_1'] is entire csv structure and len will return number of elements
#performance_calc will be dictionary with keys test_{i}
# :[] ---------------> EMPTY LIST
performance_calc = {f'test_{i}':[] for i in range(0,len(performance_data['data_1']))}
#iterate through dictionary performance_data and do what ????????????????
for key, value in performance_data.items():
    if args.pr and key == 'data_1':
        continue
    else:
        for i,test in enumerate(performance_calc):
            try:
                performance_calc[f'test_{i}'].append(value.iloc[i][2])
            except:
                pass

#iterate through performance_data dictionary with data_1 key
for i in range(0,len(performance_data['data_1'])):
    #finds max value in performance_calc dictionary with test_{i} and appends it in max_val
    max_val.append(numpy.nanmax(performance_calc.get(f'test_{i}')))
    # finds standard deviation and appends it in stdev
    stdev.append(numpy.nanstd(performance_calc.get(f'test_{i}')))
    # finds standard mean and appends it in std_mean
    std_mean.append(numpy.nanmean(performance_calc.get(f'test_{i}')))

#creates a data frame from performance_tests['tests'] and puts it into a variable tests
tests = pandas.DataFrame(performance_tests['tests'])
#concatonates tests data frame end performance data data_1 dictionary
data1 = pandas.concat([tests,performance_data['data_1']], axis=1, ignore_index=True)
#creates a data frame from performance_data['data_2'] and puts it into a variable data2
data2 = pandas.DataFrame(performance_data['data_2'])

#concats standard deviation and standard mean
dev = pandas.concat([pandas.DataFrame(stdev),pandas.DataFrame(std_mean)], axis=1, ignore_index=True)
#?????????
dev.columns = ['std','mean']
#????????? rsd --> relative standard deviation
#Creates a column rsd and gives a formula for calculation ( like exel )
dev['rsd'] = (dev['std'] / dev['mean']) * 100
#?????????
rsd = dev[['rsd']]

#if command line argument max value exist set threshold
if args.max_value:
    threshold = pandas.DataFrame(max_val)
#if command line argument range exist set threshold differently
elif args.range:
    os.chdir(args.range)
    threshold = pandas.read_csv('threshold.csv', header=None, usecols=[1], skiprows=[0])
#if command line argument range exist set threshold differently
elif args.std_dev:
    threshold = rsd

#concat data1,data2 and threshold variables
combined = pandas.concat([data1,data2,threshold], axis=1, ignore_index=True)

#Give the name to the columns of the combined table above
combined.columns = ['Test','Batch','Time new','Time old','Threshold']

# Template for results
Rate_new = f"Rate new <br />{commits['commit1']}"
Rate_old = f"Rate old <br />{commits['commit2']}"
combined[Rate_new] = combined['Batch'] * 1000 / combined['Time new']
combined[Rate_old] = combined['Batch'] * 1000 / combined['Time old']
combined['Diff'] = (combined[Rate_new] - combined[Rate_old]) / ((combined[Rate_new] + combined[Rate_old]) / 2)

#converts value to percent
# why 2 ---> 2 decimals
# shows percentage in 2 decimals and show percentage sign
def convert_to_percent(val):
    val = "{0:.2%}".format(val)
    return(val)

#returns string ?????
#shows digits as strings
def format_rate(val):
    return str('{:,.2f}'.format(val))

#if command line argument max_value exists
if args.max_value:
    #creates a list of conditions
    conditions = [combined['Time new'] >= combined['Threshold'], combined['Time new'] < combined['Threshold'], combined['Time new'].isnull()]
    #creates a list of choices
    choices = [s_green,s_red,s_nok]
    combined['Diff'] = combined['Time new'] / combined['Threshold'] - 1
else:
    #if max value is not provided create a different list of conditions anc choices
    conditions = [(combined['Diff'].abs() < combined['Threshold']), (combined['Diff'] > combined['Threshold']), (combined['Diff'] <0) & (combined['Diff']< combined['Threshold']), combined['Diff'].isnull()]
    choices = [s_green,s_yellow,s_red,s_nok]

#returns an array drawn from elements in choicelist, depending on conditions
combined['Compare'] = numpy.select(conditions, choices)
combined['Diff'] = combined['Diff'].apply(convert_to_percent)

#if max vlaue is provided
if args.max_value:
    new_name = f"Compared to best <br />of last {args.number} runs"
    combined.rename(columns={'Diff':new_name}, inplace=True) 

combined[Rate_new] = combined[Rate_new].apply(format_rate)
combined[Rate_old] = combined[Rate_old].apply(format_rate)

check_red = (combined.Compare==s_red).sum()
check_nok = (combined.Compare==s_nok).sum()
check_yellow = (combined.Compare==s_yellow).sum()

if check_red >= 1 or check_nok >= 1:
    status = f'This build is not recommended to merge {s_red}'
elif check_yellow >= 1:
    status = f'Check results before merge {s_yellow}'
else:
    status = f'This build is OK for merge {s_green}'

os.chdir(script_path)
formated = combined.drop(columns=['Batch','Time new','Time old','Threshold'])
print(formated.to_markdown('temp.md', index=False, colalign=('left','right','right','right','center')))

md_file = open('temp.md', 'a')
md_file.write(f'\n\n\n{status}')
md_file.close()