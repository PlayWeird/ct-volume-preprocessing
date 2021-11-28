import os.path
from functools import lru_cache
from typing import Optional

import nibabel as nib
import numpy as np
import pytorch_lightning as pl
import torch
from torch.utils.data import DataLoader, random_split, Dataset
from torch.utils.data.dataset import T_co
import glob
import ct_utils


class CTScanDataModule(pl.LightningDataModule):
    def __init__(self, data_dir: str = "path/to/dir", batch_size: int = 5):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.ct_train = None
        self.ct_val = None
        self.ct_test = None

    def setup(self, stage: Optional[str] = None):
        ct_dataset = CTDataSet(self.data_dir)
        ct_len = len(ct_dataset)
        portions = [0.8, 0.1, 0.1]
        sizes = [int(portion * ct_len) for portion in portions]
        self.ct_train, self.ct_val, self.ct_test = random_split(ct_dataset, sizes)

    def train_dataloader(self):
        return DataLoader(self.ct_train, batch_size=self.batch_size)

    def val_dataloader(self):
        return DataLoader(self.ct_val, batch_size=self.batch_size)

    def test_dataloader(self):
        return DataLoader(self.ct_test, batch_size=self.batch_size)

    def teardown(self, stage: Optional[str] = None):
        pass
        # Used to clean-up when the run is finished


class CTDataSet(Dataset):
    def __init__(self, data_dir: str):
        self.data_path_list = glob.glob(data_dir + '*')
        self.data_path_list.sort()

    def __len__(self):
        return len(self.data_path_list)

    def __getitem__(self, index):
        sample = ct_utils.get_sample_label_id(self.data_path_list[index], is_nifti_dataset=True)
        nifti_jaw = nib.load(sample['data'])
        jaw = torch.Tensor(np.asarray(nifti_jaw.dataobj))
        nifti_label = nib.load(sample['label'])
        label = torch.Tensor(np.asarray(nifti_label.dataobj))
        jaw = torch.unsqueeze(jaw, 0)
        label = torch.unsqueeze(label, 0)
        return jaw, label
