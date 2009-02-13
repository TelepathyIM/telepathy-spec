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
    def __init__ (self, parent, namespace, dom):
        name = dom.getAttribute ('name')
        self.name = '.'.join (
            filter (lambda n: n is not None,
                    [namespace, name.replace (' ', '')])
            )

        self.parent = parent

    def get_interface (self):
        return self.parent.get_interface ()

    def __repr__ (self):
        return '%s(%s)' % (self.__class__.__name__, self.name)

class Method (base):
    def __init__ (self, parent, namespace, dom):
        super (Method, self).__init__ (parent, namespace, dom)

        args = map (lambda n: Arg (self, None, n),
                         dom.getElementsByTagName ('arg'))

        # separate arguments as input and output arguments
        self.in_args = filter (lambda a: a.direction == Arg.DIRECTION_IN, args)
        self.out_args = filter (lambda a: a.direction == Arg.DIRECTION_OUT, args)

class Property (base): pass

class Arg (base):
    DIRECTION_IN, DIRECTION_OUT = range (2)

    def __init__ (self, parent, namespace, dom):
        super (Arg, self).__init__ (parent, namespace, dom)

        type_ = dom.getAttributeNS (XMLNS_TP, 'type')
        self.type = lookup_type (type_)

        self.dbus_type = dom.getAttribute ('type')

        direction = dom.getAttribute ('direction')
        if direction == 'in':
            self.direction = self.DIRECTION_IN
        elif direction == 'out' or direction == '':
            self.direction = self.DIRECTION_OUT
        else:
            class UnknownDirection (Exception): pass
            raise UnknownDirection ("Unknown direction `%s' on %s" % (
                                    direction, self.parent))

    def __repr__ (self):
        return '%s(%s:%s)' % (self.__class__.__name__, self.name, self.dbus_type)

class Signal (base):
    def __init__ (self, parent, namespace, dom):
        super (Signal, self).__init__ (parent, namespace, dom)

        self.args = map (lambda n: Arg (self, None, n),
                         dom.getElementsByTagName ('arg'))

class Interface (base):
    def __init__ (self, parent, namespace, dom):
        super (Interface, self).__init__ (parent, namespace, dom)

        # build a dictionary of methods in this interface
        self.methods = build_dict (self, Method, self.name,
                                   dom.getElementsByTagName ('method'))
        # build a dictionary of properties in this interface
        self.properties = build_dict (self, Property, self.name,
                                      dom.getElementsByTagName ('property'))
        # build a dictionary of signals in this interface
        self.signals = build_dict (self, Signal, self.name,
                                   dom.getElementsByTagName ('signal'))

        # print '-'*78
        # print self.methods
        # print self.properties
        # print self.signals

    def get_interface (self):
        return self

class Error (base): pass

class DBusType (base):
    """The base class for all D-Bus types referred to in the spec.

       Don't instantiate this class directly.
    """
    pass

class SimpleType (DBusType): pass

class Mapping (DBusType): pass

class Struct (DBusType): pass

class Enum (DBusType): pass

class Flags (DBusType): pass

def lookup_type (type_):
    if type_.endswith ('[]'):
        type_ = type_[:-2]

    if type_ == '': return None
    elif type_ in types:
        return types[type_]

    class UnknownType (Exception): pass

    raise UnknownType ("Type `%s' is unknown" % type_)

def build_dict (parent, type_, namespace, nodes):
    """Build a dictionary of D-Bus names to Python objects representing that
       name using the XML node for that item in the spec.

       e.g. 'org.freedesktop.Telepathy.Channel' : Interface(Channel)

       Works for any Python object inheriting from 'base' whose XML node
       implements the 'name' attribute.
    """

    def build_tuple (node):
        o = type_ (parent, namespace, node)
        return (o.name, o)

    return dict (build_tuple (n) for n in nodes)

def parse_types (parent, dom, d = None):
    """Parse all of the types of type nodes mentioned in 't' from the node
       'dom' and insert them into the dictionary 'd'.
    """
    t = [
        (SimpleType,    'simple-type'),
        (Enum,          'enum'),
        (Flags,         'flags'),
        (Mapping,       'mapping'),
        (Struct,        'struct'),
    ]

    if d is None: d = {}

    for (type_, tagname) in t:
        d.update (build_dict (parent, type_, None,
                    dom.getElementsByTagNameNS (XMLNS_TP, tagname)))

    return d

def parse (filename):
    dom = xml.dom.minidom.parse (filename)
    xincludator.xincludate (dom, filename)

    # build a dictionary of errors in this spec
    errorsnode = dom.getElementsByTagNameNS (XMLNS_TP, 'errors')[0]
    errors.update (build_dict (None, Error,
                    errorsnode.getAttribute ('namespace'),
                    errorsnode.getElementsByTagNameNS (XMLNS_TP, 'error')))
    # build a dictionary of ALL types in this spec
    parse_types (None, dom, types)
    # build a dictionary of interfaces in this spec
    interfaces = build_dict (None, Interface, None,
                             dom.getElementsByTagName ('interface'))

    return interfaces

if __name__ == '__main__':
    parse (sys.argv[1])
