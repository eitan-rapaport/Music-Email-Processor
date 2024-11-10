# pylint: disable=missing-function-docstring,missing-module-docstring
# download:

# ffprobe.exe
# ffplay.exe
# ffmpeg.exe

#TODO: fix disk path

# to:
# C:\Users\eitan.rapaport\AppData\Local\Programs\Python\Python38-32\Scripts

# TODO: filter lists out

#!pip install cyrtranslit yt_dlp pydub

import argparse
import os
from multiprocessing import Pool
import logging as log
import MailDownloader
from classification_results import ClassificationResults
from audio_editor import *
from email_reader import *

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# TODO: change this to something current:
OUTPUT_PATH = "C:\\Users\\Eitan\\Music\\dev\\Handclap detection"
DEBUG = False

# Vars:
SILENCE_AT_BEGINNING_AND_END_MS = 3000

# Organize files
def configure_log():
    log.basicConfig(
    level=log.INFO,
    format='%(asctime)s,%(funcName)s,%(levelname)s,%(thread)d,%(message)s',
    handlers=[
        log.FileHandler(os.path.join(OUTPUT_PATH, "debug.log"),'a','utf-8'),
        log.StreamHandler()
        ]
    )


def parse_args():
    parser = argparse.ArgumentParser(
    description='Download Youtube videos as wav and mp4 and normalize them', prog='Download Youtube MP3')
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
    path = os.path.join(OUTPUT_PATH, folder)

    if os.path.exists(path):
        print('Folder exists')
    else:
        os.makedirs(path)
        print('Created folder ' + folder)
    os.chdir(path)


# Parse email

def download_files(arguments):
    urls = get_urls_in_email(log)
    MailDownloader.download_all_uris(urls, log, arguments.download_video)


def print_exceptions(exceptions):
    if len(exceptions['WAV']) > 0:
        log.error("### WAV Exceptions ###")
        for i in exceptions['WAV']:
            log.error(i)

    if len(exceptions['Video']) > 0:
        log.error("### Video Exceptions ###")
        for i in exceptions['Video']:
            log.error(i)


def apply_logic_to_file(file):
    filename = normalize_filename(file, log)
    filename = compress_file(filename, log)
    filename = normalize_audio_file(filename, log)
    filename = add_silence_to_file(filename, log)

# Main flows
def apply_main_logic():
    files = get_file_list()
    p = Pool(len(files))
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
    starting_seconds = [0,1,2,3,4,5,6]
    for cr in classification_results:
        res = [i for i in cr.applause if i in starting_seconds]
    return True


def main():
    arguments = parse_args()
    create_folder()
    configure_log()
    download_files(arguments)
    if arguments.debug:
        pass
        #apply_main_logic_sequential()
    else:
        apply_main_logic()
    classification_results = classify_all_audio_files_if_needed(arguments, log)
    remove_leading_handclaps(classification_results, arguments)
    convert_to_mp3(log)
    remove_clapping(classification_results, log)

#configuring the logging before the main function so every thread will have logging capabilities
configure_log()

if __name__ == "__main__":
    main()
