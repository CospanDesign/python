#! /usr/bin/python

# Copyright (c) 2015 Dave McCoy (dave.mccoy@cospandesign.com)
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import argparse

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG = "\n" \
         "\n" \
         "Examples:\n" \
         "\t%s \n" \
         "\n"

debug = False

GITHUB_REPO_URL_FILE = "github_repo_url.txt"

def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages",
                        )
    parser.add_argument("url",
                        type = str,
                        nargs = '?',
                        default = None,
                        help="Specify the URL, if left blank, the script will attempt to read the URL from a file in the same directory with the name: %s" % GITHUB_REPO_URL_FILE)

    args = parser.parse_args()
    url_path = None

    try:
        f = open (GITHUB_REPO_URL_FILE, "r")
        url_path = f.read().strip()
        print "Found URL Path in configuration file: %s" % url_path
    except IOError as err:
        pass

    print "Running Script: %s" % NAME


if __name__ == "__main__":
    main(sys.argv)


