#! /usr/bin/python

import sys
import site

if __name__ == "__main__":
    #print "Hello, world!"
    #print "Enable user site?: %s" % str(site.ENABLE_USER_SITE)
    #print "Path to user site: %s" % str(site.USER_BASE)
    #print "Site Packages: %s" % str(site.getsitepackages())
    print "User Site Information"
    print "Path to user base (Function): %s" % str(site.getuserbase())
    print "\tThis is where I should store data for my packages"
    print "Get user site packages(): %s" % str(site.getusersitepackages())
