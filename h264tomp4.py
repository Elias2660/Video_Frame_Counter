"""
Module Name: h264tomp4.py

Description:
    Counts frames in video files and converts “.h264” inputs to “.mp4” outputs in parallel.
    - Reads every .h264 or .mp4 in the specified directory.
    - If a file ends with “.h264”, opens it, counts frames, and writes a new “.mp4” copy.
    - Records each output filename and its frame count into a shared list.
    - After processing, writes “counts.csv” mapping converted filenames to their frame counts.

Usage:
    python h264tomp4.py \
        --video-filepath <input_directory> \
        --output-filepath <output_directory> \
        [--max-workers <num_processes>] \
        [--debug]

Arguments:
    --video-filepath    Directory containing .h264/.mp4 files to process (default: “.”)
    --output-filepath   Directory where converted .mp4 and counts.csv are saved (default: “.”)
    --max-workers       Number of parallel worker processes (default: 20)
    --debug             Enable DEBUG‑level logging (default: False)

Workflow:
    1. Discover all .h264 and .mp4 files under --video-filepath.
    2. Using ProcessPoolExecutor with --max-workers:
         - For each file, open with cv2.VideoCapture.
         - If .h264, initialize VideoWriter for new .mp4 in --output-filepath.
         - Read frames in a loop, count them, and write to .mp4 if applicable.
         - Append [converted_filename, framecount] to a Manager list under a lock.
    3. After all tasks finish, assemble the shared list into a pandas DataFrame,
       sort by filename, and save as “counts.csv” in --output-filepath.
    4. Log progress every 10,000 frames and on errors.

Dependencies:
    - OpenCV (cv2)
    - pandas
    - argparse, logging, os, re, subprocess
    - concurrent.futures, multiprocessing (Manager, freeze_support, Lock)
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


def count_frames_and_write_new_file(original_path: str,output_path: str, file: str,
                                    dataframe_list: list, lock) -> int:
    """
    :param original_path: str:
    :param file: str:
    :param dataframe_list: list:
    :param lock: param 
    """
    path = os.path.join(original_path, file)
    logging.info(f"Capture to video {file} about to be established")
    cap = cv2.VideoCapture(path)

    new_path, frame_width, frame_height, fps = None, None, None, None
    # also convert to .mp4
    if path.endswith(".h264"):
        new_path = os.path.join(output_path, file.replace(".h264", ".mp4"))
        logging.info(f"Capture to video {new_path} about to be established")
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        out = cv2.VideoWriter(new_path, cv2.VideoWriter_fourcc(*"mp4v"), fps,
                              (frame_width, frame_height))

    try:
        logging.debug(f"Capture to video {file} established")
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if count % 10000 == 0 and count != 0:
                logging.debug(f"Frame {count} read from {file}")
            if not ret:
                break
            if new_path:
                out.write(frame)
                if count % 10000 == 0 and count != 0:
                    logging.debug(
                        f"Frame {count} written to {file.replace('.h264', '.mp4')}"
                    )
            count += 1

        logging.debug(f"Adding {file} to DataFrame list")
        with lock:
            logging.debug(f"Lock acquired to file {file}")
            dataframe_list.append([file.replace(".h264", ".mp4"), count])
        logging.debug(f"Lock released and added {file} to DataFrame list")
        cap.release()
        logging.debug(f"Capture to video {file} released")
        if new_path:
            out.release()
            logging.debug(f"Capture to video {file} released")
    except Exception as e:
        logging.error(f"Error in counting frames for {file} with error {e}")
        cap.release()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s: %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
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
    
    # should work even if not a relative path
    original_path = os.path.join(os.getcwd(), args.video_filepath)
    # original_path = os.path.join(args.video_filepath)


    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # weird stuff for regarding multiprocessing
    freeze_support()
    file_list = [file for file in os.listdir(args.video_filepath) if file.endswith(".h264") or file.endswith(".mp4")]
    
    if len(file_list) == 0:
        raise Exception("No video files have been found. Either they have been deleted or the specified path is wrong.")
    
    logging.debug(f"File List: {file_list}")

    try:
        with Manager() as manager:
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
                        args.output_filepath,
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
