#
# Reads in a spec document and generates pretty data structures from it
#

import sys
import xml.dom.minidom

import xincludator

XMLNS_TP = 'http://telepathy.freedesktop.org/wiki/DbusSpec#extensions-v0'

def getText (dom):
    if dom.childNodes[0].nodeType == dom.TEXT_NODE:
        return dom.childNodes[0].data
    else:
        return ''

def getChildrenByName (dom, namespace, name):
    return filter (lambda n: n.nodeType == n.ELEMENT_NODE and \
                             n.namespaceURI == namespace and \
                             n.localName == name,
                   dom.childNodes)

def build_name (namespace, name):
    """Returns a name by appending `name' to the namespace of this object.
    """
    return '.'.join (
        filter (lambda n: n is not None, [namespace, name.replace (' ', '')])
        )

class base (object):
    """The base class for any type of XML node in the spec that implements the
       'name' attribute.

       Don't instantiate this class directly.
    """
    def __init__ (self, parent, namespace, dom):
        self.short_name = name = dom.getAttribute ('name')
        self.namespace = namespace
        self.name = build_name (namespace, name)
        self.parent = parent

        try:
            self.docstring = getChildrenByName (dom, XMLNS_TP, 'docstring')[0]
        except IndexError:
            self.docstring = None

    def get_spec (self):
        return self.parent.get_spec ()

    def get_interface (self):
        return self.parent.get_interface ()

    def get_url (self):
        return "%s#%s" % (self.get_interface ().get_url (), self.name)

    def get_docstring (self):
        """Get the docstring for this node, but do node substitution to
           rewrite types, interfaces, etc. as links.
        """
        if self.docstring is None:
            return ''
        else:
            # make a copy of this node, turn it into a HTML <div> tag
            node = self.docstring.cloneNode (True)
            node.tagName = 'div'
            node.baseURI = None
            node.setAttribute ('class', 'docstring')

            # rewrite <tp:rationale>
            for n in node.getElementsByTagNameNS (XMLNS_TP, 'rationale'):
                n.tagName = 'div'
                n.namespaceURI = None
                n.setAttribute ('class', 'rationale')

            # rewrite <tp:member-ref>
            spec = self.get_spec ()
            interface = self.get_interface ()
            for n in node.getElementsByTagNameNS (XMLNS_TP, 'member-ref'):
                key = getText (n)
                try:
                    o = spec.lookup (key, namespace = interface.name)
                except KeyError:
                    print >> sys.stderr, \
                        "Key `%s' not known in interface `%s'" % (
                            key, interface.name)
                    continue

                n.tagName = 'a'
                n.namespaceURI = None
                n.setAttribute ('href', o.get_url ())
                n.setAttribute ('title', o.get_title ())

            # rewrite <tp:dbus-ref>
            for n in node.getElementsByTagNameNS (XMLNS_TP, 'dbus-ref'):
                namespace = n.getAttribute ('namespace')
                key = getText (n)
                try:
                    o = spec.lookup (key, namespace = namespace)
                except KeyError:
                    print >> sys.stderr, \
                        "Key `%s' not known in namespace `%s'" % (
                            key, namespace)
                    continue

                n.tagName = 'a'
                n.namespaceURI = None
                n.setAttribute ('href', o.get_url ())
                n.setAttribute ('title', o.get_title ())

            return node.toxml ().encode ('ascii', 'xmlcharrefreplace')

    def get_title (self):
        return '%s %s' % (self.__class__.__name__, self.name)

    def __repr__ (self):
        return '%s(%s)' % (self.__class__.__name__, self.name)

class PossibleError (base):
    def __init__ (self, parent, namespace, dom):
        super (PossibleError, self).__init__ (parent, namespace, dom)

class Method (base):
    def __init__ (self, parent, namespace, dom):
        super (Method, self).__init__ (parent, namespace, dom)

        args = build_list (self, Arg, self.name,
                         dom.getElementsByTagName ('arg'))

        # separate arguments as input and output arguments
        self.in_args = filter (lambda a: a.direction == Arg.DIRECTION_IN, args)
        self.out_args = filter (lambda a: a.direction == Arg.DIRECTION_OUT, args)

        self.possible_errors = build_list (self, PossibleError, self.name,
                        dom.getElementsByTagNameNS (XMLNS_TP, 'error'))

    def get_in_args (self):
        return ', '.join (map (lambda a: a.spec_name (), self.in_args))
    def get_out_args (self):
        if len (self.out_args) > 0:
            return ', '.join (map (lambda a: a.spec_name (), self.out_args))
        else:
            return 'nothing'

class Property (base):
    ACCESS_READ     = 0x01
    ACCESS_WRITE    = 0x10
    
    ACCESS_READWRITE = ACCESS_READ | ACCESS_WRITE

    def __init__ (self, parent, namespace, dom):
        super (Property, self).__init__ (parent, namespace, dom)

        type_ = dom.getAttributeNS (XMLNS_TP, 'type')
        self.type = self.get_spec ().lookup_type (type_)

        self.dbus_type = dom.getAttribute ('type')
        
        access = dom.getAttribute ('access')
        if access == 'read':
            self.access = self.ACCESS_READ
        elif access == 'write':
            self.access = self.ACCESS_WRITE
        elif access == 'readwrite':
            self.access = self.ACCESS_READWRITE
        else:
            class UnknownAccess (Exception): pass
            raise UnknownAccess ("Unknown access `%s' on %s" % (
                                    access, self))

    def __repr__ (self):
        return '%s(%s:%s)' % (self.__class__.__name__, self.name, self.dbus_type)

class Arg (base):
    DIRECTION_IN, DIRECTION_OUT = range (2)

    def __init__ (self, parent, namespace, dom):
        super (Arg, self).__init__ (parent, namespace, dom)

        type_ = dom.getAttributeNS (XMLNS_TP, 'type')
        self.type = self.get_spec ().lookup_type (type_)

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

    def spec_name (self):
        return '%s: %s' % (self.dbus_type, self.short_name)

    def __repr__ (self):
        return '%s(%s:%s)' % (self.__class__.__name__, self.name, self.dbus_type)

class Signal (base):
    def __init__ (self, parent, namespace, dom):
        super (Signal, self).__init__ (parent, namespace, dom)

        self.args = build_list (self, Arg, self.name,
                         dom.getElementsByTagName ('arg'))
    
    def get_args (self):
        return ', '.join (map (lambda a: a.spec_name (), self.args))

class Interface (base):
    def __init__ (self, parent, namespace, dom):
        super (Interface, self).__init__ (parent, namespace, dom)

        # build a dictionary of methods in this interface
        self.methods = build_list (self, Method, self.name,
                                   dom.getElementsByTagName ('method'))
        # build a dictionary of properties in this interface
        self.properties = build_list (self, Property, self.name,
                                      dom.getElementsByTagName ('property'))
        # build a dictionary of signals in this interface
        self.signals = build_list (self, Signal, self.name,
                                   dom.getElementsByTagName ('signal'))

        # print '-'*78
        # print self.methods
        # print self.properties
        # print self.signals

    def get_interface (self):
        return self
    
    def get_url (self):
        return "%s.html" % self.name

class Error (base):
    def get_url (self):
        return '#FIXME'

class DBusType (base):
    """The base class for all D-Bus types referred to in the spec.

       Don't instantiate this class directly.
    """

    def get_url (self):
        return '#FIXME'

class SimpleType (DBusType): pass

class Mapping (DBusType): pass

class Struct (DBusType): pass

class Enum (DBusType): pass

class Flags (DBusType): pass

class Spec (object):
    def __init__ (self, dom):
        # build a dictionary of errors in this spec
        errorsnode = dom.getElementsByTagNameNS (XMLNS_TP, 'errors')[0]
        self.errors = build_dict (self, Error,
                        errorsnode.getAttribute ('namespace'),
                        errorsnode.getElementsByTagNameNS (XMLNS_TP, 'error'))
        # build a dictionary of ALL types in this spec
        # FIXME: if we're doing all type parsing here, work out how to associate
        # types with an Interface
        self.types = parse_types (self, dom)
        # build a dictionary of interfaces in this spec
        self.interfaces = build_list (self, Interface, None,
                                 dom.getElementsByTagName ('interface'))

        # build a giant dictionary of everything
        self.everything = {}
        for interface in self.interfaces:
                self.everything[interface.name] = interface

                for method in interface.methods:
                    self.everything[method.name] = method
                for signal in interface.signals:
                    self.everything[signal.name] = signal
                for property in interface.properties:
                    self.everything[property.name] = property

    def get_spec (self):
        return self

    def lookup (self, name, namespace = None):
        key = build_name (namespace, name)
        return self.everything[key]

    def lookup_type (self, type_):
        if type_.endswith ('[]'):
            # FIXME: should this be wrapped in some sort of Array() class?
            return self.lookup_type (type_[:-2])
    
        if type_ == '': return None
        elif type_ in self.types:
            return self.types[type_]
    
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

def build_list (parent, type_, namespace, nodes):
    return map (lambda node: type_ (parent, namespace, node), nodes)

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

    spec = Spec (dom)

    return spec

if __name__ == '__main__':
    parse (sys.argv[1])
