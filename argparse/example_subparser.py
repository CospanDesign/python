#! /usr/bin/python

import sys
import argparse
import completer_extractor

DESCRIPTION = "\n" \
"Test Tool\n"

EPILOG = "\n" \
"ppllloooggg\n" + \
"\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers( title = "Tools Title",
                                        description = "Description of Commands",
                                        dest = "tool",
                                        help = 'Sub Tools',
                                        metavar = None)

    parser.add_argument("-d", "--debug", action='store_true', help="Output test debug information")

    a_parser = subparsers.add_parser("A")
    b_parser = subparsers.add_parser("B")

    #print "subparsers: %s" % str(subparsers)

    a_parser.add_argument("-t", "--test", action='store_true', help="Test something")
    b_parser.add_argument("-j", "--jman", action='store_true', help="Test something")

    completer_extractor.completer_extractor(parser)

    '''
    print "Parser:"
    for a in parser._actions:
        if type(a) is argparse._SubParsersAction:
            print "Sub parser"
            sub_dict = a.choices

            for sarg in sub_dict:
                sub_argument = sub_dict[sarg]

                print "\tName: %s " % sarg
                for sa in sub_argument._actions:
                    print "\t\t%s" % str(sa)
            continue

        print "%s" % str(a)

    '''

    sys.exit()
    args = parser.parse_args()
    
    if args.debug:
        debug = True
        print ("Debug Output Enabled")
 
    '''
    if args.verbose:
        print ("Verbose Output Enabled")
    ''' 

    print "dir: %s" % str(args)
    print "sub command: %s" % str(args.tool)

