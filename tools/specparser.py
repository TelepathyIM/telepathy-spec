#
# Reads in a spec document and generates pretty data structures from it
#

import sys
import xml.dom.minidom

import xincludator

XMLNS_TP = 'http://telepathy.freedesktop.org/wiki/DbusSpec#extensions-v0'

# dictionaries for global errors and types
errors = {}
types = {}

class base (object):
    """The base class for any type of XML node in the spec that implements the
       'name' attribute.

       Don't instantiate this class directly.
    """
    def __init__ (self, namespace, dom):
        name = dom.getAttribute ('name')
        self.name = '.'.join (
            filter (lambda n: n is not None,
                    [namespace, name.replace (' ', '')])
            )
    
    def __repr__ (self):
        return '%s(%s)' % (self.__class__.__name__, self.name)

class Method (base): pass

class Property (base): pass

class Signal (base): pass

class Interface (base):
    def __init__ (self, namespace, dom):
        super (Interface, self).__init__ (namespace, dom)

        # build a dictionary of methods in this spec
        self.methods = build_dict (Method, self.name,
                                   dom.getElementsByTagName ('method'))
        # build a dictionary of properties in this spec
        self.properties = build_dict (Property, self.name,
                                      dom.getElementsByTagName ('property'))
        # build a dictionary of signals in this spec
        self.signals = build_dict (Signal, self.name,
                                   dom.getElementsByTagName ('signal'))

        # print '-'*78
        # print self.methods
        # print self.properties
        # print self.signals

class Error (base): pass

class DBusType (base):
    """The base class for all D-Bus types referred to in the spec.

       Don't instantiate this class directly.
    """
    pass

class SimpleType (DBusType): pass

class Mapping (DBusType): pass

def build_dict (type_, namespace, nodes):
    """Build a dictionary of D-Bus names to Python objects representing that
       name using the XML node for that item in the spec.

       e.g. 'org.freedesktop.Telepathy.Channel' : Interface(Channel)

       Works for any Python object inheriting from 'base' whose XML node
       implements the 'name' attribute.
    """

    def build_tuple (node):
        o = type_ (namespace, node)
        return (o.name, o)

    return dict (build_tuple (n) for n in nodes)

def parse (filename):
    dom = xml.dom.minidom.parse (filename)
    xincludator.xincludate (dom, filename)

    # build a dictionary of errors in this spec
    errorsnode = dom.getElementsByTagNameNS (XMLNS_TP, 'errors')[0]
    errors.update (build_dict (Error, errorsnode.getAttribute ('namespace'),
                         errorsnode.getElementsByTagNameNS (XMLNS_TP, 'error')))
    # build a dictionary of types in this spec
    typesnode = dom.getElementsByTagNameNS (XMLNS_TP, 'generic-types')[0]
    types.update (build_dict (SimpleType, None,
                    typesnode.getElementsByTagNameNS (XMLNS_TP, 'simple-type')))
    types.update (build_dict (Mapping, None,
                    typesnode.getElementsByTagNameNS (XMLNS_TP, 'mapping')))
    # build a dictionary of interfaces in this spec
    interfaces = build_dict (Interface, None,
                             dom.getElementsByTagName ('interface'))

    return interfaces

if __name__ == '__main__':
    parse (sys.argv[1])
