#!/usr/bin/python2.4

import sys

try:
    from elementtree.ElementTree import fromstring, tostring, Element, SubElement
except ImportError:
    print "You need to install ElementTree (http://effbot.org/zone/element-index.htm)"
    sys.exit(1)

import dbus

from xml.dom.minidom import parseString
from telepathy.server import *

copyright = """\
Copyright (C) 2005, 2006 Collabora Limited
Copyright (C) 2005, 2006 Nokia Corporation
Copyright (C) 2006 INdT
"""

license = """\
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

def strip (element):
    if element.text:
        element.text = element.text.strip()
    if element.tail:
        element.tail = element.tail.strip()
    for child in element:
        strip (child)

nameconsts = {}
f = file(sys.argv[2])
for line in f:
    name, const = line.split()
    nameconsts[name] = const

classes = file(sys.argv[1])
for line in classes:
    if line[0] == '#':
        continue
    elif line == '\n':
        continue

    line = line.strip()
    print line
    cls = eval(line)
    bases = (cls, dbus.service.Object)
    # classes half-baked to order... :)
    subclass = type(line, bases, {'__init__':lambda self: None,
                                  '__del__':lambda self: None,
                                  '_object_path':'/'+line,
                                  '_name':line})
    instance = subclass()
    xml = instance.Introspect()

    # sort
    root = fromstring(xml)
    for i, e in enumerate(root):
        if e.get('name') == 'org.freedesktop.DBus.Introspectable':
            del root[i]

    # embrace and extend the D-Bus introspection data, because it only supports
    # annotations which are effectively an attribute value, and we want
    # multi-line docstrings
    root.set('xmlns:tp', 'http://telepathy.freedesktop.org/wiki/DbusSpec#extensions-v0')
    for interface in root:
        interface[:] = sorted(interface[:], key=lambda e: e.get('name'))
        for member in interface:
            SubElement(member, 'tp:docstring').text = '\n%s\n' % getattr(cls, member.get('name')).__doc__
        text = cls.__doc__
        interface.set('tp:name-const', nameconsts[interface.get('name')])
        if text is not None:
            SubElement(interface, 'tp:docstring').text = '\n%s\n' % text
        break
    else:
        # ContactList has no methods
        interface = SubElement(root, 'interface', name=cls._dbus_interfaces[0])
        text = cls.__doc__
        if text is not None:
            SubElement(interface, 'tp:docstring').text = '\n%s\n' % text
        interface.set('tp:name-const', nameconsts[cls._dbus_interfaces[0]])

    basename = root[0].get('name')

    elt = Element('tp:license')
    elt.text = license
    root.insert(0, elt)
    elt = Element('tp:copyright')
    elt.text = copyright
    root.insert(0, elt)

    # pretty print
    strip(root)
    xml = tostring(root)
    dom = parseString(xml)

    basename = basename.replace('org.freedesktop.Telepathy.', '')
    basename = basename.replace('.', '-')
    file = open(basename + '.xml', 'w')
    s = dom.toprettyxml('  ', '\n')
    file.write(s)
    # keep the string splitting here - it stops vim thinking this file
    # is XML!
    file.write('<!-- v''im:set sw=2 sts=2 et ft=xml: -->\n')
    file.close()
