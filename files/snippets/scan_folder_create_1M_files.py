# This script is used to optimize the "scan_folder" function
# It creates 1M files in a subfolder "test" of the "files" folder
# flake8: noqa

from pathlib import Path

path_folder = vs.file_path / "files" / "test"
path_folder.mkdir(exist_ok=True)

for i in range(1, 1000001):
    file_path = path_folder / f"file{i}"
    file_path.touch()
