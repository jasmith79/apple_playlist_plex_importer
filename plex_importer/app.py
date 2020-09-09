from datetime import datetime
from getpass import getpass
from typing import Dict, Iterable

from plexapi.audio import Track
from tqdm import tqdm

from plex_importer.apple_xml import read_apple_xml, extract_apple_playlists
from plex_importer.plex import get_plex_music, get_plex_server, search_plex_tracks
from plex_importer.cli import parse_args

START = datetime.now()
PLEX_TRACK_CACHE = {}
DEBUG = []


def process_apple_list(
        apple_list: Iterable[Dict],
        plex_tracks: Iterable[Track],
    ) -> Iterable[Track]:
    """Converts an Apple playlist into a list of Plex tracks.

        :param apple_list: List of Apple track records.
        :param plex_tracks: List of all Plex tracks.
        :returns: A list of the Plex tracks matching the Apple tracks.
    """

    playlist_tracks = []
    for item in apple_list:
        apple_track_id = str(item["Track ID"])
        apple_artist = item.get("Artist")
        track_name = item["Name"]
        apple_album_artist = item.get("Album Artist")
        apple_album = item.get("Album")
        artist = apple_artist or apple_album_artist or ""
        plex_track = PLEX_TRACK_CACHE.get(apple_track_id)

        if plex_track:
            playlist_tracks.append(plex_track)
        else:
            results, partials, name_only = search_plex_tracks(
                plex_tracks,
                track_name,
                apple_album,
                artist,
                item.get("Size"),
            )

            if results:
                if len(results) == 1:
                    PLEX_TRACK_CACHE[apple_track_id] = results[0]
                    playlist_tracks.append(results[0])
                else:
                    if DEBUG:
                        print("Multiple matches for {}/{}/{}".format(
                            artist,
                            apple_album,
                            track_name,
                        ))
                    playlist_tracks.append(results[0])

            elif partials:
                PLEX_TRACK_CACHE[apple_track_id] = partials[0]
                playlist_tracks.append(partials[0])

            elif name_only:
                pass

            elif DEBUG:
                print("Cannot find even a name match for {}/{}/{}, skipping".format(
                    artist,
                    apple_album,
                    track_name,
                ))
            else:
                pass

    return playlist_tracks


def main():
    """Main fn."""

    print("Gathering prerequisites...")
    args = parse_args()
    user = args.user or input("Please enter your plex account username:")
    password = args.password or getpass("Please enter your plex account password:")
    server = args.server or input("Please enter your plex server name:")
    if args.debug:
        DEBUG.append(True)

    print("Connecting...")
    plex_server = get_plex_server(user, password, server)
    print("Retrieving Music Section...")
    plex_music = get_plex_music(plex_server)
    print("Reading xml file...")
    appl_xml = read_apple_xml(args.apple_xml)
    appl_playlists = extract_apple_playlists(appl_xml)
    if args.limit:
        filter_list = args.limit.split(",")
        appl_playlists = [
            x for x in appl_playlists if x[0] in filter_list
        ]
        assert appl_playlists, "No playlists matched filter '{}'".format(args.limit)

    print("Getting tracks...")
    plex_tracks = list(plex_music.searchTracks())
    pbar = tqdm(appl_playlists)

    # Debug printing will mess up the progress bar, turn it off if debugging.
    if DEBUG:
        pbar = appl_playlists

    for list_name, list_items in pbar:
        pbar.set_description("Processing list {}".format(list_name).ljust(35))
        apple_tracks = [
            appl_xml["Tracks"][str(item["Track ID"])] for item in list_items
        ]
        results = process_apple_list(apple_tracks, plex_tracks)
        pbar.set_description("Have results, creating list {} on server".format(list_name))
        try:
            plex_server.createPlaylist(list_name, results)
        except IndexError: # Empty list? plexapi throws this.
            if DEBUG:
                print("Unable to create playlist {}, empty? {}".format(
                    list_name,
                    str(bool(list_items)),
                ))

    print("Done. Created {} playlists on {} in {} seconds.".format(
        str(len(appl_playlists)),
        server,
        str((datetime.now() - START).seconds),
    ))


if __name__ == "__main__":
    main()
