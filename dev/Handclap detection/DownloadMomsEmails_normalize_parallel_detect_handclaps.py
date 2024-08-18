# download:

# ffprobe.exe
# ffplay.exe
# ffmpeg.exe

#TODO: fix disk path

# to:
# C:\Users\eitan.rapaport\AppData\Local\Programs\Python\Python38-32\Scripts

# TODO: filter lists out

#!pip install cyrtranslit yt_dlp pydub numpy mediapipe

from pydub import AudioSegment
from pydub.effects import normalize
from pydub.effects import compress_dynamic_range
import re
import __future__
import os
import io
import argparse
from multiprocessing import Pool
import cyrtranslit
import glob
import logging as log
import MailDownloader
from google_classifier import Classifier


output_path = "C:\\Users\\Eitan\\Music\\dev\\Handclap detection"


# Vars:
SILENCE_AT_BEGINNING_AND_END_MS = 3000


def create_folder():
    folder = input("Please choose the folder name: ")
    path = os.path.join(output_path, folder)

    if os.path.exists(path):
        print('Folder exists')
        
    else:
        os.makedirs(path)
        print('Created folder ' + folder)

    os.chdir(path)


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

        
def normalize_all_filenames():
    files = get_file_list()
    log.info("3. Normalizing all file names")
    for file in files:
        normalize_filename(file)


def normalize_filename(file):
    if not file.endswith('.wav'):
        return

    log.info("3.1 Normalizing {0}".format(file))
    #fix cyrillic characters
    new_name = re.sub('\W+', ' ', cyrtranslit.to_latin(file, "ru"))
    new_name = re.sub(' wav', ".wav", new_name)
    os.replace(file, new_name)
    log.info("3.2 Replaced. Old file name: {0}, New file name: {1}".format(file, new_name))
    return new_name


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

        log.info("Deleting " + file)
        os.remove(file)

        log.info(f"4.2 Compressed {new_file}")
        return new_file


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

        log.info("Deleting " + file)
        os.remove(file)   
        log.info(f"5.2 Normalized {new_file}")     
        return new_file


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

    log.info("Deleting " + file)
    os.remove(file)

    log.info(f"6.2 Added silence to {new_file}")
    return new_file


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
    return glob.glob("*.wav")
    

def convert_to_mp3():
    files = get_file_list()
    for file in files:
        audio = AudioSegment.from_wav(file)
        filename = file.replace("wav","mp3")
        audio.export(filename,format='mp3')

    
        log.info("Deleting " + file)
        os.remove(file)   


def configure_log():
    log.basicConfig(
    level=log.INFO,
    format='%(asctime)s,%(funcName)s,%(levelname)s,%(message)s',
    handlers=[
        log.FileHandler("debug.log"),
        log.StreamHandler()
        ]
    )


def remove_clapping(classification_results):
    #BUG: it seems that the classifier is sometimes returning indexes of Silent\Applause\Speech that are 
    # bigger than file length. e.g: "Tchaikovsky Waltz from Sleeping Beauty"
    # File length 293 seconds. Silence indexes: [0, 1, 2, 294, 295, 296, 297, 298, 299, 300]
    for file, results in classification_results.items():
        if len(results["Applause"]) >= 2:
            log.info(f"{file} has more than 3 seconds of applause")

def classify_single_audio_file(audio_file):
    classifier = Classifier(audio_file)
    return classifier.identify()


def classify_all_audio_files_if_needed(arguments):
    classification_results = {}
    if arguments.no_classification == False:
        files = get_file_list()
        log.info("7.1 CLASSIFYING FILES")
        for i in range(len(files)):
            results = classify_single_audio_file(files[i])
            audio = AudioSegment.from_file(files[i])
            file_length = audio.duration_seconds
            results["File Length"] = file_length
            classification_results[files[i]] = results
        log.info("7.2 END CLASSIFYING")
        log_classification_results(classification_results)
    return classification_results


def log_classification_results(classification_results):
    for filename,results in classification_results.items():
        log.info("""Timestamps classification results for {0}:
                    Applause: {1}
                    Silence: {2}
                    Speech: {3}
                    File Length: {4}""".format(filename, results["Applause"], results["Silence"], results["Speech"],
                                               results["File Length"]))


def download_files(arguments):
    email_content = read_email()
    urls = find_urls_in_email(email_content)
    print_found_urls(urls)
    MailDownloader.download_all_uris(urls, log, arguments.download_video)


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

    return parser.parse_args()


def apply_logic_to_file(file):
    filename = normalize_filename(file)
    filename = compress_file(filename)
    filename = normalize_audio_file(filename)
    filename = add_silence_to_file(filename)


def apply_main_logic():
    files = get_file_list()
    p = Pool(len(files))
    p.map(apply_logic_to_file, files)
    p.close()
    p.join()

def main():
    arguments = parse_args()
    # create_folder()
    # download_files(arguments)
    # apply_main_logic()
    os.chdir("C:\\Users\\Eitan\\Music\\dev\\Handclap detection\\test")
    classification_results = classify_all_audio_files_if_needed(arguments)
    #convert_to_mp3()
    remove_clapping(classification_results)
    #print_exceptions(exceptions)

#configuring the logging before the main function so every thread will have logging capabilities
configure_log()

if __name__ == "__main__":
    main()
