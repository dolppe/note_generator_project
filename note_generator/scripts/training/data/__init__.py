import sys
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(os.path.join(THIS_DIR, os.pardir), os.pardir))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
EXTRACT_DIR = os.path.join(DATA_DIR, 'extracted_data')
if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)
if not os.path.isdir(EXTRACT_DIR):
    os.mkdir(EXTRACT_DIR)

sys.path.append(ROOT_DIR)
import importlib
from torch.utils.data import DataLoader
from .base_dataset import BaseDataset
import numpy as np
import torch
from models.constants import PAD_STATE

def find_dataset_using_name(dataset_name, task_name):
    # Given the option --dataset_name [datasetname],
    # the file "data/datasetname_dataset.py"
    # will be imported.

    # try:
    task_module = importlib.import_module(task_name)
    dataset_filename = task_name + ".data." + dataset_name + "_dataset"    
    datasetlib = importlib.import_module(dataset_filename, package=task_module)
    # except (ModuleNotFoundError, ImportError):
    #     # if module not found, attempt to load from base
    #     task_name = 'base'
    #     task_module = importlib.import_module(task_name)
    #     dataset_filename = task_name + ".data." + dataset_name + "_dataset"
    #     datasetlib = importlib.import_module(dataset_filename, package=task_module)

    # In the file, the class called DatasetNameDataset() will
    # be instantiated. It has to be a subclass of BaseDataset,
    # and it is case-insensitive.

    def is_subclass(subclass, superclass):
        return next(iter(subclass.__bases__)).__module__.endswith(superclass.__module__)

    dataset = None
    target_dataset_name = dataset_name.replace('_', '') + 'dataset'
    for name, cls in datasetlib.__dict__.items():
        if name.lower() == target_dataset_name.lower():
            if is_subclass(cls, BaseDataset) or any(is_subclass(cls_b, BaseDataset) for cls_b in cls.__bases__):
                dataset = cls

    if dataset is None:
        raise NotImplementedError("In {}.py, there should be a subclass of BaseDataset with class name that matches {} in lowercase.".format(
              dataset_filename, target_dataset_name))

    return dataset


def get_option_setter(dataset_name, task_name):
    dataset_class = find_dataset_using_name(dataset_name, task_name)
    return dataset_class.modify_commandline_options


def create_dataset(opt, validation_phase=False,*args,**kwargs):
    dataset = find_dataset_using_name(opt.dataset_name, opt.task)
    if validation_phase:
        opt.phase = "val"
    instance = dataset(opt,*args,**kwargs)
    print('dataset [{}] was created {}'.format(instance.name(), "(val)" if validation_phase else ''))
    return instance

def paired_collate_fn(insts,tgt_dim=2):
    src_insts= list(map(lambda x: x['input'],insts))
    tgt_insts = list(map(lambda x: x['target'],insts))
    src_insts = collate_fn(src_insts,dim=2)
    tgt_insts = collate_fn(tgt_insts,dim=tgt_dim)
    return {'input':src_insts, 'target':tgt_insts}

def collate_fn(insts,dim=-1): #dim is time dim
    ''' Pad the instance to the max seq length in batch '''

    max_len = max(inst.shape[dim] for inst in insts)

    # print(max_len)
    batch_seq = [
        torch.cat([inst.long(),torch.full(inst.shape[:dim]+((max_len - inst.shape[dim]),)+inst.shape[dim+1:],PAD_STATE).long()],dim)
        for inst in insts]

    batch_pos = np.array([
        [pos_i+1 for pos_i in range(inst.shape[dim])] + [PAD_STATE]*(max_len - inst.shape[dim]) for inst in insts])

    batch_seq = torch.stack(batch_seq)
    # print(batch_seq)
    batch_pos = torch.LongTensor(batch_pos)

    return batch_seq, batch_pos

def transformer_paired_collate_fn(insts):
    return paired_collate_fn(insts,tgt_dim=2)

def wavenet_paired_collate_fn(insts):
    return paired_collate_fn(insts,tgt_dim=1)

def meta_collate_fn(pad_batches, model):
    if pad_batches:
        if model == "transformer":
            return transformer_paired_collate_fn
        else:
            return wavenet_paired_collate_fn
    else:
        return default_collate

from torch.utils.data.dataloader import default_collate
def create_dataloader(dataset):
    is_val = dataset.opt.phase == "val"
    return DataLoader(dataset,
                      batch_size=dataset.opt.batch_size if not is_val else dataset.opt.val_batch_size,
                      shuffle=not is_val,
                      collate_fn=meta_collate_fn(dataset.opt.pad_batches,dataset.opt.model),
                      num_workers=dataset.opt.workers)
