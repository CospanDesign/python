#! /usr/bin/python
import os
import shutil


if __name__ == "__main__":
    out_loc = os.path.dirname(__file__)
    base_dir = os.path.join(os.path.dirname(__file__), "example_dir")
    name = 'test_archive'
    archive_loc = os.path.join(out_loc, name)
    
    print "Hello World!"
    name = shutil.make_archive( base_name = archive_loc,
                                format = 'gztar',
                                base_dir = base_dir)

