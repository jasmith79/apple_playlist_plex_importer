from argparse import ArgumentParser
from datetime import datetime
from getpass import getpass
from sys import argv
from typing import Dict, Iterable

from plexapi.audio import Track

from plex_importer.apple_xml import read_apple_xml, extract_apple_playlists
from plex_importer.plex import get_plex_music, get_plex_server, search_plex_tracks

START = datetime.now()
PLEX_TRACK_CACHE = {}


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

            else:
                print("Cannot find even a name match for {}/{}/{}, skipping".format(
                    artist,
                    apple_album,
                    track_name,
                ))

    return playlist_tracks


def main():
    """Main fn."""

    parser = ArgumentParser()
    parser.add_argument(
        "apple_xml",
        help="Path to the apple xml file.",
    )

    parser.add_argument(
        "--user",
        help="User name for the plex account.",
        required=False,
    )

    parser.add_argument(
        "--password",
        help="Password for the plex account.",
        required=False,
    )

    parser.add_argument(
        "--server",
        help="The name of the plex server to create lists on.",
        required=False,
    )

    parser.add_argument(
        "--limit",
        help="Will limit playlist processing to the list matching the name passed to --limit.",
        required=False,
    )

    print("Gathering prerequisites...")
    args = parser.parse_args(argv[1:])
    user = args.user or input("Please enter your plex account username:")
    password = args.password or getpass("Please enter your plex account password:")
    server = args.server or input("Please enter your plex server name:")

    print("Connecting...")
    plex_server = get_plex_server(user, password, server)
    print("Retrieving Music Section...")
    plex_music = get_plex_music(plex_server)
    print("Reading xml file...")
    appl_xml = read_apple_xml(args.apple_xml)
    appl_playlists = extract_apple_playlists(appl_xml)
    if args.limit:
        appl_playlists = [
            x for x in appl_playlists if x[0] == args.limit
        ]

    print("Getting tracks...")
    plex_tracks = list(plex_music.searchTracks())
    for list_name, list_items in appl_playlists:
        apple_tracks = [
            appl_xml["Tracks"][str(item["Track ID"])] for item in list_items
        ]
        results = process_apple_list(apple_tracks, plex_tracks)
        print("Have results, creating list {} on server".format(list_name))
        plex_server.createPlaylist(list_name, results)
        print("done.")

    print("Done. Created {} playlists on {} in {} seconds.".format(
        str(len(appl_playlists)),
        server,
        str((datetime.now() - START).seconds),
    ))


if __name__ == "__main__":
    main()
