# Copyright (C) 2017 Quang Nguyen http://develbranch.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import soundcloud
import getopt
import requests
import shutil
import subprocess
import json
import time
import random


class SoundCloudPlayer():
    def __init__(self, client_id=None, client_secret=None, shuffle_tracks=False):
        self.tmp_file = '/tmp/now_playing_file.mp3'
        self.shuffle = shuffle_tracks

        if client_id is None:
            if 'SOUNDCLOUD_CLIENT_ID' not in os.environ:
                raise Exception("Set client id to run")
            client_id = os.environ['SOUNDCLOUD_CLIENT_ID']
        if client_secret is None and 'SOUNDCLOUD_CLIENT_SECRET' in os.environ:
            client_secret = os.environ['SOUNDCLOUD_CLIENT_SECRET']
        self.client = soundcloud.Client(client_id=client_id, client_secret=client_secret)

    def logmsg(self, msg):
        print msg

    def download(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5', 'DNT': '1', 'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        response = requests.get(url, headers=headers, stream=True)
        out_file = open(self.tmp_file, 'wb', 0)
        shutil.copyfileobj(response.raw, out_file)
        out_file.flush()
        out_file.close()
        del response

    def play(self):
        cmd = 'vlc -I dummy ' + self.tmp_file + ' vlc://quit >/dev/null 2>&1'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        p.wait()

    def resolve(self, uri):
        try:
            r = self.client.get('http://api.soundcloud.com/resolve?url=%s' % uri)
            data = json.loads(r.raw_data)
            return data['kind'], data['id']
        except:
            return None, None

    def get_track_location(self, uri):
        try:
            # fetch track to stream
            track = self.client.get(uri)

            # get the tracks streaming URL
            stream_url = self.client.get(track.stream_url, allow_redirects=False)

            # print the tracks stream URL
            return stream_url.location
        except Exception as e:
            self.logmsg(str(e))
            return None

    def play_uri(self, uri):
        url = self.get_track_location(uri)
        if url is None:
            return
        if os.path.exists(self.tmp_file):
            os.remove(self.tmp_file)
            time.sleep(1)
        for i in range(5):
            self.download(url)
            if os.path.exists(self.tmp_file):
                break
        self.play()
        os.remove(self.tmp_file)
        time.sleep(2)

    def play_a_track(self, soundcloud_id):
        url = 'https://api.soundcloud.com/tracks/%s' % soundcloud_id
        self.play_uri(url)

    def play_user_tracks(self, soundcloud_id):
        # fetch user tracks
        tracks = json.loads(self.client.get('/users/%s/tracks' % soundcloud_id).raw_data)
        if self.shuffle:
            random.shuffle(tracks)
        for track in tracks:
            if track['kind'] == 'track':
                print track['created_at'], track['uri']
                self.play_uri(track['uri'])

    def play_playlist(self, soundcloud_id):
        # fetch playlist
        playlist = self.client.get('playlists/%s' % soundcloud_id)
        # list tracks in playlist
        tracks = playlist.tracks
        if self.shuffle:
            random.shuffle(tracks)
        for track in tracks:
            print track['title'], track['uri']
            self.play_uri(track['uri'])

    def kind_not_found(self, soundcloud_id):
        print 'Unplayable URI'

    def play_soundcloud_url(self, url):
        kind, soundcloud_id = self.resolve(url)
        f = {
            'user': self.play_user_tracks,
            'playlist': self.play_playlist,
            'track': self.play_a_track
        }.get(kind, self.kind_not_found)(soundcloud_id)  # default if kind not found


def usage():
    print "Console SoundClound Player"
    print "Developed by quangnh89."
    print "Copyright 2017, GPLv3"
    print
    print sys.argv[0], '[-c client_id] [-s client_secret] url1 [url2 [...] ]'
    print '-h Show this message'
    print '-c Set client ID, or set SOUNDCLOUD_CLIENT_ID environment variable'
    print '-k Set client secret, or set SOUNDCLOUD_CLIENT_SECRET environment variable'
    print '-s shuffle all tracks'
    sys.exit(0)


if __name__ == "__main__":
    client_id = None
    client_secret = None
    shuffle_tracks = False
    opts, args = getopt.getopt(sys.argv[1:], "hc:k:s", ["help", "client-id=", "client-secret=", "shuffle"])
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        if opt in ("-c", "--client-id"):
            client_id = arg
        if opt in ("-k", "--client-secret"):
            client_secret = arg
        if opt in ("-s", "--shuffle"):
            shuffle_tracks = True

    scp = SoundCloudPlayer(client_id, client_secret, shuffle_tracks)
    for a in args:
        scp.play_soundcloud_url(a)
