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
import select
import socket
import Queue


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



class Server(object):
    def __init__(self):
        #Create a TCP/IP Server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)

        #Bind the socket to the port
        server_address = ('localhost', 10001)
        print "Starting up on port %s" % self.server.bind(server_address)

        self.server.listen(5)

        #Sockets to listen for
        self.inputs = [self.server]

        #Sockets in which we expect to write
        self.outputs = []

        #Outgoing message queue
        self.message_queue = {}

    def run(self):
        while self.inputs:
            #Wait for at least one of the sockets to be ready for processing
            print "Waiting for next event"
            readible, writeable, execptional = select.select(self.inputs, self.outputs, self.inputs)
            for s in readible:
                if s is self.server:
                    connection, client_address = s.accept()
                    print "New Connection from: %s" % str(client_address)
                    connection.setblocking(0)
                    self.inputs.append(connection)

                    #Give the connection a queue for data we want to send
                    self.message_queue[connection] = Queue.Queue()

                else:
                    data = s.recv(1024)
                    if data:
                        #A readible client socket has data
                        print "Received: %s fom %s" % (data, s.getpeername())
                        self.message_queue[s].put(data)
                        #Add otuput channel for response
                        if s not in self.outputs:
                            self.outputs.append(s)

                    else:
                        #Interpret empty results as closed sessions
                        print "Closing: %s" % str(client_address)
                        if s in self.outputs:
                            self.outputs.remove(s)
                        self.inputs.remove(s)
                        s.close()

                        del self.message_queue[s]

            for s in writeable:
                try:
                    next_msg = self.message_queue[s].get_nowait()
                except Queue.Empty:
                    print "output Queue for %s is empty" % str(s.getpeername())
                    self.outputs.remove(s)
                else:
                    print "Sending: %s to %s" % (next_msg, str(s.getpeername()))
                    s.send(next_msg)

            for s in execptional:
                print "Handling error for %s" % str(s.getpeername())
                iputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()
                del self.message_queue[s]

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

    server = Server()
    server.run()

if __name__ == "__main__":
    main(sys.argv)


