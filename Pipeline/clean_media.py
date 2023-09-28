import os 

song_dirs = 

for dir in os.listdir('/home/yiyu/Downloads/Songs_2022'):
    # if os.path.exists('/home/yiyu/Downloads/Songs/%s/video.mp4'%dir):
    #     os.remove('/home/yiyu/Downloads/Songs/%s/video.mp4'%dir)
    # if os.path.exists('/home/yiyu/Downloads/Songs/%s/audio.wav'%dir):
    #     os.remove('/home/yiyu/Downloads/Songs/%s/audio.wav'%dir)
    if not os.path.exists('/home/yiyu/Downloads/Songs_2022/%s/audio.wav'%dir):
        os.system('ffmpeg -i %s/video.mp4 -ab 160k -ac 2 -ar %s -vn %s/audio.wav'%(song_path, str(sr), song_path))