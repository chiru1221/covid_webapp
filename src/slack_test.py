import json
import time
import sendslack
json_file = open('members.json', 'r', encoding='utf-8')
MEMBERS = json.load(json_file)

for name, id in MEMBERS.items():
    time.sleep(1)
    print(name, id)
    # sendslack.send(MEMBERS[name], name)
