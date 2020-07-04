import os
import sys
import json

result_messages = []
json_template = {}

user_input = input("Enter the path of your json file(s): ")

assert os.path.exists(user_input),"I did not find the file(s) at "+str(user_input)
print("We found your file(s)!")

directory = user_input

for file in os.listdir(directory):
    if file.endswith(".json") and file != "message.json":
        # Print the file name to debug
        print(os.path.join(directory, file))
        with open(os.path.join(directory, file)) as f:
            data = json.load(f)
            if (len(json_template) == 0):
                json_template = data
            messages = data["messages"]
            result_messages += messages

json_template['messages'] = result_messages

with open(os.path.join(directory, "message.json"),'w') as f:
    f.write(json.dumps(json_template, indent=2))
