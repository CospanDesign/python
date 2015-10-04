#! /usr/bin/python

import subprocess

#my_stdout = subprocess.STDOUT
p = subprocess.check_output(["ls"])
print "done!: %s" % str(p)

