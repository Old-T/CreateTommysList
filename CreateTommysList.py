"""
Python script to populate a playlist to sync down to a device.
The playlist contains the first episode of each show in the TV section.
Shows specified in ExludeShows are not added to the playlist.
"""
from plexapi.server import PlexServer
import ConfigParser
import os.path

baseurl = 'http://192.168.2.50:32400'
token = 'zbv7hDnHEV2aGKRmQsRd'
plex = PlexServer(baseurl, token)
Config = ConfigParser.ConfigParser()
playlistName = ''


if not os.path.exists('/home/tommy/CreateTommysList.cfg'):
    print( 'CreateTommysList.cfg not found' )
    exit()

Config.read('/home/tommy/CreateTommysList.cfg')

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

#SyncThese = "24, The Blacklist: Redemption, Criminal Minds, Hawaii Five-0, Humans, The Kettering Incident,\
#Lethal Weapon, NCIS, NCIS: Los Angeles, NCIS: New Orleans, Person of Interest, S.W.A.T. (2017),\
#SEAL Team, Stranger Things"
SyncThese = ConfigSectionMap(playlistName)['includeshows']
SyncThese = SyncThese.replace('\n', ' ')  # Remove the \n from the read string
SyncThese = SyncThese.replace(', ', ',')  # Remove the \n from the read string

SyncThese = SyncThese.split(",")

if playlistName == '':
    print ("No playlist specified. Please add PlaylistName under [General] in CreateSyncList.cfg")
    exit()

Playlist = plex.playlist(playlistName)

AddToPlaylist = []

showName = ''
StartFromCurrent = False

# Loop through all TV show, for the shows that are included SyncThese check
# Check for the last show in the playlist and start adding episodes after that.
# We don't want to  transcode and sync those again
for show2Sync in SyncThese:

    TVsection = plex.library.section('TV')
    for shows in TVsection.all():
        # find the shows we want to sync
        if shows.title == show2Sync:
            # Show to sync
            # Find the last episode in the current playlist.
            season = -1
            episodeNo = -1
            for episode in Playlist.items():
                if episode.grandparentTitle == shows.title:
                    season = episode.seasonNumber
                    episodeNo = episode.index

            for episode in shows.episodes():
                strSeason = episode.seasonNumber  # Do not add special episodes
                if (strSeason == '0'):
                    continue

                if int(episode.index) > int(episodeNo) or int(episode.seasonNumber) > int(season):
                    AddToPlaylist.append(episode)
                    break
            break

Playlist.addItems(AddToPlaylist)


