#! /usr/bin/python

import yaml

def main():
    #f = open("data.yaml", "r")
    f = open("dionysus_default.yaml", "r")
    yd = yaml.load(f)
    #print "YAML Data: %s" % str(yd)

    for key in yd:
        print "%s" % key
        print "Type: %s" % str(type(yd[key]))
        print str(yd[key])
        print ""


if __name__ == "__main__":
    main()
