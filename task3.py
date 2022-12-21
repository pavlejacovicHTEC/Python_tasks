import os
import sys

input_file = sys.argv[1] if os.path.isfile(sys.argv[1]) else sys.exit("Please provide existing input fie!")
output_file = sys.argv[2]

starting_template = "# LOG ENTRIES\n | 1.User Address | 2.RFC931       | 3.User auth    | 4.Date/Time    | 5.GMT Offset   | 6.Action       | 7.Return Code  | 8.Size         | 9.Referrer     | 10.APInfo      |\n|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|\n"

try:
    if output_file.split('.')[-1] != "md":
        output_file = output_file + ".md"

    with open(output_file, 'w') as f:
        f.write(starting_template)
except:
    sys.exit("Please provide valid output file!")


#Isolate variables
#Read line by line in loop

with open(input_file) as inp_file:
    for line in inp_file:
        if "HOME" in line or "AWAY" in line:
            elements = line.split(' ')
            user_address = elements[0]
            rfc931 = elements[1]
            user_auth = elements[2]
            date_time = elements[3]
            date_time=date_time.replace("[","")
            gmt_offset = elements[4]
            gmt_offset = gmt_offset.replace("]","")
            action = elements[5]+" "+elements[6]+" "+elements[7]
            action = action.replace("\"","")
            return_code = elements[8]
            size_code = elements[9]
            refferer = elements[10]
            refferer = refferer.replace("\"","")
            accpoInfo = elements[11]+" "+elements[12]+" "+elements[13]+" "+elements[14]
            accpoInfo = accpoInfo.replace("\"","")
            accpoInfo = accpoInfo.replace("\n", "")

        with open(output_file, 'a') as f:
            f.write("|"+user_address+"|"+rfc931+"|"+user_auth+"|"+date_time+"|"+gmt_offset+"|"+action+"|"+return_code+"|"+size_code+"|"+refferer+"|"+accpoInfo+"|\n")
