# Labeling Tool for VCR
> Labeling tool for video content recognition based on deep learning

This provides a convenient GUI for non-tech users to draw bounding boxes around targets in the image.

## Functions
1) Load image folder for labeling
2) Select content type of labeling
3) Adjust size of the bounding boxes
4) Add new bounding boxes with label from each .names file
5) Delete unnecessary bounding boxes
6) Read/write image information from the json file

## Environment setup

#### Installation

- Anaconda latest version
  - python 3.6 or above 
- Python packages
  - `pip install -r requirements.txt`

#### Creating an executable file for Windows OS

- Pyinstaller latest version
  - `pyinstaller -w -F vcr_labeling.py`
  
