import os
import tempfile
import shutil
from pathlib import Path

def can_access_directory(directory):
    return os.access(directory, os.R_OK)

def traverse_directory(directory, prefix="", depth=0):
    tree = []
    if can_access_directory(directory):
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    tree.append((entry.path, depth))
                    tree.extend(traverse_directory(entry.path, prefix + "  ", depth + 1))
    return tree

def write_temp_files(tree, temp_dir):
    for idx, (entry, depth) in enumerate(tree):
        file_path = os.path.join(temp_dir, f"temp_file_{idx}.txt")
        with open(file_path, "w") as f:
            f.write(f"{depth * '  '}{entry}\n")

def aggregate_temp_files(temp_dir, output_file):
    with open(output_file, "w") as outfile:
        for temp_file in sorted(os.listdir(temp_dir)):
            with open(os.path.join(temp_dir, temp_file), "r") as infile:
                outfile.write(infile.read())

def main():
    directory = Path.home() / "Downloads"
    tree = traverse_directory(directory)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        write_temp_files(tree, temp_dir)
        aggregate_temp_files(temp_dir, "log.txt")

main()
