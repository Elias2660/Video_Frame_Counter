# Video Frame Counter

This project includes a Python script (`converter.py`) for counting the frames in video files (`.h264` and `.mp4` formats) within a specified directory and outputs the counts to a CSV file (`counts.csv`).

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
python converter.py --path `<path_to_video_files>`
```

This will generate a counts.csv file in the specified directory containing the filenames and their corresponding frame counts.

## Contributing

(Contributions)[Contributing.md] are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Remember to replace `<path_to_video_files>` with the actual path to the directory containing your video files. Also, if you have a license file, replace "MIT License" with the correct license for your project.