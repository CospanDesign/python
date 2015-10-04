#!/usr/bin/python


'''
Download the python module here:

http://www.abisource.com/download/
'''

import argparse
import sys
import os
import enchant
import string

DESCRIPTION = "\n" \
"\n"\
"Checks spelling within a file\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tspell_check.py 'test_file.txt'\n" \
"\t\tcheck test_file.txt for spelling errors\n"\
"\n"



def main():
    parser = argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = DESCRIPTION,
            epilog = EPILOG)

    debug = False

    parser.add_argument("-d", "--debug",
                        action = "store_true",
                        help = "Enable Helpful Debug Messages")

    parser.add_argument("in_file",
                        nargs = 1,
                        type = str,
                        help = "Specify the file to check")


    args = parser.parse_args()

    if args.debug:
        print ("Debug Enable")
        debug = True


    if debug: print "Openning file: %s" % args.in_file[0]
    f = open(args.in_file[0], 'r')
    data = f.read()

    if debug: print "Getting an instance of a dictionary..."
    d = enchant.DictWithPWL("en_US")

    if debug: print "Adding a custom name"
    name = "yingzi"
    d.add(name)
    if debug: print "Checking if the custom name we just entered is in the dictioary..."
    print "\tis %s in the personal dictionary: %s" % (name, d.is_added(name))
    if debug: print "Checking if a random custom name is in the dictioary..."
    print "\tis %s in the personal dictionary: %s" % ("bob", d.is_added("bob"))

    if debug: print "Splitting up text in document to a list of signal words"
    words = data.split(" ")

    if debug: print "Go through each word and see if it is correct"
    error_count = 0
    for word in words:
        #Remove white spaces
        word = word.strip()
        word = string.strip(word, string.punctuation)
        if not d.check(word) and not d.is_added(word):
            print "%s is incorrect, possible alternatives:" % word
            for w in d.suggest(word):
                print "\t%s" % w

if __name__ == "__main__":
    main()
