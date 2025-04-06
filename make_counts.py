"""
Module: make_counts.py
Description:
    This module processes video files in a specified directory by counting their frames.
    The frame counts, along with the corresponding filenames, are saved in a CSV file ('counts.csv').
    Video processing is handled by OpenCV, and the module leverages parallel processing through
    the concurrent.futures.ProcessPoolExecutor along with multiprocessing.Manager to safely share data
    between processes.
Usage:
    The script is intended to be executed as a standalone program. Command-line arguments include:
      --path       : Path to the directory containing the video files (default is the current directory).
      --max-workers: Number of worker processes to use for parallel processing (default is 20).
      --debug      : Enable debug level logging (optional).
    The script filters video files based on the extensions '.mp4' and '.h264', counts the frames for
    each video, and outputs a CSV file with columns "filename" and "framecount".
Functions:
    count_frames_and_write_new_file(original_path: str, file: str, dataframe_list: list, lock) -> int:
        Processes a single video file by performing the following:
          - Constructs the video file path.
          - Opens the video file using OpenCV's VideoCapture.
          - Iterates through the video frame by frame to count the total number of frames.
          - Logs progress periodically (every 10,000 frames).
          - Safely appends the filename and its corresponding frame count into a shared list using a lock.
          - Releases the video capture resource after processing.
        Parameters:
          original_path (str): The directory path where the video file is located.
          file (str): The filename of the video to be processed.
          dataframe_list (list): A shared list for collecting the [filename, framecount] pairs.
          lock: A multiprocessing lock to ensure that appending to the shared list is thread-safe.
        Returns:
          int: The number of frames counted in the video (the result is indirectly used by appending to the shared list).
        Exceptions:
          - Logs an error message if any exceptions occur during the frame counting process, ensuring proper cleanup.
Notes:
    - The script uses a UNIX command via subprocess (i.e., 'ls' and 'grep') to filter video files,
      so it may be platform specific.
    - The entry point includes a call to freeze_support() to support running frozen executables.
    - Logging is set up to provide informative messages, with optional debug logging available.
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
        "--path",
        type=str,
        help="Path to the directory containing the video files",
        default=".",
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

    original_path = os.path.join(os.getcwd(), args.path)

    try:
        command = "ls | grep -E '.mp4$|.h264$'"
        ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        result = subprocess.run(command,
                                shell=True,
                                capture_output=True,
                                text=True)
        file_list = sorted(
            [ansi_escape.sub("", line) for line in result.stdout.splitlines()])
        logging.debug(f"File List: {file_list}")
    except Exception as e:
        logging.error(f"Error in getting file list with error {e}")

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
            dataframe.to_csv(os.path.join(original_path, "counts.csv"),
                             index=False)
    except Exception as e:
        logging.error(f"Error in creating counts.csv with error {e}")
