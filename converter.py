#%%
import pandas as pd 
import numpy as np
import os
import logging
import threading
import sys
import argparse
import cv2
import concurrent.futures
import re
import subprocess

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)

parser = argparse.ArgumentParser(description="Create counts.csv file")

parser.add_argument("--path", type=str, help="Path to the directory containing the video files", required=True)

args = parser.parse_args()
original_path = os.path.join(os.getcwd(), args.path)

_lock = threading.Lock()
dataframe = pd.DataFrame(columns=["filename", "framecount"])


def count_frames(original_path: str, file:str) -> int:
    global _lock
    global dataframe
    path = os.path.join(original_path, file)
    logging.info(f"Capture to Path {file} about to be established")
    cap = cv2.VideoCapture(path)
    try:
        logging.debug(f"Capture to Path {file} established")
        count = 0
        while cap.isOpened():
            ret, _ = cap.read()
            if count % 300 == 0:
                logging.debug(f"Frame {count} read from {file}")
            if not ret:
                break
            count += 1
        with _lock:
            logging.debug(f"Adding {file} to DataFrame")
            new_row = pd.DataFrame([[file, count]], columns=["filename", "framecount"])
            dataframe = pd.concat([dataframe, new_row], ignore_index=True)
        cap.release()
        logging.info(f"Capture to Path {path} released")
    except Exception as e:
        logging.error(f"Error in counting frames for {file} with error {e}")
        cap.release()
    

command = "ls | grep -E '.h264|.mp4'"
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
result = subprocess.run(command, shell=True, capture_output=True, text=True)
file_list = sorted([ansi_escape.sub('', line) for line in result.stdout.splitlines()])


threads = list()
print(f"File List: {file_list}")

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    executor.map(count_frames, [original_path]*len(file_list), file_list)
    
dataframe = dataframe.sort_values(by="filename")

dataframe.to_csv(os.path.join(original_path, "counts.csv"), index=False)


# %%

