# Console SoundCloud Player

A free and open-sourc music player using data from SoundCloud on Raspberry Pi. I use SoundCloud API.

## Requirements
 * vlc client `sudo apt-get install vlc`
 * python 2 and pip `sudo apt-get install python-pip`
 * `soundcloud` python from pip
 * Enable audio module: spot `snd-bcm2835` in /etc/modules entry, remove it and add `dtparam=audio=on` to config.txt (`/boot/config.txt` or `/boot/firmware/config.txt`)

 
## Authentication
You need [SoundCloud API key](http://soundcloud.com/you/apps/new) to play.

# License
[GPLv3](LICENSE) © 2017 Quang Nguyễn