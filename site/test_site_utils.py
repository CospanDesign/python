import os
import sys
import site
import site_utils


def test_site_dir_exists():
    result = site_utils.site_dir_exists("test")

def test_create_site_dir():
    site_utils.create_site_dir("test")
    tdir = os.path.join(site.getuserbase(), "test")
    #print "tdir: %s" % str(tdir)
    assert os.path.exists(tdir)
    site_utils._remove_site_dir("test")
    assert not site_utils.site_dir_exists("test")
        

