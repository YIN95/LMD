from GLOBAL import *

from torch.utils.data import Dataset

from nosmpl.smpl_onnx import SMPLOnnxRuntime
from nosmpl.vis.vis_o3d import Open3DVisualizer

import numpy as np
import torch
import torch.nn as nn
import os

from transformers import BertTokenizer, BertModel
import librosa

#Lyrics_Music_Dance_Dataset
class LMD_Dataset(Dataset): 
    def __init__ (self, data_dir, songs_collection, name='LMD'):
        self.dict_path = '%s/%s_Dict.pt'%(data_dir,name)
        self.indexing_path = '%s/%s_indexing.json'%(data_dir,name)
        self.songs_collection = songs_collection
        
        self.lyricsEmbedding = nn.Linear(768, 128)
        
        if os.path.exists(self.dict_path) and os.path.exists(self.indexing_path):
            self.LMD_Dict = torch.load(self.dict_path)
            self.indexing = json.load(open(self.indexing_path, 'r'))
        else: 
            print("Creating new dataset")
            # tokenizer for lyrics
            tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            model = BertModel.from_pretrained('bert-base-uncased')
            
            self.LMD_Dict = {}
            self.indexing = {}
            index = 0
            
            for year_dir in self.songs_collection:
                for song in os.listdir(year_dir):
                    print(song)
                    song_path = year_dir + song
                    
                    if song[0] in ['.','_'] or not os.path.isdir(song_path):
                        continue
                    if not os.path.exists(song_path + '/sliced.json') or not os.path.exists(song_path + '/output-smpl-3d/smplfull.json'):
                        continue
                    
                    # Load sliced lyrics as timestamps for cutting
                    sliced = json.load(open(song_path + '/sliced.json', 'r'))            
                    start = list(sliced.keys())[0]
                    todo = list(sliced.keys())
                    del todo[-1] # To avoid the last sequence being shorter than 6s
                    
                    full_dance = json.load(open('%s/output-smpl-3d/smplfull.json'%song_path, 'r'))

                    for timestamp in todo:
                        # trimed_timestamps = timestamp - start
                        trimed_timestamp = toTimestamp(toSeconds(timestamp)-toSeconds(start))
                        seconds = toSeconds(timestamp)
                        tag = str(int(seconds))
                        
                        # LAD Dict
                        dance_data = self.load_dance(full_dance, trimed_timestamp)
                        if dance_data!=None:
                            data = {'lyrics':self.load_lyrics(sliced[timestamp], tokenizer, model), \
                                'music':self.load_music('%s/audio.wav'%song_path, seconds), \
                                'dance':dance_data}
                        
                            self.LMD_Dict[song+"_"+tag] = data
                            self.indexing[index] = song+"_"+tag
                            index += 1

            with open(self.indexing_path, "w", encoding="utf-8") as json_file:
                json.dump(self.indexing, json_file, ensure_ascii=False, indent=4)
                
            torch.save(self.LMD_Dict, self.dict_path)

    def load_music(self, audio_path, start):
        audio = librosa.core.load(audio_path, sr=sr, offset=start, duration=sequenceLength)[0]
        
        # Extract features
        mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr, hop_length=601, n_mels=128)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        mel_spec_db_norm = (mel_spec_db - np.mean(mel_spec_db)) / np.std(mel_spec_db)
        audio_features = torch.from_numpy(mel_spec_db_norm).T
        return audio_features

    def load_dance(self, full_dance, timestamp):
        dance = []
        start = toSeconds(timestamp)*fps
        all_frames = list(full_dance.keys())
        
        for offset in range(sequenceLength*fps):
            stamp = str(int(start + offset)).zfill(6)
            if stamp in all_frames:
                poses = full_dance[stamp]['annots'][0]['poses'][0]
                Th = full_dance[stamp]['annots'][0]['Th'][0]
                Rh = full_dance[stamp]['annots'][0]['Rh'][0]
                dance.append(poses + Th + Rh)

        if len(dance) != sequenceLength*fps: return None
        dance = torch.from_numpy(np.array(dance))
        return dance

    def load_lyrics(self, lyrics, tokenizer, model):
        tokens = tokenizer.encode_plus(lyrics, add_special_tokens=True, return_tensors='pt')
        outputs = model(**tokens)
        # get the cls token
        lyrics_embeddings = outputs[0][:,0,:]
        lyrics_embeddings = outputs.last_hidden_state[0].detach()
        
        flexibleEmbedding = nn.Linear(lyrics_embeddings.size(0), sequenceLength*fps)

        lyrics_embeddings = lyrics_embeddings.permute(1,0)
        lyrics_embeddings = flexibleEmbedding(lyrics_embeddings)
        lyrics_embeddings = lyrics_embeddings.permute(1,0)
        lyrics_embeddings = self.lyricsEmbedding(lyrics_embeddings).detach()
        
        return lyrics_embeddings

    def __getitem__(self,index):
        key = self.indexing[str(index)]
        item = self.LMD_Dict[key]
        return item #['lyrics'], item['music'], item['dance']
    
    def __len__ (self):
        return len(self.indexing.keys())
    
    def visualize(self,seq_name, save_img_folder=None, inf=False, glob_trans=True):
        [song, tag] = seq_name.split("_")
        seq = self.LMD_Dict[seq_name]
        
        if inf:
            poses = torch.load('%s/%s/%s.pt'%(self.songs_collection[0], song, seq_name))
        
        elif seq != None:
            poses = seq['dance']
        else:
            print("Sequence does not exist")
            return

        smpl = SMPLOnnxRuntime()
        o3d_vis = Open3DVisualizer(fps=30, save_img_folder=save_img_folder, enable_axis=True)

        poses = poses.reshape(180,26,3).detach().numpy().astype(np.float32)
        
        for pose in poses:
            body = pose[:-3, :]
            trans = (pose[-2, :]).tolist()
            rot = pose[-1, :]
            body[0] = rot
            
            data = smpl.forward(body[None], [[[0,0,0]]])

            [vertices, joints, faces] = data
            vertices = vertices[0].squeeze()
            joints = joints[0].squeeze()
            faces = faces.astype(np.int32)
            
            if glob_trans:
                vertices += trans
                trans = [trans[0], trans[1], 0]

            if glob_trans: o3d_vis.update(vertices, faces, trans,  R_along_axis=(-np.pi, 0, 0), waitKey=1)
            else: o3d_vis.update(vertices, faces, [0,0,0],  R_along_axis=(0, 0, 0), waitKey=1)

        o3d_vis.release()
        
        
    def export(self, seq_name, save_dir=None, inf=False, glob_trans=True):
        if save_dir==None:
            save_dir = 'Previews/'+seq_name
        self.visualize(seq_name, save_img_folder=save_dir, inf=inf, glob_trans=glob_trans)
        
        # Load audio and lyrics
        lyrics = str(self.get_raw_audio_lyrics(save_dir, seq_name))
        lyrics = lyrics.replace('\'', '')
        lyrics = lyrics.replace('\"', '')
        lyrics = lyrics.replace(',', '\,')
        lyrics = lyrics.replace('.', '\.')
        print('\n',lyrics,'\n')
        
        # Merge Video audio and lyrics
        os.system('ffmpeg -framerate 30 -i ' + save_dir + '/temp_%04d.png -c:v libx264 -r 30 -pix_fmt yuv420p ' + save_dir + '/mesh.mp4')
        os.system('ffmpeg -i %s/mesh.mp4 -i %s/audio.wav -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 %s/tmp.mp4'%(save_dir, save_dir, save_dir))
        os.system("ffmpeg -i %s/tmp.mp4 -vf \"drawtext=fontfile=Roboto-Regular.ttf:text=%s:fontsize=30:x=(w-tw)/2:y=h-th-10:fontcolor=black\" -codec:a copy %s/%s.mp4"%(save_dir, lyrics, save_dir, seq_name))
                
        os.system('rm %s/*.png'%save_dir)
        os.system('rm %s/tmp.mp4'%save_dir)
        os.system('rm %s/mesh.mp4'%save_dir)
        os.system('rm %s/audio.wav'%save_dir)
        
    
    def get_raw_audio_lyrics(self, save_dir, seq_name):
        [song, tag] = seq_name.split("_")
        for year_dir in self.songs_collection:
            if os.path.isdir(year_dir + "/" + song):
                song_path = year_dir + "/" + song
                slicecd = json.load(open(song_path + "/sliced.json", "r"))
                for timestamp in slicecd:
                    if str(int(toSeconds(timestamp))) == tag:
                        lyrics = slicecd[timestamp]
                        os.system('ffmpeg -i %s/audio.wav -ss "%s" -t 00:06 -c copy %s/audio.wav'%(song_path, timestamp, save_dir))
                        return lyrics
                    