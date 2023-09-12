# 음악 파일 전처리 모듈

import numpy as np
import librosa
import json
import os
import shutil
import pickle
from math import *
import constants

class SongPreprocessor():
    def __init__(self):
        pass

    def set_output_path(self, output_path):
        self.output_path = output_path
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)

    def copy_song_to_output(self, song_path):
        song_title = song_path.split('\\')[-1].split('.')[0]
        shutil.copy2(song_path, self.output_path+'/'+song_title+'.egg')

    def extract_features_multi_mel(self, y, sr=44100.0, hop=512, nffts=[1024, 2048, 4096], mel_dim=100):
        featuress = []
        for nfft in nffts:
            mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=mel_dim, n_fft=nfft, hop_length=hop)  # C2 is 65.4 Hz
            features = librosa.power_to_db(mel, ref=np.max)
            featuress.append(features)
        features = np.stack(featuress, axis=1)
        return features

    def extract_features_mel(self, y, sr, hop, mel_dim=100):
        mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=mel_dim, hop_length=hop)  # C2 is 65.4 Hz
        features = librosa.power_to_db(mel, ref=np.max)
        return features

    def get_raw_binary_classes_reduced_tensors_from_level(self, notes, sequence_length, num_classes, bpm, sr, num_samples_per_feature, receptive_field):
        l = sequence_length
        ## BLOCKS TENSORS ##
        # variable `blocks` of shape (time steps, number of locations in the block grid), storing the class of block (as a number from 0 to 19) at each point in the grid, at each point in time
        # this variable is here only used to construct the blocks_reduced later; in the non-reduced representation dataset, it would be used directly.
        blocks = np.zeros((l, 12))
        # reduced state version of the above. The reduced-state "class" at each time is represented as a one-hot vector of size `self.opt.num_classes`
        blocks_reduced_classes = np.zeros((l, 1))

        unique_states = pickle.load(open("../data/statespace/sorted_states_ss_short.pkl","rb"))

        ## CONSTRUCT BLOCKS TENSOR ##
        for note in notes:
            # we add receptive_field because we padded the y with 0s, to imitate generation
            sample_index = receptive_field + floor((note['_time'] * 60 / bpm) * sr / num_samples_per_feature - 0.5)
            # check if note falls within the length of the song (why are there so many that don't??)
            if sample_index >= l:
                # print("note beyond the end of time")
                continue
            # constructing the representation of the block (as a number from 0 to 19)
            if note["_type"] == 3:
                note_representation = 19
            elif note["_type"] == 0 or note["_type"] == 1:
                note_representation = 1 + note["_type"] * 9 + note["_cutDirection"]
            else:
                raise ValueError("I thought there was no notes with _type different from 0,1,3. Ahem, what are those??")

            # print(note)
            try:
                blocks[sample_index, note["_lineLayer"] * 4 + note["_lineIndex"]] = note_representation
            except:
                continue  # some weird notes with too big or small lineLayer / lineIndex ??

        # convert blocks tensor to reduced_blocks using the dictionary `unique states` (reduced representation) provided by Ralph (loaded at beginning of file)
        for i, block in enumerate(blocks):
            if i < receptive_field:
                blocks_reduced_classes[i, 0] = constants.START_STATE
            elif i == len(blocks) - 1:
                blocks_reduced_classes[i, 0] = constants.END_STATE
            else:
                try:
                    state_index = unique_states.index(tuple(block))
                    if num_classes <= constants.NUM_SPECIAL_STATES + 1:
                        state_index = 0
                    blocks_reduced_classes[i, 0] = constants.NUM_SPECIAL_STATES + state_index
                except (ValueError,
                        IndexError):  # if not in top 2000 states, then we consider it the empty state (no blocks; class = 0)
                    blocks_reduced_classes[i, 0] = constants.EMPTY_STATE
        return blocks_reduced_classes

    def preprocess(self, song_path, feature_name='multi_mel', feature_size=80, sampling_rate=44100.0, step_size=0.01):
        
        song_title = song_path.split('\\')[-1].split('.')[0]+'.egg'
        feature_path = self.output_path+'/'+song_title+'_'+feature_name+'_'+str(feature_size)+'.npy'

        # get song
        y_wav, sr = librosa.load(song_path, sr=sampling_rate)

        sr = sampling_rate
        hop = int(sr * step_size)

        #get feature
        if feature_name == "mel":
            features = self.extract_features_mel(y_wav, sr, hop, mel_dim=feature_size)
        elif feature_name == "multi_mel":
            features = self.extract_features_multi_mel(y_wav, sr=sampling_rate, hop=hop, nffts=[1024,2048,4096], mel_dim=feature_size)

        np.save(feature_path, features)

        return feature_path
    
    def block_reduced(self, song_path, feature_path, level_path, sampling_rate=44100.0, step_size=0.01):
        song_title = song_path.split('\\')[-1].split('.')[0]+'.egg'
        song_diff = level_path.split('\\')[-1].split('.')[0]
        blocks_reduced_classes_file = self.output_path+'/'+song_title+song_diff+'_blocks_reduced_classes_.npy'
        receptive_field = 1

        sr = sampling_rate
        hop = int(sr * step_size)

        y = np.load(feature_path)
        sequence_length = y.shape[-1]

        level = json.load(open(level_path, 'r'))
        notes = level['_notes']
        bpm = level['_beatsPerMinute']

        # print(notes)

        blocks_reduced_classes = self.get_raw_binary_classes_reduced_tensors_from_level(notes, sequence_length, 5, bpm, sr, hop, receptive_field)
        np.save(blocks_reduced_classes_file,blocks_reduced_classes)

# 하단의 코드는 이 파일을 단독으로 실행할 경우만 사용됨
OUTPUT_DIR = "./ssdsconverter_output"

if __name__ == '__main__':
    preprocessor = SongPreprocessor()
    preprocessor.set_output_path(OUTPUT_DIR)
    song_path = '../SuperStarResource/json/SSJ/1to10.ogg'
    feature_path = preprocessor.preprocess(song_path)
    preprocessor.block_reduced(song_path, feature_path, '../deepsaber-master/scripts/data/extracted_data/SSJ_1to10/Expert.dat')
