import os
import pandas
import pathlib
import argparse
import numpy
os.environ ['PR_ID'] = "2"
s_green = ":white_check_mark:"
s_red = ":red_circle:"
s_yellow = ":high_brightness:"
s_nok = ":x:"
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--test', type=str, required=True, help="Path to test results")
parser.add_argument('-r', '--range', type=str, help="Path to threshold config")
parser.add_argument('-n', '--number', type=int, required=True, help="Number of results for calculation")
parser.add_argument('-s', '--std_dev', action='store_true', help="Calculate standard deviation of last n results")
parser.add_argument('-m', '--max_value', action='store_true', help="Compare to max value from last n results")
parser.add_argument('-p', '--pr', action='store_true', help="Triggered inside PR - use PR_ID")
args = parser.parse_args()

#Get last results depends of number "n"
def get_last_nth(n,path):
    new_path = sorted(pathlib.Path(path).glob('perf*'), key=os.path.getmtime)[-n]
    print(new_path)
    print ("this is last path ^^")
    return new_path
    
def get_commit(path):
    os.chdir(path)
    with open('commit.txt') as git:
        commit_id = str(git.readlines(1))[9:15]
    git.close()
    return commit_id
def get_result(path):
    os.chdir(path)
    result_data = pandas.read_csv('results.csv', header=None, usecols=[2])
    print (result_data)
    print ("this print result data^^")
    return result_data

#Read names of tests from results.csv
def get_name(path):
    os.chdir(path)
    test_names = pandas.read_csv('results.csv', header=None, usecols=[0,1])
    print (test_names,)
    print ("this print test names ^^")
    return test_names

script_path = os.path.dirname(os.path.realpath(__file__))
commits = {}
performance_data = {}
performance_tests = {}
stdev = []
max_val = []
std_mean = []

print (args.pr)
print ("this is args")
#if -pr exist than  n+2
if args.pr:
    n = args.number + 2
    print (n)
    print ("this is n")
else:
    #number of results +1
    n = args.number + 0 
    print (n )
    print ("this is n2")
succesfull = 0
i = 1
while i < n:
    if (i==1) and (args.pr):
        path = f"{args.test}-{os.environ.get('PR_ID')}"
        # Get folder results with env PR_ID
        x = i
        print (x, "this is first cond")
    elif args.pr:
        x = i-1
        path = f"{args.test}"
        print (x, "this is second cond")
    else:
        path = f"{args.test}"
        x = i
        print (x, "this is third cond")
    os.chdir(get_last_nth(x,path))
    #return last results
    if os.path.exists('results.csv'):
        succesfull+=1
        if succesfull==1:
            #Print names of tests
            performance_tests[f'tests'] = get_name(get_last_nth(x,path))
            print (performance_tests, 'PERFORMANCE TEST ')
            performance_data[f'data_{succesfull}'] = get_result(get_last_nth(x,path))
            print (performance_data)
            print ("PERFORMANCE DATA ^^")
            commits[f'commit{succesfull}'] = get_commit(get_last_nth(x,path))

        elif succesfull==2:
            performance_data[f'data_{succesfull}'] = get_result(get_last_nth(x,path))
            commits[f'commit{succesfull}'] = get_commit(get_last_nth(x,path))

        elif succesfull>=3:
            performance_data[f'data_{succesfull}'] = get_result(get_last_nth(x,path))
    else:
        n+=1
    i+=1
    print (succesfull)
    print ("this is succesfull^^")
    
    #print (n, "n")
    #print (i, "i" )

performance_calc = {f'test_{i}':[] for i in range(0,len(performance_data['data_1']))}
#print(performance_calc, "this is perfor calc")
for key, value in performance_data.items():
    if args.pr and key == 'data_1':
        continue
    else:
        for i,test in enumerate(performance_calc):
            try:
                #
                #print (i, test, "this is i and test enumerate")
                # calculation append 
                performance_calc[f'test_{i}'].append(value.iloc[i][2])
            except:
                pass

for i in range(0,len(performance_data['data_1'])):
    max_val.append(numpy.nanmax(performance_calc.get(f'test_{i}')))
    stdev.append(numpy.nanstd(performance_calc.get(f'test_{i}')))
    std_mean.append(numpy.nanmean(performance_calc.get(f'test_{i}')))

tests = pandas.DataFrame(performance_tests['tests'])
data1 = pandas.concat((tests,performance_data['data_1']), axis = 1, ignore_index=True)
data2 = pandas.DataFrame(performance_data['data_2'])

dev = pandas.concat([pandas.DataFrame(stdev),pandas.DataFrame(std_mean)], axis=1, ignore_index=True)
dev.columns = ['std','mean']
dev['rsd'] = (dev['std'] / dev['mean']) * 100
rsd = dev[['rsd']]

if args.max_value:
    threshold = pandas.DataFrame(max_val)
elif args.range:
    os.chdir(args.range)
    threshold = pandas.read_csv('threshold.csv', header=None, usecols=[1], skiprows=[0])
elif args.std_dev:
    threshold = rsd
     
combined = pandas.concat([data1,data2,threshold], axis=1, ignore_index=True)

combined.columns = ['Test','Batch','Time new','Time old','Threshold']

Rate_new = f"Rate new <br />{commits['commit1']}"
Rate_old = f"Rate old <br />{commits['commit2']}"
combined[Rate_new] = combined['Batch'] * 1000 / combined['Time new']
combined[Rate_old] = combined['Batch'] * 1000 / combined['Time old']
combined['Diff'] = (combined[Rate_new] - combined[Rate_old]) / ((combined[Rate_new] + combined[Rate_old]) / 2)

def convert_to_percent(val):
    val = "{0:.2%}".format(val)
    return(val)

def format_rate(val):
    return str('{:,.2f}'.format(val))

if args.max_value:
    conditions = [combined['Time new'] >= combined['Threshold'], combined['Time new'] < combined['Threshold'], combined['Time new'].isnull()]
    choices = [s_green,s_red,s_nok]
    combined['Diff'] = combined['Time new'] / combined['Threshold'] - 1
else:
    conditions = [(combined['Diff'].abs() < combined['Threshold']), (combined['Diff'] > combined['Threshold']), (combined['Diff'] <0) & (combined['Diff']< combined['Threshold']), combined['Diff'].isnull()]
    choices = [s_green,s_yellow,s_red,s_nok]

combined['Compare'] = numpy.select(conditions, choices)
combined['Diff'] = combined['Diff'].apply(convert_to_percent)

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