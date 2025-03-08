# pylint: disable=missing-function-docstring,missing-module-docstring
# download:

# ffprobe.exe
# ffplay.exe
# ffmpeg.exe

# to:
# %appdata%\Local\Programs\Python\Python38-32\Scripts

#!pip install cyrtranslit yt_dlp pydub

from typing import List
import argparse
import os
from multiprocessing import Pool
import logging as log
import mail_downloader
from classification_results import ClassificationResults
from audio_editor import classify_all_audio_files_if_needed, convert_to_mp3
from audio_editor import compress_file, normalize_audio_file, add_silence_to_file
from audio_editor import shorten_file
from file_manager import get_file_list, normalize_filename
#os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' // disable annoying error by TF on import
from email_reader import get_urls_in_email
from file_info import FileInfo


# Vars:
SILENCE_AT_BEGINNING_AND_END_MS = 3000

# Organize files
def configure_log():
    log.basicConfig(
    level=log.INFO,
    format='%(asctime)s,%(funcName)s,%(levelname)s,%(thread)d,%(message)s',
    handlers=[
        log.FileHandler(os.path.join(os.getcwd(), "debug.log"),'a','utf-8'),
        log.StreamHandler()
        ]
    )


def parse_args():
    parser = argparse.ArgumentParser(
    description='Download Youtube videos as wav and mp4 and normalize them',
    prog='Download Youtube MP3')
    parser.add_argument('--download-video', action='store_true', default=False,
                        help="Download the video")
    parser.add_argument('--keep-original', action='store_true', default=False,
                        help="Keep the not normalized wav file")
    parser.add_argument('--no-edit', action='store_true', default=False,
                        help="disable adding silence, compressing and normalizing")
    parser.add_argument('--no-classification', action='store_true', default=False,
                        help='Do not classify the audio parts in sections. Will help performance')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Debug configuration')

    return parser.parse_args()


def create_folder():
    folder = input("Please choose the folder name: ")
    path = os.path.join(os.getcwd(), folder)

    if os.path.exists(path):
        print('Folder exists')
    else:
        os.makedirs(path)
        print('Created folder ' + folder)
    os.chdir(path)


# Parse email

def download_files(arguments):
    urls_and_end_timestamps = get_urls_in_email(log)
    downloaded_files = mail_downloader.download_all_uris(
        urls_and_end_timestamps, log, arguments.download_video)
    return downloaded_files


def apply_logic_to_file(file):
    configure_log()
    global SILENCE_AT_BEGINNING_AND_END_MS
    log.info("Starting main logic")
    filename = normalize_filename(file, log)
    filename = compress_file(filename, log)
    filename = normalize_audio_file(filename, log)
    filename = add_silence_to_file(filename, log)
    log.info("Finished main logic")

# Main flows
def apply_main_logic():
    files = get_file_list()
    num_of_files = len(files)
    log.info("Creating %i threads", num_of_files)
    with Pool(num_of_files) as p:
        p.map(apply_logic_to_file, files)
        p.close()
        p.join()


def apply_main_logic_sequential():
    files = get_file_list()
    for file in files:
        apply_logic_to_file(file)


def remove_leading_handclaps(classification_results: list[ClassificationResults], arguments):
    if not arguments.debug:
        return
    #starting_seconds = [0,1,2,3,4,5,6]
    for cr in classification_results:
        #res = [i for i in cr.applause if i in starting_seconds]
        pass
    return True


def get_file_from_list(file: str, files: List[str]):
    for f in files:
        if f.startswith(file):
            return f

def remove_marked_areas(files: List[FileInfo]):
    for file in files:
        try:
            if file.end_timestamp == 0:
                continue
            shorten_file(file.name, file.end_timestamp, log)
        except Exception as e:
            log.error(f"Failed to download {file.name} because of error", exc_info=e)


def main():
    arguments = parse_args()
    create_folder()
    configure_log()
    downloaded_files = download_files(arguments)
    remove_marked_areas(downloaded_files)
    if arguments.debug:
        pass
        #apply_main_logic_sequential()
    else:
        apply_main_logic()
    classification_results = classify_all_audio_files_if_needed(arguments, log)
    remove_leading_handclaps(classification_results, arguments)
    convert_to_mp3(log)

#configuring the logging before the main function so every thread will have logging capabilities

if __name__ == "__main__":
    main()
