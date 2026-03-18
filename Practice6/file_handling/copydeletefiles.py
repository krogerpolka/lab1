import shutil  # module for file operations
import os      # module for operating system functions

# copy sample.txt to a backup file
shutil.copy("sample.txt", "backup_sample.txt")

print("File copied.")

# check if file exists before deleting
if os.path.exists("backup_sample.txt"):
    
    os.remove("backup_sample.txt")  # delete file
    
    print("Backup file deleted.")
    
else:
    print("File not found.")