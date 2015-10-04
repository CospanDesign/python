#! /usr/bin/python

import os
import sys
import site
import shutil



def site_dir_exists(dirname):
    udir = os.path.join(site.getuserbase(), dirname)
    return os.path.exists(udir)

def create_site_dir(dirname):
    udir = os.path.join(site.getuserbase(), dirname)
    if not site_dir_exists(dirname):
        os.makedirs(udir)

def _remove_site_dir(dirname):
    udir = os.path.join(site.getuserbase(), dirname)
    if site_dir_exists(udir):
        #print "Removing dirs..."
        shutil.rmtree(udir)
        #print "done!"

def get_site_base():
    return site.getuserbase()

