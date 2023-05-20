import numpy as np

from mediapipe.tasks import python
from mediapipe.tasks.python.components import containers
from mediapipe.tasks.python import audio
from scipy.io import wavfile

class Classifier:

    def __init__(self, audio_file_name):
        self.audio_file_name = audio_file_name
        # Customize and associate model for Classifier
        self.base_options = python.BaseOptions(model_asset_path='classifier.tflite')
        self.options = audio.AudioClassifierOptions(
            base_options=self.base_options, max_results=4)

    def identify(self):
        # Create classifier, segment audio clips, and classify
        with audio.AudioClassifier.create_from_options(self.options) as classifier:
            sample_rate, wav_data = wavfile.read(self.audio_file_name)
            audio_clip = containers.AudioData.create_from_array(
            wav_data.astype(float) / np.iinfo(np.int16).max, sample_rate)
            classification_result_list = classifier.classify(audio_clip)

        results = {
             "Applause" : [],
             "Speech" : [],
             "Silence" : []
        }
        # Iterate through clips to display classifications
        for idx, timestamp in enumerate(range(len(classification_result_list))):
            classification_result = classification_result_list[idx]
            top_category = classification_result.classifications[0].categories[0]
            if top_category.category_name == "Speech":
                results["Speech"].append(timestamp)
            if top_category.category_name == "Applause":
                results["Applause"].append(timestamp)
            if top_category.category_name == "Silence":
                results["Silence"].append(timestamp)
            # if top_category.category_name in ['Speech', 'Applause', 'Silence']:
            #         results[timestamp] = (top_category.category_name)
                
        
        return results
        

