from GLOBAL import *

fps = 30
sr = 16000
    
if __name__ == '__main__':
    todo = []
    for song in getSongList(version):
        song_path = songs_dir + song
        if song[0]=='.' or song[0]=='_' \
            or not os.path.isdir(song_path) \
                or len(os.listdir('%s/videos'%song_path)) == 0 \
                    or ( os.path.exists('%s/output-smpl-3d'%(song_path)) and (not os.path.exists('%s/annots'%(song_path)) or len(os.listdir('%s/annots'%(song_path))) == 0)):
            continue
        todo.append(song)

    # todo.sort()
    # todo = todo[::-1]
    print(todo)

    os.chdir('./.EasyMocap/')
    for song in todo:
        song_path = songs_dir + song
        os.system('python apps/preprocess/extract_keypoints.py %s --mode mp-pose'%song_path)