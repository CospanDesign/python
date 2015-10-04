#! /usr/bin/python

import os
import urllib2
import json
import site_utils

SITE_DIR = "test"
URL_BASE = "http://www.cospandesign.com/nysa/packages"
VERSION_NAME = "versions.json"
TIMEOUT = 2.0

class LocalDefinition(Exception):
    pass

class RemoteDefinition(Exception):
    pass

def get_remote_version(vpath):
    response = urllib2.urlopen(vpath)
    #print "Response: %s" % response.read()
    return response.read()

def get_local_version(vpath):
    #Get a reference to a local version

    if not os.path.exists(vpath):
        #Doesn't exists, create a reference to it
        f = open(vpath, "w")
        f.write("{}")
        f.close()

    f = open(vpath, "r")
    version = f.read()
    f.close()
    return version

def compare_versions(site_dir, entry):
    site_path = os.path.join(site_utils.get_site_base(), site_dir)
    print "Create a site dir: %s" % site_dir
    site_utils.create_site_dir(site_dir)
    remote_version_path = "%s/%s" % (URL_BASE, VERSION_NAME)
    #print "%s" % remote_version_path
    remote_version_raw = get_remote_version(remote_version_path)
    remote_version = json.loads(remote_version_raw)

    if entry not in remote_version:
        raise RemoteDefinition("%s is not within the remote version" % entry)

    local_version_path = os.path.join(site_path, VERSION_NAME)
    local_version_raw = get_local_version(local_version_path)
    local_version = json.loads(local_version_raw)

    if entry not in local_version:
        raise LocalDefinition("%s is not within local version" % entry)

    if local_version[entry] != remote_version[entry]:
        print "Local != Remote: %s != %s" % (local_version[entry], remote_version[entry])
        update_local_version(site_dir, entry, remote_version[entry])
    else:
        print "local and remote are the same"
        


def create_local_entry(site_dir, entry):
    site_path = os.path.join(site_utils.get_site_base(), site_dir)
    local_version_path = os.path.join(site_path, VERSION_NAME)
    local_version_raw = get_local_version(local_version_path)
    local_version = json.loads(local_version_raw)

    if entry not in local_version:
        local_version[entry] = ""
    f = open(local_version_path, "w")
    f.write(json.dumps(local_version))
    f.close()


def update_local_version(site_dir, entry, value):
    site_path = os.path.join(site_utils.get_site_base(), site_dir)
    local_version_path = os.path.join(site_path, VERSION_NAME)
    local_version_raw = get_local_version(local_version_path)
    local_version = json.loads(local_version_raw)

    local_version[entry] = value
    f = open(local_version_path, "w")
    f.write(json.dumps(local_version))
    f.close()



if __name__ == "__main__":
    TEST_NAME = "nysa-verilog"
    create_local_entry(SITE_DIR, TEST_NAME)
    try:
        compare_versions(SITE_DIR, TEST_NAME)
    except LocalDefinition as ex:
        print "%s" % ex




