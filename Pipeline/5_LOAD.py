from GLOBAL import *
from LMD_Dataset import LMD_Dataset

from multiprocessing import freeze_support
from torch.utils.data import DataLoader
import random
    
if __name__ == '__main__':
    freeze_support()
    
    dataset = LMD_Dataset(path + '/Pipeline/', songs_collection, name='LMD_New_Embedding')
    sample = dataset.LMD_Dict['SmalltownBoybyBronskiBeatJustDance2022ComiCon_239']
    print(sample['lyrics'].shape, sample['music'].shape, sample['dance'].shape)
    dataloader = DataLoader(dataset=dataset, batch_size=1, shuffle=True, num_workers=1)

    dataiter = iter(dataloader)
    data = next(dataiter)
    
    print(data['lyrics'].size(), data['music'].size(), data['dance'].size())
    
    seq = random.choice(list(dataset.indexing.values()))
    # seq = 'BuildABBellaPoarchJustDance2022_22'
    # seq = 'MONTEROCallMebyYourNamebyLilNasXJustDance2022_41'
    # seq = 'MONTEROCallMebyYourNamebyLilNasXJustDance2022_57'
    
    # dataset.visualize(seq)
    dataset.export(seq)
