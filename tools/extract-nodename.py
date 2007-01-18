#!/usr/bin/python

import sys
import xml.dom.minidom

if __name__ == '__main__':
    dom = xml.dom.minidom.parse(sys.argv[1])

    nodes = dom.getElementsByTagName("node")
    assert len(nodes) == 1
    print nodes[0].getAttributeNode("name").nodeValue.replace('/', '')
