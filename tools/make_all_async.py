#!/usr/bin/python2.4

import sys

try:
    from elementtree.ElementTree import fromstring, tostring, ElementTree, Element
except ImportError:
    print "You need to install ElementTree (http://effbot.org/zone/element-index.htm)"
    sys.exit(1)

from xml.dom.minidom import parseString
from telepathy.server import *

import sys

def strip (element):
    if element.text:
        element.text = element.text.strip()
    if element.tail:
        element.tail = element.tail.strip()
    for child in element:
        strip (child)

def annotate(root):
    assert root.tag == 'node'

    for interface_elt in root:
        if interface_elt.tag != 'interface':
            continue
        for method_elt in interface_elt:
            if method_elt.tag != 'method':
                continue
            a_elt = Element('annotation',
                            name='org.freedesktop.DBus.GLib.Async',
                            value='')
            method_elt.insert(0, a_elt)
            #a_elt = Element('annotation',
            #                name='org.freedesktop.DBus.GLib.Const',
            #                value='')
            #method_elt.insert(0, a_elt)

if __name__ == '__main__':
    root = ElementTree(file=sys.argv[1]).getroot()
    annotate(root)

    # pretty print
    strip(root)
    xml = tostring(root)
    dom = parseString(xml)

    output = file(sys.argv[2], 'w')
    output.write(dom.toprettyxml('  ', '\n'))
    output.close()
