#! /usr/bin/python
import zipfile
import os

def create_directory_structure(root = None, debug = False):
  if root is None:
    raise IOError ("Root is None!")

  mfiles = []
  for root, dirs, files in os.walk(root):
    for d in dirs:
      create_directory_structure(d, debug = debug)

    for f in files:
      fadd = os.path.join(root, f)
      if debug: print "+ %s" % fadd
      mfiles.append(fadd)
 
  return mfiles


if __name__ == "__main__":

  debug = True
  base = os.path.join(os.curdir, "test_folder")
  out_folder = os.curdir
  
  print "Zip test start"
  files = create_directory_structure(root = "./test_folder", debug = debug)
  zf = zipfile.ZipFile("zf.zip", mode="w")

  for f in files:
    if debug: print "Writing: %s" % f
    zf.write(f, os.path.relpath(f, out_folder))

  zf.close()



