import numpy as np
import librosa
from pathlib import Path
import json
import os.path
import os
import sys
import argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(os.path.join(THIS_DIR, os.pardir), os.pardir))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
EXTRACT_DIR = os.path.join(DATA_DIR, 'extracted_data')
if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)
if not os.path.isdir(EXTRACT_DIR):
    os.mkdir(EXTRACT_DIR)
sys.path.append(ROOT_DIR)
from scripts.feature_extraction.feature_extraction import extract_features_hybrid, extract_features_mel,extract_features_hybrid_beat_synced, extract_features_multi_mel

from scripts.feature_extraction.feature_extraction import extract_features_hybrid, extract_features_mel,extract_features_hybrid_beat_synced, extract_features_multi_mel

parser = argparse.ArgumentParser(description="Preprocess songs data")

parser.add_argument("--data_path", type=str,default="../../../data/extracted_data", help="Directory contining Beat Saber level folders")
parser.add_argument("--difficulties", type=str, default="Expert",help="Comma-separated list of difficulties to process (e.g. \"Expert,Hard\"")
parser.add_argument("--feature_name", metavar='', type=str, default="multi_mel", help="mel, chroma, multi_mel")
parser.add_argument("--feature_size", metavar='', type=int, default=80)
parser.add_argument("--sampling_rate", metavar='', type=float, default=44100.0)
parser.add_argument("--beat_subdivision", metavar='', type=int, default=16)
parser.add_argument("--step_size", metavar='', type=float, default=0.01)
parser.add_argument("--replace_existing", action="store_true")
parser.add_argument("--using_bpm_time_division", action="store_true")

args = parser.parse_args()

# makes arugments into global variables of the same name, used later in the code
#globals().update(vars(args))
data_path = Path(args.data_path)


## distributing tasks accross nodes ##
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
print(rank)
print("creating {} of size {}".format(args.feature_name, args.feature_size))

#assuming egg sound format, as used in new BeatSaber format
candidate_audio_files = sorted(data_path.glob('**/*.egg'), key=lambda path: path.parent.__str__())

#candidate_audio_files = sorted(data_path.glob('**/*.egg'), key=lambda path: path.parent.__str__())
num_tasks = len(candidate_audio_files)
num_tasks_per_job = num_tasks//size
tasks = list(range(rank*num_tasks_per_job,(rank+1)*num_tasks_per_job))
if rank < num_tasks%size:
    tasks.append(size*num_tasks_per_job+rank)

for i in tasks:
    path = candidate_audio_files[i]
    song_file_path = path.__str__()
    # feature files are going to be saved as numpy files
    features_file = song_file_path+"_"+args.feature_name+"_"+str(args.feature_size)+".npy"

    level_file_found = False
    
    # find level files with target difficulties that exist
    for diff in args.difficulties.split(","):
        if Path(path.parent.__str__()+"/"+diff+".dat").is_file():
            level = list(path.parent.glob('./'+diff+'.dat'))[0]
            level = level.__str__()
            #info_file = list(path.parent.glob('./info.dat'))[0]
            #info_file = info_file.__str__()
            level_file_found = True
    if not level_file_found:
        continue

    if args.replace_existing or not os.path.isfile(features_file):
        print("creating feature file",i)
        # get level
        level = json.load(open(level, 'r'))
        #info = json.load(open(info_file, 'r'))

        # get song
        print(song_file_path)
        y_wav, sr = librosa.load((song_file_path), sr=args.sampling_rate)

        bpm = level['_beatsPerMinute']
        sr = args.sampling_rate
        hop = int(sr * args.step_size)

        #get feature
        if args.feature_name == "chroma":
            if args.using_bpm_time_division:
                state_times = np.arange(0,y_wav.shape[0]/sr,step=args.step_size)
                features = extract_features_hybrid_beat_synced(y_wav,sr,state_times,bpm,beat_discretization=1/args.beat_subdivision)
            else:
                features = extract_features_hybrid(y_wav,sr,hop)
        elif args.feature_name == "mel":
            if args.using_bpm_time_division:
                raise NotImplementedError("Mel features with beat synced times not implemented, but trivial TODO")
            else:
                features = extract_features_mel(y_wav,sr,hop,mel_dim=args.feature_size)
        elif args.feature_name == "multi_mel":
            if args.using_bpm_time_division:
                raise NotImplementedError("Mel features with beat synced times not implemented, but trivial TODO")
            else:
                features = extract_features_multi_mel(y_wav, sr=args.sampling_rate, hop=hop, nffts=[1024,2048,4096], mel_dim=args.feature_size)

        np.save(features_file,features)


















































'''
for i in tasks:
    path = candidate_audio_files[i]
    song_file_path = path.__str__()
    # feature files are going to be saved as numpy files
    features_file = song_file_path+"_"+args.feature_name+"_"+str(args.feature_size)+".npy"

    level_file_found = False
    
    # find level files with target difficulties that exist
    for diff in args.difficulties.split(","):
        if Path(path.parent.__str__()+"/"+diff+".dat").is_file():
            level = list(path.parent.glob('./'+diff+'.dat'))[0]
            level = level.__str__()
            info_file = list(path.parent.glob('./info.dat'))[0]
            info_file = info_file.__str__()
            level_file_found = True
    if not level_file_found:
        continue

    if args.replace_existing or not os.path.isfile(features_file):
        print("creating feature file",i)
        # get level
        level = json.load(open(level, 'r'))
        info = json.load(open(info_file, 'r'))

        # get song
        print(song_file_path)
        y_wav, sr = librosa.load((song_file_path), sr=args.sampling_rate)

        bpm = info['_beatsPerMinute']
        sr = args.sampling_rate
        hop = int(sr * args.step_size)

        #get feature
        if args.feature_name == "chroma":
            if args.using_bpm_time_division:
                state_times = np.arange(0,y_wav.shape[0]/sr,step=args.step_size)
                features = extract_features_hybrid_beat_synced(y_wav,sr,state_times,bpm,beat_discretization=1/args.beat_subdivision)
            else:
                features = extract_features_hybrid(y_wav,sr,hop)
        elif args.feature_name == "mel":
            if args.using_bpm_time_division:
                raise NotImplementedError("Mel features with beat synced times not implemented, but trivial TODO")
            else:
                features = extract_features_mel(y_wav,sr,hop,mel_dim=args.feature_size)
        elif args.feature_name == "multi_mel":
            if args.using_bpm_time_division:
                raise NotImplementedError("Mel features with beat synced times not implemented, but trivial TODO")
            else:
                features = extract_features_multi_mel(y_wav, sr=args.sampling_rate, hop=hop, nffts=[1024,2048,4096], mel_dim=args.feature_size)

        np.save(features_file,features)
'''