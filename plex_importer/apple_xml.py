import plistlib
from pathlib import Path
from typing import Tuple, Iterable, Dict, Union


PATHLIKE = Union[str, Path]


def read_apple_xml(path: PATHLIKE) -> Dict:
    """Loads a file as an Apple XML plist.

        :param path: The pathlib.Path or string path.
        :returns: A dictionary created from parsing the XML plist.
    """

    with open(path, "rb") as f_handle:
        plist = plistlib.load(f_handle)
        return plist


def extract_apple_playlists(xml_plist: Dict) -> Iterable[Tuple[str, Iterable[Dict]]]:
    """Extracts the user-defined playlists from the Apple plist.

        :param xml_plist: The parsed XML plist.
        :returns: An Iterable of (playlist_name, playlist_items) tuples.
    """

    playlists = []
    xml_playlists = xml_plist["Playlists"]
    for playlist in xml_playlists:
        keys = playlist.keys()
        if "Master" not in keys and "Distinguished Kind" not in keys:
            playlists.append(
                (playlist["Name"], playlist["Playlist Items"]))

    return playlists
