import os

# Folder containing the images
folder_path = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector\test_set"

# Starting number for the renaming
start_number = 1

# Get all .jpg files in the folder
files = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]

# Sort files to ensure consistent renaming
files.sort()

# Rename the files
for i, file in enumerate(files):
    new_name = f"watch_test{start_number + i}.jpg"
    old_file = os.path.join(folder_path, file)
    new_file = os.path.join(folder_path, new_name)
    os.rename(old_file, new_file)

print("Renaming completed!")
