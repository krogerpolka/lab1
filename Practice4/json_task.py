import json #working with json files

with open("sample_data.json", "r") as x: #open file in reading format, save as x, with - close file after reading
    y = json.load(x) #convert to python -object(dictionary)

print("Interface Status")
print("=" * 80)
print(f"{'DN':<50} {'Description':<20} {'Speed':<8} {'MTU':<6}") #field with width going to right
print(f"{'-'*50:<50} {'-'*20:<20} {'-'*8:<8} {'-'*6:<6}") #creating separated line

for i in y["imdata"]: #through each element in list
    dn = i["l1PhysIf"]["attributes"]["dn"] #element i, to key, than attributes, and defined fields
    speed = i["l1PhysIf"]["attributes"]["speed"]
    mtu = i["l1PhysIf"]["attributes"]["mtu"]
    
    print(f"{dn:<50} {'':<20} {speed:<8} {mtu:<6}")
   