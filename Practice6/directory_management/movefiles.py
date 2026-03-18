import shutil
import os

# create directory if it doesn't exist
os.makedirs("folder1/sample,txt", exist_ok=True)

# move file
if os.path.exists("sample.txt"):
    shutil.move("sample.txt", "folder1/sample.txt")
    print("File moved.")
else:
    print("sample.txt not found.") 

#2nd variant 
# import shutil
# import os

# # path to the file from another folder
# source = "../file_handling/sample.txt"   # file location
# destination = "folder1/sample.txt"      # where we move it

# # check if file exists
# if os.path.exists(source):
    
#     shutil.move(source, destination)  # move file
    
#     print("File moved to folder1.")
    
# else:
#     print("sample.txt not found.")