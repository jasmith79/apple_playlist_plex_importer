# apple_playlist_plex_importer

Imports Apple Playlists into Plex Media Server. Note that this is an imperfect process. It *should* work on older iTunes XML files, but I've only tested it on Catalina (latest Music), Mojave (latest iTunes), and Windows 10 (latest iTunes). It *should* work on just about any host OS for PMS, but I've only tested on a Synology NAS (i.e. Linux).

To work at all a few things are required:

1. An Apple music library XML file (File -> Library -> Export library in the Music app or iTunes).
2. Credentials for your Plex Account (your plex.tv account, NOT your account on the server).
3. The name of your Plex Server.

Additionally, some steps while not strictly required will make it work much more reliably:

1. In your Plex Server settings under Agents move "Local Media Assets" to the top of the list for both Artists and Albums. This will reduce the amount of renaming of your media files that Plex does, making it easier to match to the Apple playlist tracks. Be sure to refresh the metadata after doing this.
2. Double-check the output in the terminal when running the importer. If it can't match a track, then the problem is almost certainly that the plex name is different than the Apple name, and you should rename the track(s)/album(s)/artist(s). This is more true the more non-English non-ASCII your collection is. I have a lot of Japanese, Scandanavian, and Latin character-having artists/tracks in my collection but ended up only having to manually rename one artist after doing step 1.

## Installing

You can clone this repository, install the plexapi package dependency, and run app.py in the importer package but I recommend installing through pip:

```
python3 -m pip install --user git+https://github.com/jasmith79/apple_playlist_plex_importer.git
```

## Usage

Open up a terminal and (assuming you installed via pip) run the command:

```
pleximport path/to/library.xml --user myplexuser --password myplexpassword --server myplexserver
```

For those of you worried about having passwords in your shell history, you can omit anything except the file path and it will interactively prompt you for them. If you only want to run it against a specific playlist you can use the `--limit` flag. See `--help` as well.

## Known Issues:

1. It can take a significant amount of time for PMS to optimize all of those playlists. Don't be too concerned if you try to access them right away and get some sort of "failed to load" error message.
2. If you don't have any existing music playlists you will have to reload the page/restart the client app to get the playlists menu option to show in the Plex client.
3. As I said the name matching is not perfect and was *shockingly* difficult to implement with even decent reliability. Probably the reason the Plex team didn't do it.
4. Playlist items will always fail to load for me the first week or so even though the playlist plays just fine. One of the weekly background tasks seems to fix this.
