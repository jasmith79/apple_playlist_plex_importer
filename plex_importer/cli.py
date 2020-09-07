from argparse import ArgumentParser, Namespace
from sys import argv
from typing import Iterable


def parse_args(args: Iterable[str] = argv[1:]) -> Namespace:
    """Parses arguments, defaults to sys.argv"""

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
        help="""Will limit playlist processing to the lists matching 
        the comma-delimited list of playlist names passed to --limit.
        """,
        required=False,
    )

    parser.add_argument(
        "--debug",
        help="Debug output, turns off progress bar.",
        required=False,
    )

    return parser.parse_args(args)
