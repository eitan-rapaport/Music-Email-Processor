from pydub import AudioSegment
from pydub import effects
import os
import re

os.chdir("disk\\test")
file = ' BEST OF Velikij E mil Gilel s IV S Raxmaninov Margaritki UJ4o5NcMUOA_normalized.mp3'
new_file = re.sub("\.mp3", "", file)
empty_file = AudioSegment.empty()
aud = AudioSegment.from_file(' BEST OF Velikij E mil Gilel s IV S Raxmaninov Margaritki UJ4o5NcMUOA_normalized.mp3')
file_len_in_ms = len(aud)

def add_seconds_of_quiet(file, len_ms):
    sample = file[:len_ms]
    sample = sample - 70
    return sample + file + sample

def main():
    export_file = effects.compress_dynamic_range(aud, -20, 2.5)
    export_file = effects.normalize(export_file, -1)
    export_file = add_seconds_of_quiet(export_file, 3000)
    export_file.export(new_file + "_normalizerTEsTDynaMicRanGE-20,2.5.mp3", format='mp3')

if __name__ == "__main__":
    main()


