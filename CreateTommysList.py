"""
Python script to populate a playlist to sync down to a device.
The playlist contains the first episode of each show in the TV section.
Shows specified in ExludeShows are not added to the playlist.
"""
from plexapi.server import PlexServer
import ConfigParser
import os.path

Config = ConfigParser.ConfigParser()
playlistName = ''

if not os.path.exists('/home/tommy/CreateSyncList.cfg'):
    print 'CreateSyncList.cfg not found'
    exit()

Config.read('/home/tommy/CreateSyncList.cfg')


def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


baseurl = ConfigSectionMap('General')['baseurl']
token = ConfigSectionMap('General')['token']
plex = PlexServer(baseurl, token)

playlistName = ConfigSectionMap('General')['playlistname']
numberOfShows2Add = ConfigSectionMap('General')['numberofepisodes2sync']

startAfterThisShow = ConfigSectionMap(playlistName)['lastsyncedshow']
doNotSyncThese = ConfigSectionMap(playlistName)['excludeshows']
doNotSyncThese = doNotSyncThese.replace('\n', ' ')  # Remove the \n from the read string
doNotSyncThese = doNotSyncThese.replace(', ', ',')  # Remove the \n from the read string

ExcludeShows = doNotSyncThese.split(",")

if playlistName == '':
    print ("No playlist specified. Please add PlaylistName under [General] in CreateSyncList.cfg")
    exit()

Playlist = plex.playlist(playlistName)

thefirstlist = [];
AllEpisodes = [];
TVEpisodes = 0;
TotalSize = 0;

showName = ''
StartFromCurrent = False

# Check for the last show in the playlist and start adding episodes after that.
# We don't want to  transcode and sync those again
for episode in Playlist.items():
    showName = episode.grandparentTitle

    # Trim the showName by removing the leading 'A '/'The ' so we can compared to the titleSort
    if showName.startswith('A '):
        showName = showName[2:]
    if showName.startswith('The '):
        showName = showName[4:]

    if episode.isWatched:
        Playlist.removeItem(episode)
    else:
        TotalSize = TotalSize;
    StartFromCurrent = True
    TVEpisodes += 1

alreadyInList = TVEpisodes
# If we still have shows left in the current playlist, start from that show
if (showName != ''):
    firstShowToAdd = showName

TVsection = plex.library.section('TV')
for shows in TVsection.all():

    if StartFromCurrent:
        if firstShowToAdd == shows.titleSort or firstShowToAdd.upper() < shows.titleSort.upper():
            StartFromCurrent = False
        continue

    if shows.title in ExcludeShows:
        print('Excluded: ', shows.title)
        continue

    episode = shows.episodes()[0]

    if shows.episodes()[0].seasonNumber == '0':  # Don't sync specials
        for episode in shows.episodes():
            strSeason = episode.seasonNumber  # We need to explicitly set the seasonNumber to get it right.
            if (strSeason == '0'):
                continue
            thefirstlist.append(episode)
            TVEpisodes += 1
            break
        continue

    if len(shows.episodes()) <= 3:
        for episode in shows.episodes():
            thefirstlist.append(episode)
            TVEpisodes += 1
        AllEpisodes.append(shows.title)
    else:
        thefirstlist.append(shows.episodes()[0])

    TVEpisodes += 1;

    if TVEpisodes >= int(numberOfShows2Add):
        break

Playlist.addItems(thefirstlist)

Config.set(playlistName, 'FirstSyncedShow', thefirstlist[0].grandparentTitle)
Config.set(playlistName, 'LastSyncedShow', shows.title)

with open(r'CreateSyncList.cfg', 'wb') as configfile:
    Config.write(configfile)

print('Episodes added to the Playlist:', TVEpisodes - alreadyInList)
for show in AllEpisodes:
    print('All episodes are added for show: ', show)
