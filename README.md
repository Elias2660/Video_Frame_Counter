# Video Frame Counter

This project includes Python scripts for counting and converting video files (`.h264` and `.mp4`) and generating `counts.csv`. It is most used with the [Unified-bee-Runner](https://github.com/Elias2660/Unified-bee-Runner).

## Installation

1. Clone this repository:  
   ```sh  
   git clone https://github.com/Elias2660/VideoFrameCounter.git  
   cd VideoFrameCounter  
   ```

2. Create and activate a virtual environment:  
   ```sh  
   python3 -m venv venv  
   source venv/bin/activate    # On Windows: venv\Scripts\activate  
   ```

3. Install dependencies:  
   ```sh  
   pip install -r requirements.txt  
   ```

## Usage

Count frames in video files:  
```sh  
python make_counts.py --video-filepath <path_to_videos> --output-filepath <path_for_counts>  
```

Generates `counts.csv` in the specified output directory.

## Available Scripts

- **make_counts.py**: Count frames per video and generate `counts.csv`.  
  ```sh  
  python make_counts.py --video-filepath <path> --output-filepath <path>  
  ```

- **optimized_make_counts.py**: Fast metadata-based frame count.  
  ```sh  
  python optimized_make_counts.py --video-filepath <path> --output-filepath <path>  
  ```
  
- **h264tomp4.py**: Convert `.h264` to `.mp4` and count frames.  
  ```sh  
  python h264tomp4.py --video-filepath <path> --output-filepath <path>  
  ```

## Contributing

Contributions are welcome! See [Contributing.md](Contributing.md).

## License

Licensed under the MIT License. See [LICENSE](LICENSE).

## Security

Review our [Security Policy](SECURITY.md) for reporting issues.
