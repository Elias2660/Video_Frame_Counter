"""
Module Name: optimized_make_counts.py

Description:
    Efficiently counts frames in .mp4 and .h264 video files by reading OpenCV’s CAP_PROP_FRAME_COUNT
    property instead of decoding each frame. Scans the target directory, collects filename/framecount pairs,
    and writes them to 'counts.csv'.

Usage:
    python optimized_make_counts.py \
        --video-filepath <directory> \
        --output-filepath <directory> \
        [--max-workers <num>] \
        [--debug]

Arguments:
    --video-filepath    Directory containing video files (.mp4, .h264). (default: ".")
    --output-filepath   Directory where 'counts.csv' will be written. (default: ".")
    --max-workers       Reserved for compatibility (not used). (default: 20)
    --debug             Enable DEBUG-level logging. (default: False)

Workflow:
    1. Parse command-line arguments and set up logging.
    2. Resolve full path to `--video-filepath`.
    3. List all files ending in '.mp4' or '.h264'.
    4. For each video:
         - Open with cv2.VideoCapture.
         - Retrieve total frame count via `cap.get(cv2.CAP_PROP_FRAME_COUNT)`.
         - Release the capture.
         - Append [filename, count] to a data list.
    5. Build a pandas DataFrame from collected data, sort by filename, and save as 'counts.csv'.
    6. Log progress and any errors encountered.

Dependencies:
    - OpenCV (cv2)
    - pandas
    - argparse, logging, os
"""

import argparse
import logging
import os

import cv2
import pandas as pd

if __name__ == "__main__":
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
        dataframe.to_csv(os.path.join(args.output_filepath, "counts.csv"),
                         index=False)
    except Exception as e:
        logging.error(f"Error in creating counts.csv with error {e}")
