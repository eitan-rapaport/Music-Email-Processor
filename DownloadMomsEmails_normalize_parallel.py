# download:

# ffprobe.exe
# ffplay.exe
# ffmpeg.exe

# to:
# C:\Users\eitan.rapaport\AppData\Local\Programs\Python\Python38-32\Scripts

# TODO: filter lists out

from pydub import AudioSegment
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

# Vars:
SILENCE_AT_BEGINNING_AND_END_MS = 3000

parser = argparse.ArgumentParser(
    description='Download Youtube videos as mp3 and mp4 and normalize them', prog='Download Youtube MP3')
parser.add_argument('--download-video', action='store_true', default=False,
                    help="Download the video")
parser.add_argument('--keep-original', action='store_true', default=False,
                    help="Keep the not normalized mp3 file")

args = parser.parse_args()

print(args)
output_path = path.join(os.environ['USERPROFILE'], "Music\\disk")
exceptions = {'Video': [], 'MP3': []}

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
}
ydl_video = {
    'format': 'best',
}
    

def create_folder(path):
    folder = input("Please choose the folder name: ")
    path = os.path.join(output_path, folder)

    if os.path.exists(path):
        print('Folder exists')
        os.chdir(path)
    else:
        os.makedirs(path)
        print('Created folder ' + folder)
        os.chdir(path)


def download(link):
    # Download audio
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
    except Exception as e:
        print("Exception while downloading MP3!")
        print(e)
        exceptions['MP3'].append(link)

    # Download Video
    if args.download_video == True:
        try:
            with yt_dlp.YoutubeDL(ydl_video) as ydl:
                ydl.download([link])
        except Exception as e:
            print("Exception while downloading Video!")
            print(e)
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
    print("### MP3 Exceptions ###")
    for i in exceptions['MP3']:
        print(i)

    print("### Video Exceptions ###")
    for i in exceptions['Video']:
        print(i)

def print_found_urls(urls):
    print("1. Found the following URIs, {0} in total:".format(len(urls)))
    for i in urls:
        print(i)

    print()

def download_all_uris(urls):
    print("2. Downloading URLs")
    with Pool() as pool:
        try:
            pool.map(download, urls)
        except Exception as e:
            print("Encountered exception: ", e, "for file: ", urls)
            traceback.print_exc(file=sys.stdout)
    print("2. Finished downloading")
        
def normalize_all_filenames(files):
    print("3. Normalizing all file names")
    for file in files:
        normalize_filename(file)

def normalize_filename(file):
    if not file.endswith('.mp3'):
        return

    print("3.1 Normalizing {0}".format(file))
    new_name = re.sub('\W+', ' ', cyrtranslit.to_latin(file, "ru"))
    new_name = re.sub(' mp3', ".mp3", new_name)
    os.replace(file, new_name)
    print("3.1 Replaced. Old file name: {0}, New file name: {1}".format(file, new_name))

def compress_all_files(files):
    print(f"4. Compressing all files")
    with Pool() as pool:
        pool.map(compress_file, files)
    print("4. Finished compressing")


def compress_file(file):
    if not file.endswith('.mp3'):
        pass
    else:
        print(f'4.1 Compressing: -- {file}')
        raw_sound = AudioSegment.from_file(file)
        compressed_sound = compress_dynamic_range(raw_sound, -20, 6)
        new_file = re.sub("\.mp3", "_C.mp3", file)
        compressed_sound.export(new_file , format='mp3')

        if args.keep_original == False:
            print("Deleting " + file)
            os.remove(file)

        print(f"4.1 Compressed {new_file}")


def normalize_all_audio_files(files):
    print("5. Normalizing files...")
    with Pool() as pool:
        pool.map(normalize_audio_file, files)
    print("5. Finished normalizing")


def normalize_audio_file(file):
    if not file.endswith('.mp3'):
        pass

    else:
        print(f"5.1 Normalizing {file}")
        raw_sound = AudioSegment.from_file(file)
        normalized_file = normalize(raw_sound, -1)
        new_file = re.sub("\.mp3", "N.mp3", file)
        normalized_file.export(new_file, format='mp3')

        if args.keep_original == False:
            print("Deleting " + file)
            os.remove(file)   
        print(f"5.1 Normalized {new_file}")     


def add_ms_of_silence_to_all_files(files):
    print("6. Add silence to files")
    with Pool() as pool:
        pool.map(add_silence_to_file, files)
    print("6. Finished adding silence ")


def add_silence_to_file(file):
    print(f"6.1 Adding silence to file {file}")
    raw_sound = AudioSegment.from_file(file)
    sample = raw_sound[:SILENCE_AT_BEGINNING_AND_END_MS]
    sample = sample - 70
    output = sample + raw_sound + sample
    new_file = re.sub("\.mp3", "S.mp3", file)
    output.export(new_file, format='mp3')

    if args.keep_original == False:
        print("Deleting " + file)
        os.remove(file)

    print(f"6.1 Added silence to {new_file}")


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
    print("Getting file list")
    files = glob.glob("*.mp3")
    print(files)
    return files


def main():
    create_folder(path)
    email_content = read_email()
    urls = find_urls_in_email(email_content)
    print_found_urls(urls)
    download_all_uris(urls)
    file_list = get_file_list()
    normalize_all_filenames(file_list)
    file_list = get_file_list()
    compress_all_files(file_list)
    file_list = get_file_list()
    normalize_all_audio_files(file_list)
    file_list = get_file_list()
    add_ms_of_silence_to_all_files(file_list)
    print_exceptions(exceptions)


if __name__ == '__main__':
    main()
