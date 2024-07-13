import pandas as pd
import os
import logging
import argparse
import cv2
import concurrent.futures
import re
import subprocess
from multiprocessing import Manager, freeze_support, Lock

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
# logging.getLogger().setLevel(logging.DEBUG)

parser = argparse.ArgumentParser(description="Create counts.csv file")

parser.add_argument(
    "--path",
    type=str,
    help="Path to the directory containing the video files",
    required=True,
)
parser.add_argument(
    "--max-workers", type=int, help="Number of processes to use", default=20
)
args = parser.parse_args()
original_path = os.path.join(os.getcwd(), args.path)


def count_frames_and_write_new_file(original_path: str, file: str, dataframe_list: list, lock) -> int:
    path = os.path.join(original_path, file)
    logging.info(f"Capture to Path {file} about to be established")
    cap = cv2.VideoCapture(path)
    
    new_path, frame_width, frame_height, fps = None, None, None, None
    # also convert to .mp4
    if (path.endswith(".mp4")):
        new_path = path.replace(".mp4", ".h264")
        logging.info(f"Capture to Path {new_path} about to be established")
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        out = cv2.VideoWriter(new_path, cv2.VideoWriter_fourcc(*'H264'), fps, (frame_width, frame_height))
    
    
    try:
        logging.debug(f"Capture to Path {file} established")
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if count % 1500 == 0:
                logging.info(f"Frame {count} read from {file}")
            if not ret:
                break
            if new_path:
                out.write(frame)
                if count % 1500 == 0:
                    logging.info(f"Frame {count} written to {file.replace('.mp4', '.h264')}")
            count += 1
            
        logging.info(f"Adding {file} to DataFrame list")
        with lock:
            logging.info(f"Lock acquired to file {file}")
            dataframe_list.append([file.replace('.mp4', '.h264'), count])
        logging.info(f"Lock released and added {file} to DataFrame list")
        cap.release()
        logging.info(f"Capture to Path {path} released")
        if new_path:
            out.release()
            logging.info(f"Capture to Path {new_path} released")
    except Exception as e:
        logging.error(f"Error in counting frames for {file} with error {e}")
        cap.release()


if __name__ == "__main__":
    freeze_support()
    try:
        command = "ls | grep -E '.mp4$'"
        ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        file_list = sorted(
            [ansi_escape.sub("", line) for line in result.stdout.splitlines()]
        )
        logging.debug(f"File List: {file_list}")
    except Exception as e:
        logging.error(f"Error in getting file list with error {e}")

    try:
        with Manager() as manager:
            lock = manager.Lock()
            dataframe_list = manager.list()

            logging.info(f"File List: {file_list}")

            with concurrent.futures.ProcessPoolExecutor(
                max_workers=args.max_workers
            ) as executor:
                logging.debug(f"Executor established")
                futures = [
                    executor.submit(count_frames_and_write_new_file, original_path, file, dataframe_list, lock)
                    for file in file_list
                ]
                concurrent.futures.wait(futures)
                logging.debug(f"Executor mapped")

            dataframe = pd.DataFrame(
                list(dataframe_list), columns=["filename", "framecount"]
            )
            logging.debug(f"DataFrame about to be sorted")
            dataframe = dataframe.sort_values(by="filename")
            logging.debug(f"DataFrame about to be saved")
            dataframe.to_csv(os.path.join(original_path, "counts.csv"), index=False)
    except Exception as e:
        logging.error(f"Error in creating counts.csv with error {e}")
