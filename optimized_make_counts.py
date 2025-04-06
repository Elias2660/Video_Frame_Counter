"""
Script for counting video frames in media files and generating a CSV report.

This script searches for video files with extensions .mp4 and .h264 in the specified
directory, counts the total number of frames for each video using OpenCV, and writes
the results into a CSV file named "counts.csv". Logging is provided for both normal
and debug modes to help trace execution flow and potential issues.

Usage:
    python optimized_make_counts.py [--path PATH] [--max-workers MAX_WORKERS] [--debug]

Arguments:
    --path:
        Type: str
        Description: Path to the directory containing the video files.
        Default: "." (current working directory)

    ! no use, just for compatibility for the master_run.py
    --max-workers:
        Type: int
        Description: Number of processes to use (reserved for potential parallelizations).
        Default: 20

    --debug:
        Action: store_true
        Description: Enable debug logging to provide detailed output.
        Default: False

Workflow:
    1. Parse command-line parameters.
    2. Configure logging based on debug flag.
    3. Construct the full path to the directory with video files.
    4. Execute a shell command to list files filtered for .mp4 and .h264 formats.
    5. Iterate through each file:
         - Open the video using OpenCV.
         - Retrieve the total frame count.
         - Append the filename and frame count to a data collection list.
    6. Create a pandas DataFrame from the collected data.
    7. Sort the DataFrame by filename and save it as "counts.csv" in the same directory.
"""
import argparse
import logging
import os
import re
import subprocess

import cv2
import pandas as pd

if __name__ == "__main__":
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
        dataframe_list = []

        logging.info(f"File List: {file_list}")

        for file in file_list:
            # use .mp4 indexing function to find the frames without actually counting them
            path = os.path.join(original_path, file)
            cap = cv2.VideoCapture(path)
            count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            dataframe_list.append([file, count])
            cap.release()

        dataframe = pd.DataFrame(list(dataframe_list),
                                 columns=["filename", "framecount"])

        logging.debug(f"DataFrame about to be sorted")
        dataframe = dataframe.sort_values(by="filename")
        logging.debug(f"DataFrame about to be saved")
        dataframe.to_csv(os.path.join(original_path, "counts.csv"),
                         index=False)
    except Exception as e:
        logging.error(f"Error in creating counts.csv with error {e}")
