import numpy as np
import torch
from math import *
import pickle

import sys
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(os.path.join(os.path.join(THIS_DIR, os.pardir, os.pardir), os.pardir)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
EXTRACT_DIR = os.path.join(DATA_DIR, 'extracted_data')
if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)
if not os.path.isdir(EXTRACT_DIR):
    os.mkdir(EXTRACT_DIR)

sys.path.append(ROOT_DIR)

unique_states = pickle.load(open(DATA_DIR+"/statespace/sorted_states.pkl","rb"))
from models import constants


def get_reduced_tensors_from_level(notes, indices, sequence_length, num_classes, bpm, sr, num_samples_per_feature,
                                   receptive_field, input_length, output_length, time_offset):
    l = sequence_length
    ## BLOCKS TENSORS ##
    # variable `blocks` of shape (time steps, number of locations in the block grid), storing the class of block (as a number from 0 to 19) at each point in the grid, at each point in time
    # this variable is here only used to construct the blocks_reduced later; in the non-reduced representation dataset, it would be used directly.
    blocks = np.zeros((l, 12))
    # reduced state version of the above. The reduced-state "class" at each time is represented as a one-hot vector of size `self.opt.num_classes`
    blocks_reduced = np.zeros((l, num_classes))
    # same as above but with class number, rather than one-hot, used as target
    blocks_reduced_classes = np.zeros((l, 1))

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
            blocks_reduced[i, constants.START_STATE] = 1.0
            blocks_reduced_classes[i, 0] = constants.START_STATE
        elif i == len(blocks) - 1:
            blocks_reduced[i, constants.END_STATE] = 1.0
            blocks_reduced_classes[i, 0] = constants.END_STATE
        else:
            try:
                state_index = unique_states.index(tuple(block))
                if num_classes <= constants.NUM_SPECIAL_STATES + 1:
                    state_index = 0
                blocks_reduced[i, constants.NUM_SPECIAL_STATES + state_index] = 1.0
                blocks_reduced_classes[i, 0] = constants.NUM_SPECIAL_STATES + state_index
            except (ValueError,
                    IndexError):  # if not in top 2000 states, then we consider it the empty state (no blocks; class = 0)
                blocks_reduced[i, constants.EMPTY_STATE] = 1.0
                blocks_reduced_classes[i, 0] = constants.EMPTY_STATE

    # get the block features corresponding to the windows
    block_reduced_targets_windows = [blocks_reduced_classes[
                                     i + time_offset + receptive_field - 1:i + time_offset + receptive_field - 1 + output_length,
                                     :] for i in indices]
    block_reduced_targets_windows = torch.tensor(block_reduced_targets_windows, dtype=torch.long)
    blocks_reduced_windows = [blocks_reduced[i:i + input_length, :] for i in indices]

    blocks_reduced_windows = torch.tensor(blocks_reduced_windows)
    ### TODO: I think the padding below is only for wavenet model :PPP
    blocks_reduced_windows_pad = torch.zeros(blocks_reduced_windows.shape)
    blocks_reduced_windows_pad[:, :, constants.PAD_STATE] = 1.0
    blocks_reduced_windows = torch.cat([blocks_reduced_windows, blocks_reduced_windows_pad.double()], 1)
    # this is because the input features have dimensions (num_windows,time_steps,num_features)
    blocks_reduced_windows = blocks_reduced_windows.permute(0, 2, 1)

    return blocks_reduced_windows, block_reduced_targets_windows

def get_raw_binary_reduced_tensors_from_level(notes, sequence_length, num_classes, bpm, sr, num_samples_per_feature, receptive_field):
    l = sequence_length
    ## BLOCKS TENSORS ##
    # variable `blocks` of shape (time steps, number of locations in the block grid), storing the class of block (as a number from 0 to 19) at each point in the grid, at each point in time
    # this variable is here only used to construct the blocks_reduced later; in the non-reduced representation dataset, it would be used directly.
    blocks = np.zeros((l, 12))
    # reduced state version of the above. The reduced-state "class" at each time is represented as a one-hot vector of size `self.opt.num_classes`
    blocks_reduced = np.zeros((l, num_classes))
    # same as above but with class number, rather than one-hot, used as target
    blocks_reduced_classes = np.zeros((l, 1))

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
            blocks_reduced[i, constants.START_STATE] = 1.0
            blocks_reduced_classes[i, 0] = constants.START_STATE
        elif i == len(blocks) - 1:
            blocks_reduced[i, constants.END_STATE] = 1.0
            blocks_reduced_classes[i, 0] = constants.END_STATE
        else:
            try:
                state_index = unique_states.index(tuple(block))
                if num_classes <= constants.NUM_SPECIAL_STATES + 1:
                    state_index = 0
                blocks_reduced[i, constants.NUM_SPECIAL_STATES + state_index] = 1.0
                blocks_reduced_classes[i, 0] = constants.NUM_SPECIAL_STATES + state_index
            except (ValueError,
                    IndexError):  # if not in top 2000 states, then we consider it the empty state (no blocks; class = 0)
                blocks_reduced[i, constants.EMPTY_STATE] = 1.0
                blocks_reduced_classes[i, 0] = constants.EMPTY_STATE
    return blocks_reduced, blocks_reduced_classes

def get_raw_binary_classes_reduced_tensors_from_level(notes, sequence_length, num_classes, bpm, sr, num_samples_per_feature, receptive_field):
    l = sequence_length
    ## BLOCKS TENSORS ##
    # variable `blocks` of shape (time steps, number of locations in the block grid), storing the class of block (as a number from 0 to 19) at each point in the grid, at each point in time
    # this variable is here only used to construct the blocks_reduced later; in the non-reduced representation dataset, it would be used directly.
    blocks = np.zeros((l, 12))
    # reduced state version of the above. The reduced-state "class" at each time is represented as a one-hot vector of size `self.opt.num_classes`
    blocks_reduced_classes = np.zeros((l, 1))

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

def get_binary_reduced_tensors_from_level_fast(blocks_reduced, blocks_reduced_classes, indices, sequence_length, num_classes, bpm, sr, num_samples_per_feature,
                                   receptive_field, input_length, output_length, time_offset):
    # get the block features corresponding to the windows
    block_reduced_targets_windows = [blocks_reduced_classes[
                                     i + time_offset + receptive_field - 1:i + time_offset + receptive_field - 1 + output_length,
                                     :] for i in indices]
    block_reduced_targets_windows = torch.tensor(block_reduced_targets_windows, dtype=torch.long)
    blocks_reduced_windows = [blocks_reduced[i:i + input_length, :] for i in indices]

    blocks_reduced_windows = torch.tensor(blocks_reduced_windows)
    # blocks_reduced_windows_pad = torch.zeros(blocks_reduced_windows.shape)
    # blocks_reduced_windows_pad[:, :, constants.PAD_STATE] = 1.0
    # blocks_reduced_windows = torch.cat([blocks_reduced_windows, blocks_reduced_windows_pad.double()], 1)
    # this is because the input features have dimensions (num_windows,time_steps,num_features)
    blocks_reduced_windows = blocks_reduced_windows.permute(0, 2, 1)

    return blocks_reduced_windows, block_reduced_targets_windows

def get_binary_reduced_tensors_from_level_faster(blocks_reduced_classes, indices, sequence_length, num_classes, bpm, sr, num_samples_per_feature,
                                   receptive_field, input_length, output_length, time_offset):
    # get the block features corresponding to the windows
    block_reduced_targets_windows = [blocks_reduced_classes[
                                     i + time_offset + receptive_field - 1:i + time_offset + receptive_field - 1 + output_length,
                                     :] for i in indices]
    block_reduced_targets_windows = torch.tensor(block_reduced_targets_windows, dtype=torch.long)

    return block_reduced_targets_windows

def get_binary_classes_reduced_tensors_from_level(notes, indices, sequence_length, num_classes, bpm, sr, num_samples_per_feature,
                                   receptive_field, input_length, output_length, time_offset):
    l = sequence_length
    ## BLOCKS TENSORS ##
    # variable `blocks` of shape (time steps, number of locations in the block grid), storing the class of block (as a number from 0 to 19) at each point in the grid, at each point in time
    # this variable is here only used to construct the blocks_reduced later; in the non-reduced representation dataset, it would be used directly.
    blocks = np.zeros((l, 12))
    # reduced state version of the above. The reduced-state "class" at each time is represented as a one-hot vector of size `self.opt.num_classes`
    blocks_reduced_classes = np.zeros((l, 1))

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

    # get the block features corresponding to the windows
    block_reduced_targets_windows = [blocks_reduced_classes[
                                     i + time_offset + receptive_field - 1:i + time_offset + receptive_field - 1 + output_length,
                                     :] for i in indices]
    block_reduced_targets_windows = torch.tensor(block_reduced_targets_windows, dtype=torch.long)

    return block_reduced_targets_windows

def get_full_tensors_from_level(notes, indices, l, num_classes, output_channels, bpm, sr, num_samples_per_feature,
                                receptive_field, input_length):
    ## BLOCKS TENSORS ##
    # variable `blocks` of shape (time steps, number of locations in the block grid), storing the class of block (as a number from 0 to 19) at each point in the grid, at each point in time
    blocks = np.zeros((l, output_channels))
    # many-hot vector
    # for each point in the grid we will have a one-hot vector of size 20 (num_classes)
    # and we will just stack these 12 (output_channels) one-hot vectors
    # to get a "many-hot" tensor of shape (time_steps,output_channels,num_classes)
    blocks_manyhot = np.zeros((l, output_channels, num_classes))
    # we initialize the one-hot vectors in the tensor
    blocks_manyhot[:, :, 0] = 1.0  # default is the "nothing" class

    ## CONSTRUCT BLOCKS TENSOR ##
    for note in notes:
        # sample_index = floor((time of note in seconds)*sampling_rate/(num_samples_per_feature))
        sample_index = floor((note['_time'] * 60 / bpm) * sr / num_samples_per_feature)
        # check if note falls within the length of the song (why are there so many that don't??) #TODO: research why this happens
        if sample_index >= l:
            print("note beyond the end of time")
            continue

        # constructing the representation of the block (as a number from 0 to 19)
        if note["_type"] == 3:
            note_representation = 19
        elif note["_type"] == 0 or note["_type"] == 1:
            note_representation = 1 + note["_type"] * 9 + note["_cutDirection"]
        else:
            raise ValueError("I thought there was no notes with _type different from 0,1,3. Ahem, what are those??")
        blocks[sample_index, note["_lineLayer"] * 4 + note["_lineIndex"]] = note_representation
        blocks_manyhot[
            sample_index, note["_lineLayer"] * 4 + note["_lineIndex"], 0] = 0.0  # remove the one hot at the zero class
        blocks_manyhot[sample_index, note["_lineLayer"] * 4 + note["_lineIndex"], note_representation] = 1.0

    # get the block features corresponding to the windows
    block_windows = [blocks[i + receptive_field:i + input_length + 1, :] for i in indices]
    block_windows = torch.tensor(block_windows, dtype=torch.long)

    blocks_manyhot_windows = [blocks_manyhot[i:i + input_length, :, :] for i in indices]
    blocks_manyhot_windows = torch.tensor(blocks_manyhot_windows)
    # this is because the input features have dimensions (num_windows,time_steps,num_features)
    blocks_manyhot_windows = blocks_manyhot_windows.permute(0, 2, 3, 1)
    shape = blocks_manyhot_windows.shape
    # now we reshape so that the stack of one-hot vectors becomes a single "many-hot" vector
    # formed by concatenating the one hot vectors
    blocks_manyhot_windows = blocks_manyhot_windows.view(shape[0], shape[1] * shape[2], shape[3]).float()

    return blocks_manyhot_windows, block_windows
