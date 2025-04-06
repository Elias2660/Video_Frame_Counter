# Video Frame Counter

This project includes a Python script (`converter.py`) for counting the frames in video files (`.h264` and `.mp4` formats) within a specified directory and outputs the counts to a CSV file (`counts.csv`).

This project is most used with the [Unified-bee-Runner](https://github.com/Elias2660/Unified-bee-Runner).

## Installation

To set up the project environment:

1. Clone this repository to your local machine.
2. Ensure Python 3.12 and pip are installed.
3. Create a virtual environment:

   ```sh
   python3 -m venv venv
   ```

4. Activate Virtual Environment

   - on Windows

   ```powershell
   .\venv\Scripts\activate
   ```

   - on Unix of MacOS

   ```sh
   source venv/bin/activate
   ```

5. Install required dependencies:

```sh
pip install -r requirements.txt
```

## Usage

To count the frames in video files:

```sh
python make_counts.py --path <path_to_video_files>
```

This will generate a counts.csv file in the specified directory containing the filenames and their corresponding frame counts.

## Available Scripts

- Make Counts: Counts frames from video files and generates counts.csv.
  ```sh
  python make_counts.py --path <path_to_video_files>
  ```
- Optimized Counts: Quickly counts frames using video metadata.
  ```sh
  python optimized_make_counts.py --path <path_to_video_files>
  ```
- MP4 to H264 Converter: Converts .mp4 files to .h264 and counts frames.
  ```sh
  python mp4toh264.py --path <path_to_video_files>
  ```
- H264 to MP4 Converter: Converts .h264 files to .mp4 and counts frames.
  ```sh
  python h264tomp4.py --path <path_to_video_files>
  ```

## Contributing

[Contributions](Contributing.md) are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Remember to replace `<path_to_video_files>` with the actual path to the directory containing your video files. Also, if you have a license file, replace "MIT License" with the correct license for your project.
