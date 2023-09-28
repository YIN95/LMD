from GLOBAL import *
import re

todo = []
for song in getSongList(version):
    song_path = songs_dir+song
    if song[0]=='.' or song[0]=='_' \
        or not os.path.isdir(song_path) \
            or len(os.listdir('%s/videos'%song_path)) == 0 \
                    or ( os.path.exists('%s/output-smpl-3d'%(song_path)) and (not os.path.exists('%s/annots'%(song_path)) or len(os.listdir('%s/annots'%(song_path))) == 0)):
        continue
    todo.append(song)

# todo.sort()
print(todo)
# todo = todo[::-1]

for song in todo:
    song_path = songs_dir+song
    if os.path.exists('%s/output-smpl-3d/smplmesh'%song_path):
        for dir in os.listdir('%s/output-smpl-3d/smplmesh'%song_path):
            os.system('rm -rf %s/images/%s'%(song_path,dir))
            os.system('rm -rf %s/annots/%s'%(song_path,dir))

os.chdir('./.EasyMocap/')

for song in todo:
    song_path = songs_dir+song
    
    os.system('python apps/demo/mocap.py %s --work internet --fps 30 --bodyonly'%song_path) 
    #--disable_vismesh \
    
    if os.path.exists('%s/output-smpl-3d/smplmesh'%song_path):
        for dir in os.listdir('%s/output-smpl-3d/smplmesh'%song_path):
            os.system('rm -rf %s/images/%s'%(song_path,dir))
            os.system('rm -rf %s/annots/%s'%(song_path,dir))
            
for song in os.listdir(path):
    song_path = songs_dir+song
    if os.path.exists('%s/output-smpl-3d'%song_path):
        for dir in os.listdir('%s/output-smpl-3d/smplmesh'%song_path):
            if dir[-4:] == '.mp4':
                # get file name without .mp4
                toDel = dir[:-4]
                os.system('rm -rf %s/output-smpl-3d/smplmesh/%s'%(song_path,toDel))
    if os.path.exists('%s/images'%song_path) and os.path.exists('%s/annots'%song_path)  and os.path.exists('%s/cache_spin'%song_path) \
        and len(os.listdir('%s/images'%song_path)) == 0 and len(os.listdir('%s/annots'%song_path)) == 0:
        os.system('rm -rf %s/images'%song_path)
        os.system('rm -rf %s/annots'%song_path)
        os.system('rm -rf %s/cache_spin'%song_path)
        
for song in os.listdir(songs_dir):
    song_path = songs_dir+song
    os.system('rm -rf %s/cache_spin'%song_path)

    all_frames = {}
    for frame in os.listdir('%s/output-smpl-3d/smplfull/video'%song_path):
        if frame[-5:] == '.json':
            all_frames[frame[:-5]] = json.load(open('%s/output-smpl-3d/smplfull/video/%s'%(song_path,frame),'r'))

    json.dump(all_frames, open('%s/output-smpl-3d/smplfull.json'%song_path, 'w', encoding="utf-8"), ensure_ascii=False)

    with open('%s/output-smpl-3d/smplfull.json'%song_path, 'r') as f:
        text = f.read()

    # Remove newlines after "[" character using regular expressions
    text = re.sub(r'(".*?":)', r'\n\1', text)
    text = re.sub(r'("K"|"R"|"T"|"annots")', r'\t\1', text)
    text = re.sub(r'("id"|"shapes"|"poses"|"Rh"|"Th")', r'\t\t\1', text)

    # Open the file for writing and write the modified text
    with open('%s/output-smpl-3d/smplfull.json'%song_path, 'w') as f:
        f.write(text)
    
    print(song)