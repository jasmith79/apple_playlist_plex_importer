import re

from typing import Iterable, Tuple

from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.library import MusicSection
from plexapi.audio import Track

TRACK_NAME_REGEX = re.compile(r"^(?:\d+)?\s*-?\s*(.+)$")
FILE_NAME_REGEX = re.compile(r"(.+)\.\w+$")


def get_plex_server(username: str, password: str, server_name: str) -> PlexServer:
    """Returns the specified plex server of the specified account.

        :param username: The username of the plex account. NOTE: *not* the
            username for the plex *server*, this is what you'd use to
            sign in to e.g. plex.tv or the forums.
        :param password: User password, same deal as above.
        :param server_name: This is the name of the plex server to get a
            connection to.
        :returns: An OO-handle for the Plex Media Server.
    """

    plex_acc = MyPlexAccount(username, password)
    plex_server = plex_acc.resource(server_name).connect()
    return plex_server


def get_plex_music(plex_server: PlexServer) -> MusicSection:
    """Retrieves a view on the music database on the specified plex server.

        :param plex_server: An Object representing the PMS.
        :returns: An Object representing the Music library section.
    """

    plex_music = plex_server.library.section("Music")
    return plex_music


def search_plex_tracks(
        tracks: Iterable[Track],
        apple_title: str,
        apple_album: str,
        apple_artist: str,
        apple_size: int,
    ) -> Tuple[Iterable[Track], Iterable[Track], Iterable[Track]]:
    """Searches through a list of plex tracks for ones that match the
        data provided in the Apple playlist.
        
        :param tracks: List of tracks to search.
        :param apple_title: Title of the track from Apple playlist.
        :param apple_album: Album name of the track from Apple playlist.
        :param apple_artist: Artist name of the track from Apple playlist.
        :param apple_size: Size in bytes of the track from Apple playlist.
        :returns: A Tuple of lists of matches, partials, and name-only matched tracks.
    """

    results = []
    partials = []
    name_only = []
    for track in tracks:
        track_media_part = track.media[0].parts[0]
        file_path = track_media_part.file
        plex_size = track_media_part.size
        parts = file_path.split("/")
        file = parts[-1]
        album_folder = parts[-2].lower()
        match = re.search(FILE_NAME_REGEX, file)
        if match:
            file_name = match.groups()[0].lower()
        else:
            file_name = file.lower()

        plex_title = track.title and re.search(
            TRACK_NAME_REGEX, track.title).groups()[0].lower()
        track_title = re.search(
            TRACK_NAME_REGEX, apple_title).groups()[0].lower()

        # print("{} | {}".format(file_name, apple_title.lower()))
        title_match = (
            (file_name.lower() == apple_title.lower())
            or (track.title.lower() == apple_title.lower())
            or plex_title == track_title
        )

        size_match = str(plex_size) == str(apple_size)
        if title_match or size_match:
            plex_album = track.parentTitle.lower()
            album_match = plex_album in (album_folder, apple_album)
            artist_match = apple_artist.lower() in (
                (track.originalTitle and track.originalTitle.lower()),
                (track.grandparentTitle and track.grandparentTitle.lower()),
            )

            if title_match and size_match and album_match and artist_match:
                results = [track]
                break
            elif title_match and size_match and (album_match or artist_match):
                results.append(track)
            elif size_match and album_match and artist_match:
                results.append(track)
            elif title_match and size_match:
                partials.append(track)
            elif title_match and (album_match or artist_match):
                partials.append(track)
            elif size_match and (album_match or artist_match):
                partials.append(track)
            elif size_match and title_match:
                partials.append(track)
            elif title_match:
                name_only.append(track)
            else:
                pass  # random same size

    return (results, partials, name_only)
