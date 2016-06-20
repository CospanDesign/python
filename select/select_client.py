#! /usr/bin/env python

# Copyright (c) 2016 Dave McCoy (dave.mccoy@cospandesign.com)
#
# NAME is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NAME is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NAME; If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import argparse
import socket

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG = "\n" \
         "\n" \
         "Examples:\n" \
         "\tSomething\n" \
         "\n"


messages = [ 'This is the message. ',
             'It will be send ',
             'in parts.',
           ]

server_address = ('localhost', 10001)

def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )

    parser.add_argument("-t", "--test",
                        nargs=1,
                        default=["something"])

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages")

    args = parser.parse_args()
    print "Running Script: %s" % NAME


    if args.debug:
        print "test: %s" % str(args.test[0])

    socks = [socket.socket(socket.AF_INET, socket.SOCK_STREAM),
             socket.socket(socket.AF_INET, socket.SOCK_STREAM),
            ]

    for s in socks:
        s.connect(server_address)

    for message in messages:
        for s in socks:
            print "%s: Sending: %s" % (s.getsockname(), message)
            s.send(message)

        #Read reponse on both sockets
        for s in socks:
            data = s.recv(1024)
            print "%s: Received: %s" % (s.getsockname(), data)
            if not data:
                print "Closing Socket: %s" % s.getsockname()
                s.close()

    print "Connection to port %s" % server_address


if __name__ == "__main__":
    main(sys.argv)


