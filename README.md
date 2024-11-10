# YouTube Audio and Video Downloader with Processing

This Python script downloads YouTube videos, processes audio and video files by normalizing, compressing, and adding silence to them. The script also classifies audio segments, removes unwanted sounds like applause, and converts the processed audio files into MP3 format.

## Requirements

Before running this script, ensure you have the following dependencies installed:

### Dependencies

- **Python 3.8+**  
  (Note: The script assumes Python 3.8-32 bit version as it's designed for this environment)
  
- **Required Software**  
  - `ffprobe.exe`, `ffplay.exe`, `ffmpeg.exe` (Make sure these executables are available in your system’s `Scripts` directory. The default directory for 32-bit Python is `%appdata%\Local\Programs\Python\Python38-32\Scripts`.)

- **Python Libraries**  
  The following libraries need to be installed via `pip`:
  
  ```bash
  pip install cyrtranslit yt_dlp pydub
  ```

  These libraries are used for downloading content from YouTube (`yt_dlp`), handling audio files (`pydub`), and transliteration (`cyrtranslit`).

## Features

- **Download Videos**  
  Download YouTube videos as `.mp4` files, and audio as `.wav` files.

- **Normalize and Compress Audio**  
  The audio files are normalized, compressed, and edited with silence added at the beginning and end to improve listening quality.

- **Classify Audio Sections**  
  Audio is classified into different segments (if the classification flag is enabled).

- **WIP: Remove Unwanted Sounds**  
  The script can remove specific sounds (e.g., handclaps) from the beginning of audio files if enabled.

- **Convert to MP3**  
  After processing, audio files are converted to MP3 format.

## How to Use

### Running the Script

To run the script, execute the following command:

```bash
python download_and_process.py [OPTIONS]
```

### Command Line Options

- `--download-video`  
  Download the video along with the audio (default is to only download audio).

- `--keep-original`  
  Keep the original `.wav` file (not normalized). Without this option, the script will overwrite the `.wav` file with a normalized version.

- `--no-edit`  
  Disable audio editing (compression, normalization, adding silence).

- `--no-classification`  
  Skip the audio classification process, which can improve performance.

- `--debug`  
  Enable debugging. This option does not apply the main audio processing logic (e.g., normalization, compression).

### Example Usage

```bash
python download_and_process.py --download-video --keep-original --debug
```

This command will:
- Download the video
- Keep the original `.wav` file
- Enable debugging mode (skipping normal processing)

### Folder Creation

When the script is run, it will prompt you to choose a folder name. This folder will be created inside the `OUTPUT_PATH` directory (current folder by default), and the files will be saved there.

### Log File

The script generates logs and saves them to `debug.log` in the output folder. It also prints logs to the console.

## File Processing Flow

1. **Folder Setup**:  
   The script asks the user to specify a folder name and creates it in the output directory.

2. **File Download**:  
   The script fetches YouTube video URLs from email and downloads them.

3. **File Processing**:  
   After the download, the files are processed using the following steps:
   - Filename normalization
   - Audio compression
   - Normalization of audio
   - Addition of silence at the beginning and end

   File names will have the following characters inserted along their journey within the software:
   - C -> As in Compressed
   - N -> Normalized
   - S -> Added silence padding

4. **Audio Classification**:  
   The audio is classified into different segments (if classification is enabled).

5. **MP3 Conversion**:  
   The processed audio is converted into MP3 format.

6. **WIP: Clapping Removal**:  
   If enabled, the script will remove leading handclaps detected at the beginning of the audio.

## Configuration

- **Output Path**:  
  The `OUTPUT_PATH` variable is set to current directory. Change it to your preferred directory if needed.

- **Silence Padding**:  
  `SILENCE_AT_BEGINNING_AND_END_MS` defines the duration of silence (in milliseconds) to be added at the beginning and end of the audio files. The default is set to 3000 ms.

## Error Handling

The script logs any errors encountered during processing. It handles different types of errors related to WAV and video files and will log them accordingly.

## License

This project is open-source and available under the MIT License.

---

This `README.md` provides detailed instructions on how to use the script, dependencies required, and a description of the various options and file processing flow.