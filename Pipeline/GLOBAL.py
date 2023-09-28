import os
import json
import datetime

if os.path.exists('/home/yiyu/'):
    path = '/home/yiyu/JustLM2D/'
else: path = '/Users/Marvin/NII_Code/JustLM2D/'

# jd2022 = json.load(open(path + "/Pipeline/jd2022.json", "r"))
test = {'SweetButPsychoAvaMaxJustDance2023Edition':[]}

all_years = ['2020', '2021', '2022']
songs_collection = [path + 'Songs_2020/', path + 'Songs_2021/', path + 'Songs_2022/']

year = '2022'
songs_dir = path + 'Songs_'+year+'/'

fps = 30
# sr = 16000
sr = 18000
sequenceLength = 6
lyrics_padding = 180

version = 'JD'+year

def toSeconds(time_stamp):
    minutes, seconds = map(float, time_stamp.split(':'))
    return datetime.timedelta(minutes=minutes, seconds=seconds).total_seconds()

def toTimestamp(seconds): #format muniute:second.milisecond
    delta = datetime.timedelta(seconds=seconds)
    return '{:02d}:{:06.3f}'.format(int(delta.total_seconds() // 60), delta.total_seconds() % 60)

def getSongList(version):
    if not os.path.exists(path + '/Pipeline/' + version+".json"):
        songList = {}
        json.dump(songList, open(version+".json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)

    songList = json.load(open(path + '/Pipeline/' + version+".json", "r"))
    return songList
