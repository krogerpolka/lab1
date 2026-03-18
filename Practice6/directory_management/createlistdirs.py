import os

# create nested directories
os.makedirs("folder1/folder2/folder3", exist_ok=True) #if exist create if not the same
print("Directories created.")

# list files and folders
print("Files and directories in current folder:")
print(os.listdir("."))