from GLOBAL import *
    
def autoSlice(song_path, sequenceLength):
    with open('%s/lyrics.lrc'%song_path,'r') as fin:
        lines = fin.readlines()
        if len(lines) == 0:
            return None
        lines = [line.strip() for line in lines]
        if lines[0][0] != '[':
            return None
        
    out = {}
    tmpTimestamps = lines[0].split(']')[0][1:]
    
    tmpLyrics = ''
    
    for line in lines:
        timestamp = line.split(']')[0][1:]
        lyrics = line.split(']')[1]
        
        if toSeconds(timestamp) - toSeconds(tmpTimestamps) > sequenceLength or toSeconds(tmpTimestamps)==0:
            # if "u0" in tmpLyrics: print(tmpLyrics)
            out[tmpTimestamps] = tmpLyrics.lstrip()
            tmpLyrics = lyrics
            tmpTimestamps = timestamp
        else:
            tmpLyrics = tmpLyrics + ' ' + lyrics
    
    json.dump(out, open(song_path+'/sliced.json', 'w', encoding="utf-8"), ensure_ascii=False, indent=4)
    
    return out

def trim(song_path, sliced):
    timestamps = list(sliced.keys())
    start = timestamps[0]
    end = toTimestamp(toSeconds(timestamps[-1]) + sequenceLength + 1)

    # os.system('mv %s/video.mp4 %s/tmp.mp4'%(song_path, song_path))
    os.system('ffmpeg -i %s -ss %s -to %s -c copy %s' % (song_path+'/video.mp4', start, end, song_path+'/videos/video.mp4'))
    # os.system('rm %s/tmp.mp4'%song_path)

if __name__ == '__main__':
    
    for song in getSongList(version):
        song_path = songs_dir + song
        
        autoSlice(song_path, sequenceLength)
        
        if song[0]=='.' or song[0]=='_' \
            or not os.path.isdir(song_path) \
                    or not os.path.exists('%s/lyrics.lrc'%(song_path)):
            continue
        
        if not os.path.exists('%s/videos'%song_path):
            os.system('mkdir %s/videos'%song_path)
            os.system('mkdir %s/audios'%song_path)
            
        if len(os.listdir('%s/videos'%song_path)) > 0 or len(os.listdir('%s/audios'%song_path)) > 0:
            continue
        
        print("slicing: "+ song)
        sliced = autoSlice(song_path, sequenceLength)
        if sliced is None:
            continue
        
        trim(song_path, sliced)