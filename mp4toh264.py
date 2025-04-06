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
    logging.info(f"Capture to Path {file} about to be established")
    cap = cv2.VideoCapture(path)

    new_path, frame_width, frame_height, fps = None, None, None, None
    # also convert to .mp4
    if path.endswith(".mp4"):
        new_path = path.replace(".mp4", ".h264")
        logging.info(f"Capture to video {file} about to be established")
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        out = cv2.VideoWriter(new_path, cv2.VideoWriter_fourcc(*"H264"), fps,
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
                        f"Frame {count} written to {file.replace('.mp4', '.h264')}"
                    )
            count += 1

        logging.info(f"Adding {file} to DataFrame list")
        with lock:
            logging.info(f"Lock acquired to file {file}")
            dataframe_list.append([file.replace(".mp4", ".h264"), count])
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
        command = "ls | grep -E '.mp4$'"
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

            logging.info(f"Moving the files to new directory")
            subprocess.run("rm -rf mp4_files", shell=True)
            subprocess.run("mkdir -p mp4_files", shell=True)
            subprocess.run("mv *.mp4 mp4_files/", shell=True)
    except Exception as e:
        logging.error(f"Error in creating counts.csv with error {e}")
