#! /usr/bin/env python3

import subprocess

#my_stdout = subprocess.STDOUT
p = subprocess.check_output(["ls"])
print ("done!: %s" % str(p))

