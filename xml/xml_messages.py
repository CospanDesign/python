#! /usr/bin/python

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError



iterator = None


def iterparse_function(path):
    iterator = ET.iterparse(path)
    print "iterator: %s" % str(iterator)
    print "dir: %s" % str(dir (iterator))
    val = None
    try:
        for val in iterator:
            val = iterator.next()
            print "output: %s" % str(val)
    except StopIteration, err:
        print "Stop Iterator at: %s" % str(val)
        print "dir: %s" % str(dir(val))
    
    except ParseError, err:
        print "Parse Error at: %s" % str(err)

    print "Finished"

def parse_xml(path):
    try:
        tree = ET.parse(path)
        print "Tree: %s" % str(tree)
        root = tree.getroot()
    except ParseError, err:
        print "Parse Error at: %s" % str(err)

def sub_process(path, submessages):

    #try:
    tree = ET.parse(path)
    print "Tree: %s" % str(tree)
    root = tree.getroot()
    #except ParseError, err:
    #    print "Parse Error at: %s" % str(err)

    sub_str = open(submessages, "r").readlines()
    print "sub string: %s" % str(sub_str)
    sub_tree = ET.fromstringlist(sub_str)
    print "sub str: %s" % str(sub_tree)
    #ET.SubElement(tree, 
    


if __name__ == "__main__":
    print "XML test"
    #parse_xml("xst.xmsgs")
    #parse_xml("temp.xmsgs")
    #iterparse_function("xst.xmsgs")
    #iterparse_function("temp.xmsgs")

    sub_process("messages.xmsgs", "sub_messages.xmsgs")

    

