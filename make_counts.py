"""
Module Name: make_counts.py

Description:
    Counts frames in all .mp4 and .h264 videos under a given directory in parallel,
    and writes out a CSV file ('counts.csv') listing each filename and its frame count.
    Utilizes OpenCV for video access and multiprocessing to speed up per-file processing.

Usage:
    python make_counts.py \
        --video-filepath <video_directory> \
        --output-filepath <output_directory> \
        [--max-workers <num_processes>] \
        [--debug]

Arguments:
    --video-filepath    Directory containing the video files to process (default: '.')
    --output-filepath   Directory where 'counts.csv' will be written (default: '.')
    --max-workers       Number of parallel worker processes to use (default: 20)
    --debug             Enable DEBUG‑level logging for detailed output

Workflow:
    1. Gather all files ending in .mp4 or .h264 in --video-filepath.
    2. Spawn a ProcessPoolExecutor with --max-workers processes.
    3. For each video, call count_frames_and_write_new_file():
         - Open the video with OpenCV VideoCapture.
         - Read frames in a loop, incrementing a counter and logging every 10,000 frames.
         - Append [filename, framecount] to a shared list under a lock.
    4. After all tasks complete, collect the shared list into a pandas DataFrame,
       sort by filename, and save as 'counts.csv' in --output-filepath.
    5. Log progress and any errors encountered.

Dependencies:
    - OpenCV (cv2)
    - pandas
    - argparse
    - concurrent.futures
    - multiprocessing (Manager, freeze_support, Lock)
    - logging
    - os, re, subprocess
"""

import argparse
import concurrent.futures
import logging
import os
import re
import subprocess
from multiprocessing import freeze_support
from multiprocessing import Lock
from multiprocessing import Manager

import cv2
import pandas as pd


def count_frames_and_write_new_file(original_path: str, file: str,
                                    dataframe_list: list, lock) -> int:
    """

    :param original_path: str:
    :param file: str:
    :param dataframe_list: list:
    :param lock: param original_path: str:
    :param file: str:
    :param dataframe_list: list:
    :param original_path: str:
    :param file: str:
    :param dataframe_list: list:
    :param original_path: str:
    :param file: str:
    :param dataframe_list: list:
    :param original_path: str:
    :param file: str:
    :param dataframe_list: list:
    :param original_path: str:
    :param file: str:
    :param dataframe_list: list:

    """
    path = os.path.join(original_path, file)
    logging.info(f"Capture to video {file} about to be established")
    cap = cv2.VideoCapture(path)

    try:
        logging.debug(f"Capture to video {file} established")
        count = 0
        while cap.isOpened():
            ret, _ = cap.read()
            if count % 10000 == 0 and count != 0:
                logging.info(f"Frame {count} read from {file}")
            if not ret:
                break
            count += 1

        logging.info(f"Adding {file} to DataFrame list")
        with lock:
            logging.info(f"Lock acquired to file {file}")
            dataframe_list.append([file, count])
        logging.info(f"Lock released and added {file} to DataFrame list")
        cap.release()
        logging.info(f"Capture to video {file} released")
    except Exception as e:
        logging.error(f"Error in counting frames for {file} with error {e}")
        cap.release()


if __name__ == "__main__":
    freeze_support()

    parser = argparse.ArgumentParser(description="Create counts.csv file")

    parser.add_argument(
        "--video-filepath",
        type=str,
        help="Path to the directory containing the video files",
        default=".",
    )
    parser.add_argument(
        "--output-filepath",
        type=str,
        help="Where the counts.csv file is going to be written to",
        default="."
    )
    parser.add_argument("--max-workers",
                        type=int,
                        help="Number of processes to use",
                        default=20)
    parser.add_argument("--debug",
                        action="store_true",
                        help="Enable debug logging",
                        default=False)
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s: %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug(f"Debug logging enabled")
        
    # should work even if not a relative path
    original_path = os.path.join(os.getcwd(), args.video_filepath)
    # original_path = os.path.join(args.video_filepath)



    file_list = [file for file in os.listdir(args.video_filepath) if file.endswith(".h264") or file.endswith(".mp4")]
    if len(file_list) == 0:
        raise Exception("No video files have been found. Either they have been deleted or the specified path is wrong.")

    logging.debug(f"File List: {file_list}")


    try:
        with Manager() as manager:
            # prevent multiple processes from writing to each other
            # might not be needed, but it feels safer to keep in
            lock = manager.Lock()
            dataframe_list = manager.list()

            logging.info(f"File List: {file_list}")

            with concurrent.futures.ProcessPoolExecutor(
                    max_workers=args.max_workers) as executor:
                logging.debug(f"Executor established")
                futures = [
                    executor.submit(
                        count_frames_and_write_new_file,
                        original_path,
                        file,
                        dataframe_list,
                        lock,
                    ) for file in file_list
                ]
                concurrent.futures.wait(futures)
                logging.debug(f"Executor mapped")

            dataframe = pd.DataFrame(list(dataframe_list),
                                     columns=["filename", "framecount"])
            logging.debug(f"DataFrame about to be sorted")
            dataframe = dataframe.sort_values(by="filename")
            logging.debug(f"DataFrame about to be saved")
            dataframe.to_csv(os.path.join(args.output_filepath, "counts.csv"),
                             index=False)
    except Exception as e:
        logging.error(f"Error in creating counts.csv with error {e}")
