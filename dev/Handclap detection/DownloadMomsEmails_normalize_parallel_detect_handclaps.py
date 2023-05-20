# download:

# ffprobe.exe
# ffplay.exe
# ffmpeg.exe

#TODO: fix disk path

# to:
# C:\Users\eitan.rapaport\AppData\Local\Programs\Python\Python38-32\Scripts

# TODO: filter lists out

#!pip install cyrtranslit yt_dlp pydub

from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from pydub.effects import normalize
from pydub.effects import compress_dynamic_range
import re
import yt_dlp
import __future__
from os import path
import os
import io
import argparse
from multiprocessing import Pool
import traceback
import sys
import cyrtranslit
import glob
import logging as log




# Vars:
SILENCE_AT_BEGINNING_AND_END_MS = 3000
APPLAUSE = "Applause"

parser = argparse.ArgumentParser(
    description='Download Youtube videos as wav and mp4 and normalize them', prog='Download Youtube MP3')
parser.add_argument('--download-video', action='store_true', default=False,
                    help="Download the video")
parser.add_argument('--keep-original', action='store_true', default=True,
                    help="Keep the not normalized wav file")
parser.add_argument('--no-edit', action='store_true', default=False,
                    help="disable adding silence, compressing and normalizing")
parser.add_argument('--no-classification', action='store_true', default=False,
                    help='Do not classify the audio parts in sections. Will help performance')
parser.add_argument('--download-mp3', action='store_true', default=False,
                    help='Download the files as MP3 instead of WAV. Feature not completely ready')

args = parser.parse_args()

if args.no_classification == False:
    from google_classifier import Classifier

print(args)
output_path = "C:\\Users\\Eitan\\Music\\dev\\Handclap detection"
exceptions = {'Video': [], 'WAV': []}

if args.download_mp3 == True:
    preferred_codec = 'mp3'
else:
    preferred_codec = 'wav'

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': preferred_codec,
        'preferredquality': '320',
    }],
}
ydl_video = {
    'format': 'best',
}

classification_results = {}
    

def create_folder(path):
    folder = input("Please choose the folder name: ")
    path = os.path.join(output_path, folder)

    if os.path.exists(path):
        print('Folder exists')
        
    else:
        os.makedirs(path)
        print('Created folder ' + folder)

    os.chdir(path)

def download(link):
    # Download audio
    log.info(f"Downloading {link}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
    except Exception as e:
        log.error(f"Exception while downloading WAV for {link}", exc_info=e)
        log.error(e)
        exceptions['WAV'].append(link)

    # Download Video
    if args.download_video == True:
        try:
            with yt_dlp.YoutubeDL(ydl_video) as ydl:
                ydl.download([link])
        except Exception as e:
            log.error(f"Exception while downloading Video for {link}", exc_info=e)
            log.error(e)
            exceptions['Video'].append(link)


def parse_email(mail):
    try:
        url = re.match("(https?://[^\s]+)", mail).group(0)
        url = re.sub("&list=.*", "", url)
        return url
    except:
        pass


def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)


def print_exceptions(exceptions):
    if len(exceptions['WAV']) > 0:
        log.error("### WAV Exceptions ###")
        for i in exceptions['WAV']:
            log.error(i)

    if len(exceptions['Video']) > 0:
        log.error("### Video Exceptions ###")
        for i in exceptions['Video']:
            log.error(i)

def print_found_urls(urls):
    log.info("1. Found the following URIs, {0} in total:".format(len(urls)))
    for i in urls:
        log.info(i)

def download_all_uris(urls):
    log.info("2. Downloading URLs")
    with Pool() as pool:
        try:
            pool.map(download, urls)
        except Exception as e:
            log.error("Encountered exception: ", e, "for file: ", urls)
            traceback.print_exc(file=sys.stdout)
    log.info("2. Finished downloading")
        
def normalize_all_filenames(files):
    files = get_file_list()
    log.info("3. Normalizing all file names")
    for file in files:
        normalize_filename(file)

def normalize_filename(file):
    if not file.endswith('.wav'):
        return

    log.info("3.1 Normalizing {0}".format(file))
    new_name = re.sub('\W+', ' ', cyrtranslit.to_latin(file, "ru"))
    new_name = re.sub(' wav', ".wav", new_name)
    os.replace(file, new_name)
    log.info("3.1 Replaced. Old file name: {0}, New file name: {1}".format(file, new_name))

def compress_all_files():
    files = get_file_list()
    log.info(f"4. Compressing all files")
    with Pool() as pool:
        pool.map(compress_file, files)
    log.info("4. Finished compressing")


def compress_file(file):
    if not file.endswith('.wav'):
        pass
    else:
        log.info(f'4.1 Compressing: -- {file}')
        raw_sound = AudioSegment.from_file(file)
        compressed_sound = compress_dynamic_range(raw_sound, -20, 6)
        new_file = re.sub("\.wav", "_C.wav", file)
        compressed_sound.export(new_file , format='wav')

        if args.keep_original == False:
            log.info("Deleting " + file)
            os.remove(file)

        log.info(f"4.1 Compressed {new_file}")


def normalize_all_audio_files():
    files = get_file_list()
    log.info("5. Normalizing files...")
    with Pool() as pool:
        pool.map(normalize_audio_file, files)
    log.info("5. Finished normalizing")


def normalize_audio_file(file):
    if not file.endswith('.wav'):
        pass

    else:
        log.info(f"5.1 Normalizing {file}")
        raw_sound = AudioSegment.from_file(file)
        normalized_file = normalize(raw_sound, -1)
        new_file = re.sub("\.wav", "N.wav", file)
        normalized_file.export(new_file, format='wav')

        if args.keep_original == False:
            log.info("Deleting " + file)
            os.remove(file)   
        log.info(f"5.1 Normalized {new_file}")     


def add_ms_of_silence_to_all_files():
    files = get_file_list()
    log.info("6. Add silence to files")
    with Pool() as pool:
        pool.map(add_silence_to_file, files)
    log.info("6. Finished adding silence ")


def add_silence_to_file(file):
    log.info(f"6.1 Adding silence to file {file}")
    raw_sound = AudioSegment.from_file(file)
    sample = raw_sound[:SILENCE_AT_BEGINNING_AND_END_MS]
    sample = sample - 70
    output = sample + raw_sound + sample
    new_file = re.sub("\.wav", "S.wav", file)
    output.export(new_file, format='wav')

    if args.keep_original == False:
        log.info("Deleting " + file)
        os.remove(file)

    log.info(f"6.1 Added silence to {new_file}")


def read_email():
    email_content = []
    print("Paste the email below:")
    try:
        while(True):
            line = input()
            email_content.append(line)
    except KeyboardInterrupt as e:
        pass

    return email_content


def parse_all_email_lines(email_content):
    urls = []

    for line in email_content:
        with io.open('email.txt', 'a', encoding='utf-8') as f:
            f.write(line + "\n")
        urls.append(parse_email(line))

    return urls


def find_urls_in_email(email_content):
    urls = parse_all_email_lines(email_content)
    urls = list(filter(None, urls))
    return urls


def get_file_list():
    log.info("Getting file list")
    files = glob.glob("test\*.wav")
    log.info(files)
    return files

def configure_log():
    log.basicConfig(
    level=log.INFO,
    format='%(asctime)s,%(funcName)s,%(levelname)s,%(message)s',
    handlers=[
        log.FileHandler("debug.log"),
        log.StreamHandler()
        ]
    )

def remove_clapping(file_list):
    audio = AudioSegment.from_wav(file_list[0])
    min_silence_len = 1000  # minimum silence length in milliseconds
    silence_thresh = -50  # silence threshold in dBFS
    non_silent_parts = detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    audio_no_claps = AudioSegment.silent(duration=0)
    for start, end in non_silent_parts:
        audio_no_claps += audio[start:end]


def classify_single_audio_file(audio_file):
    log.info(f"Got {audio_file}")
    
    classifier = Classifier(audio_file)
    return classifier.identify()


def classify_all_audio_files():
    files = get_file_list()
    log.info("7. CLASSIFYING FILES")
    for i in range(len(files)):
        results = classify_single_audio_file(files[i])
        classification_results[files[i]] = results
    log.info("7. END CLASSIFYING")


def log_classification_results():
    for filename,results in classification_results.items():
        log.info("""Timestamps classification results for {0}:
                    Applause: {1}
                    Silence: {2}
                    Speech: {3}""".format(filename, results["Applause"], results["Silence"], results["Speech"]))



def main():
    # create_folder(path)
    configure_log()
    # email_content = read_email()
    # urls = find_urls_in_email(email_content)
    # print_found_urls(urls)
    # download_all_uris(urls)
    print(args.no_classification)
    # compress_all_files()

    # normalize_all_audio_files()
    # add_ms_of_silence_to_all_files()
    if args.no_classification == False:
        classify_all_audio_files()
    log_classification_results()
    # print_exceptions(exceptions)
    #remove_clapping(file_list)


if __name__ == "__main__":
    main()
