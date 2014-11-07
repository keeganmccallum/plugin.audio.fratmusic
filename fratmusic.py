import requests
import sys
import urllib
import urlparse
import xbmc
import xbmcplugin
import xbmcgui
try:
    import json
except:
    import simplejson as json

BASE_URL = 'http://fratmusic.com/api/'
STATIONS_URL = BASE_URL+"stations.php"
PLAYLISTS_URL = BASE_URL+"playlists.php"

addon_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

page = args.get("page", [None])[0]


def build_url(query):
    return addon_url + '?' + urllib.urlencode(query)


def get_stations():
    resp = requests.get(url=STATIONS_URL)
    data = json.loads(resp.text)
    stations = data["stations"]

    for station in stations:
        params = {"station_id": station["station_id"], "page": "playlists"}
        url = build_url(params)
        li = xbmcgui.ListItem(station["station_name"],
                              iconImage=station["station_cover_image"])
        li.setProperty('fanart_image', station["station_cover_image"])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    isFolder=True, listitem=li)


def get_playlists(station_id):
    resp = requests.get(url=PLAYLISTS_URL,
                        params={"stationId": station_id,
                                "playlistPerPage": 1000})
    data = json.loads(resp.text)
    playlists = data["playlists"]

    for playlist in playlists:
        params = {"page": "songs",
                  "playlist_url": playlist.get("playlist_api_url", "")}
        cover_urls = playlist["cover_urls"]
        li = xbmcgui.ListItem(playlist["playlist_name"],
                              thumbnailImage=cover_urls["thumbnail_cover"],
                              iconImage=cover_urls["large_cover"])
        li.setProperty('fanart_image', cover_urls["large_cover"])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=build_url(params),
                                    isFolder=True, listitem=li)


def get_songs(playlist_url):
    resp = requests.get(url=playlist_url)
    data = json.loads(resp.text)
    tracks = data["playlist_mix"]["tracks"]

    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    playlist.clear()

    for track in tracks:
        playlist.add(track["stream_url"])

    li = xbmcgui.ListItem("Play All", iconImage="DefaultAudio.png")
    xbmcplugin.addDirectoryItem(handle=addon_handle,
                                url=build_url({"page": "play_all"}), listitem=li)

    li = xbmcgui.ListItem("Shuffle", iconImage="DefaultAudio.png")
    xbmcplugin.addDirectoryItem(handle=addon_handle,
                                url=build_url({"page": "shuffle"}), listitem=li)

    for i, track in enumerate(tracks):
        li = xbmcgui.ListItem(track["track_name"], iconImage="DefaultAudio.png")
        li.setInfo("music", {
            "tracknumber": i + 1,
            "artist": track["track_artist"],
            "title": track["track_name"]
        })
        li.setMimeType("audio/mpeg")
        li.setProperty('IsPlayable', 'true')

        xbmcplugin.addDirectoryItem(handle=addon_handle,
                                    url=track["stream_url"], listitem=li)


def shuffle():
    xbmc.PlayList(xbmc.PLAYLIST_MUSIC).shuffle()


def play_all():
    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    xbmc.Player().play(playlist)


if page is None:
    get_stations()


elif page == "playlists":
    station_id = args.get("station_id", [""])[0]
    get_playlists(station_id)

elif page == "songs":
    playlist_url = args.get("playlist_url", [""])[0]
    get_songs(playlist_url)

elif page == "play_all":
    play_all()

elif page == "shuffle":
    shuffle()
    play_all()

xbmcplugin.endOfDirectory(addon_handle)
