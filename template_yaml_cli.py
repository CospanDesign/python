#! /usr/bin/env python3


import sys
import os
import argparse
import yaml

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

DEFAULT_YAML_CONFIG = "config.yaml"

def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )

    parser.add_argument("-c", "--config",
                        nargs=1,
                        default=[DEFAULT_YAML_CONFIG])

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages")

    args = parser.parse_args()
    print ("Running Script: %s" % NAME)


    if args.debug:
        print ("YAML Config File: %s" % str(args.config[0]))

    yconfig = None
    with open(args.config[0]) as f:
        yconfig = yaml.safe_load(f)


    print ("String: %s" % yconfig["test_str"])
    print ("Integer: %d" % yconfig["test_int"])
    print ("Float: %f" % yconfig["test_float"])
    print ("List: %s" % str(yconfig["test_list"]))
    print ("Dict: %s" % str(yconfig["test_dict"]))

if __name__ == "__main__":
    main(sys.argv)


