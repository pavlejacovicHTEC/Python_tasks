### Explanation

The main goal of the script is to compare results of the data models/tests.

It takes multiple command-line arguments:

test --> Path to test results file\
number --> Number of previous results you want to compare your last result to\

Your main result can be stored in pull request that is opened in which case we need argument
pr --> location of PR folder with all of it's commits which are seperate folders

Besides these 3 arguments, there is 3 more arguments that you can provide, but 
only one of them is possible\

range --> Path to threshold config\
std_dev --> Standard deviation of the last number of results you provided\
max_value --> Max value from the last number of results

