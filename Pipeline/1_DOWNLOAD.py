from GLOBAL import *

import re

def getURLs(version):
    if os.path.exists(version+"_url.json"):
        urls = json.load(open(version+"_url.json", "r"))['urls']
    else:
        urls = []
    return urls

def urlToTitle(version):
    urls = getURLs(version)
    songList = getSongList(version)
    finished = songList.values()
    
    if len(urls) == len(finished):
        print("Json already done")
        return
    
    for url in urls:
        if url in finished:
            continue
        # get title with yt-dlp
        title = os.popen('yt-dlp --get-title %s'%url[0]).read()
        print(title)
        # yt = pytube.YouTube(url[0])
        print(url)
        songList[re.sub(r'\W+', '',title)] = url
    
    json.dump(songList, open(version+".json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    

if __name__ == '__main__':
    urlToTitle(version)
    songList = getSongList(version)
    
    for song in songList.keys():
        song_path = songs_dir + re.sub(r'\W+', '',song)
        
        if not os.path.exists(song_path+"/video.mp4"):
            url = songList[song][0]
            crop = songList[song][1]
        
            # download video of 720p 30fps with yt-dlp
            print("downloading: "+ song)
            #delete everything in the folder
            os.system('rm -rf %s/*.mp4'%song_path)
            os.system('yt-dlp -f "best[height=720][fps=30]" -o "%s" %s'%(song_path+"/video.mp4", url))
        
    # crop 
    for song in songList.keys():
        song_path = songs_dir + re.sub(r'\W+', '',song)
        crop = songList[song][1]
        
        if not os.path.exists(song_path+"/lyrics.lrc"):
            os.system('touch '+song_path+'/lyrics.lrc')
        
        if not os.path.exists(song_path+"/audio.wav"):
           os.system('ffmpeg -i %s/video.mp4 -ab 160k -ac 2 -ar %s -vn %s/audio.wav'%(song_path, str(sr), song_path))
        
        # # Crop 
        # #if the video frame width is higer than 1000p
        # if crop != "full" and int(os.popen('ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=s=x:p=0 %s/video.mp4'%song_path).read()) > 1000:
        #     print("crop: "+ song)
        #     os.system('mv %s/video.mp4 %s/tmp.mp4'%(song_path,song_path))
        #     if crop == "left":
        #         os.system('ffmpeg -i %s/tmp.mp4 -filter:v "crop=in_w/2:in_h:0:0" %s/video.mp4'%(song_path,song_path))
        #     elif crop == "right":
        #         os.system('ffmpeg -i %s/tmp.mp4 -filter:v "crop=in_w/2:in_h:in_w/2:0" %s/video.mp4'%(song_path,song_path))
        #     elif crop == "center":
        #         os.system('ffmpeg -i %s/tmp.mp4 -filter:v "crop=in_w/2:in_h:in_w/4:0" %s/video.mp4'%(song_path,song_path))
        # os.system('rm %s/tmp.mp4'%song_path)
