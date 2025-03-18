import pandas as pd
import os
import logging
import argparse
import cv2
import re
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create counts.csv file")

    parser.add_argument(
        "--path",
        type=str,
        help="Path to the directory containing the video files",
        default=".",
    )
    parser.add_argument(
        "--max-workers", type=int, help="Number of processes to use", default=20
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging", default=False
    )
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
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        file_list = sorted(
            [ansi_escape.sub("", line) for line in result.stdout.splitlines()]
        )
        logging.debug(f"File List: {file_list}")
    except Exception as e:
        logging.error(f"Error in getting file list with error {e}")

    try:
        dataframe_list = []

        logging.info(f"File List: {file_list}")

        for file in file_list:
            path = os.path.join(original_path, file)
            logging.info(f"Capture about to {file} about to be established")
            cap = cv2.VideoCapture(path)
            count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            dataframe_list.append([file, count])
            cap.release()

        dataframe = pd.DataFrame(
            list(dataframe_list), columns=["filename", "framecount"]
        )

        logging.debug(f"DataFrame about to be sorted")
        dataframe = dataframe.sort_values(by="filename")
        logging.debug(f"DataFrame about to be saved")
        dataframe.to_csv(os.path.join(original_path, "counts.csv"), index=False)
    except Exception as e:
        logging.error(f"Error in creating counts.csv with error {e}")
