"""
Module: h264tomp4.py

This module processes video files in the .h264 format, converting them to .mp4 while counting the number
of frames in each video. The processed data (new filename and frame count) is stored in a CSV file. Additionally,
the module moves the original .h264 files to a specified directory after processing.

The module leverages OpenCV for video capture and writing, concurrent.futures for parallel processing, and
multiprocessing for sharing data safely between processes. It also provides command-line arguments to specify
the path to video files, the number of parallel workers, and the logging level.

Functions:
    count_frames_and_write_new_file(original_path: str, file: str, dataframe_list: list, lock) -> int:
        Processes a video file by reading its frames, converting it to .mp4 if needed, counting the frames,
        and appending the results to a shared list. Logging statements provide feedback during processing.

Usage:
    To run the module:
        python h264tomp4.py --path [directory_path] --max-workers [num_workers] [--debug]

Processes a given video file by reading its frames, optionally converting it from .h264 to .mp4,
counting the number of frames, and appending the processed filename and frame count to a shared list.

    Parameters:
        original_path (str): The base directory path containing the video file.
        file (str): The name of the video file to be processed.
        dataframe_list (list): A list shared among processes to store the output as [filename, framecount].
        lock (Lock): A multiprocessing lock to ensure thread-safe updates to the shared dataframe_list.

    Returns:
        int: The total number of frames read from the video file.
             (Note: The function may not explicitly return a value in case of an exception.)

    Notes:
        - If the video file has a ".h264" extension, the function creates a new file with a ".mp4"
          extension and writes the converted video frames into it.
        - OpenCV's VideoCapture is used to read frames, and VideoWriter is used to write frames to the new file.
        - The function periodically logs progress (every 10,000 frames) for both reading and writing.
        - After processing, the original capture and video writer objects are properly released.
        - Any exceptions encountered during processing are logged, and the function safely releases
          any allocated resources.
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

    new_path, frame_width, frame_height, fps = None, None, None, None
    # also convert to .mp4
    if path.endswith(".h264"):
        new_path = path.replace(".h264", ".mp4")
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
                logging.info(f"Frame {count} read from {file}")
            if not ret:
                break
            if new_path:
                out.write(frame)
                if count % 10000 == 0 and count != 0:
                    logging.info(
                        f"Frame {count} written to {file.replace('.h264', '.mp4')}"
                    )
            count += 1

        logging.info(f"Adding {file} to DataFrame list")
        with lock:
            logging.info(f"Lock acquired to file {file}")
            dataframe_list.append([file.replace(".h264", ".mp4"), count])
        logging.info(f"Lock released and added {file} to DataFrame list")
        cap.release()
        logging.info(f"Capture to video {file} released")
        if new_path:
            out.release()
            logging.info(f"Capture to video {file} released")
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
    original_path = os.path.join(os.getcwd(), args.path)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # weird stuff for regarding multiprocessing
    freeze_support()
    try:
        command = "ls | grep -E '.h264$'"
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

            # keep the .h264 and the .mp4 files separate
            logging.info(f"Moving the files to new directory")
            subprocess.run("rm -rf h264_files", shell=True)
            subprocess.run("mkdir -p h264_files", shell=True)
            subprocess.run("mv *.h264 h264_files/", shell=True)

    except Exception as e:
        logging.error(f"Error in creating counts.csv with error {e}")
