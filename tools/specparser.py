#
# specparser.py
#
# Reads in a spec document and generates pretty data structures from it.
#
# Copyright (C) 2009 Collabora Ltd.
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or (at
# your option) any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Authors: Davyd Madeley <davyd.madeley@collabora.co.uk>
#

import sys
import xml.dom.minidom

import xincludator

XMLNS_TP = 'http://telepathy.freedesktop.org/wiki/DbusSpec#extensions-v0'

def getText (dom):
    try:
        if dom.childNodes[0].nodeType == dom.TEXT_NODE:
            return dom.childNodes[0].data
        else:
            return ''
    except IndexError:
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
        filter (lambda n: n is not None and n != '',
                [namespace, name.replace (' ', '')])
        )

class Base (object):
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

        try:
            self.added = getChildrenByName (dom, XMLNS_TP, 'added')[0]
        except IndexError:
            self.added = None
        
        try:
            self.deprecated = getChildrenByName (dom, XMLNS_TP, 'deprecated')[0]
        except IndexError:
            self.deprecated = None
    
    def get_type_name (self):
        return self.__class__.__name__

    def get_spec (self):
        return self.parent.get_spec ()

    def get_root_namespace (self):
        return self.get_interface ().name

    def get_interface (self):
        return self.parent.get_interface ()

    def get_url (self):
        return "%s#%s" % (self.get_interface ().get_url (), self.name)

    def get_added (self):
        if self.added is None:
            return ''
        else:
            # make a copy of this node, turn it into a HTML <div> tag
            node = self.added.cloneNode (True)
            node.tagName = 'div'
            node.baseURI = None
            node.setAttribute ('class', 'added')

            try:
                node.removeAttribute ('version')

                span = xml.dom.minidom.parseString (
                    '<span class="version">Added in %s.\n</span>' %
                            self.added.getAttribute ('version')).firstChild
                node.insertBefore (span, node.firstChild)
            except xml.dom.NotFoundErr:
                print >> sys.stderr, \
                    'WARNING: %s was added, but gives no version' % self

            self._convert_to_html (node)

            return node.toxml ().encode ('ascii', 'xmlcharrefreplace')

    def get_deprecated (self):
        if self.deprecated is None:
            return ''
        else:
            # make a copy of this node, turn it into a HTML <div> tag
            node = self.deprecated.cloneNode (True)
            node.tagName = 'div'
            node.baseURI = None
            node.setAttribute ('class', 'deprecated')
            try:
                node.removeAttribute ('version')

                span = xml.dom.minidom.parseString (
                    '<span class="version">Deprecated since %s.\n</span>' %
                            self.deprecated.getAttribute ('version')).firstChild
                node.insertBefore (span, node.firstChild)
            except xml.dom.NotFoundErr:
                print >> sys.stderr, \
                    'WARNING: %s is deprecated, but gives no version' % self

            self._convert_to_html (node)

            return node.toxml ().encode ('ascii', 'xmlcharrefreplace')

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

            self._convert_to_html (node)

            return node.toxml ().encode ('ascii', 'xmlcharrefreplace')
    
    def _convert_to_html (self, node):

        # rewrite <tp:rationale>
        for n in node.getElementsByTagNameNS (XMLNS_TP, 'rationale'):
            n.tagName = 'div'
            n.namespaceURI = None
            n.setAttribute ('class', 'rationale')
    
        # rewrite <tp:member-ref>
        spec = self.get_spec ()
        namespace = self.get_root_namespace ()
        for n in node.getElementsByTagNameNS (XMLNS_TP, 'member-ref'):
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

    def get_title (self):
        return '%s %s' % (self.__class__.__name__, self.name)

    def __repr__ (self):
        return '%s(%s)' % (self.__class__.__name__, self.name)

class PossibleError (Base):
    def __init__ (self, parent, namespace, dom):
        super (PossibleError, self).__init__ (parent, namespace, dom)

    def get_error (self):
        spec = self.get_spec ()
        return spec.errors[self.name]

    def get_url (self):
        return self.get_error ().get_url ()

    def get_title (self):
        return self.get_error ().get_title ()

    def get_docstring (self):
        d = super (PossibleError, self).get_docstring ()
        if d == '':
            return self.get_error ().get_docstring ()
        else:
            return d

class Method (Base):
    def __init__ (self, parent, namespace, dom):
        super (Method, self).__init__ (parent, namespace, dom)

        args = build_list (self, Arg, self.name,
                         dom.getElementsByTagName ('arg'))

        # separate arguments as input and output arguments
        self.in_args = filter (lambda a: a.direction == Arg.DIRECTION_IN, args)
        self.out_args = filter (lambda a: a.direction == Arg.DIRECTION_OUT, args)

        self.possible_errors = build_list (self, PossibleError, None,
                        dom.getElementsByTagNameNS (XMLNS_TP, 'error'))

    def get_in_args (self):
        return ', '.join (map (lambda a: a.spec_name (), self.in_args))
    def get_out_args (self):
        if len (self.out_args) > 0:
            return ', '.join (map (lambda a: a.spec_name (), self.out_args))
        else:
            return 'nothing'

class Typed (Base):
    """The base class for all typed nodes (i.e. Arg and Property).

       Don't instantiate this class directly.
    """
    def __init__ (self, parent, namespace, dom):
        super (Typed, self).__init__ (parent, namespace, dom)

        self.type = dom.getAttributeNS (XMLNS_TP, 'type')
        self.dbus_type = dom.getAttribute ('type')
        
    def get_type (self):
        return self.get_spec ().lookup_type (self.type)

    def get_type_url (self):
        t = self.get_type ()
        if t is None: return ''
        else: return t.get_url ()

    def get_type_title (self):
        t = self.get_type ()
        if t is None: return ''
        else: return t.get_title ()

    def spec_name (self):
        return '%s: %s' % (self.dbus_type, self.short_name)

    def __repr__ (self):
        return '%s(%s:%s)' % (self.__class__.__name__, self.name, self.dbus_type)

class Property (Typed):
    ACCESS_READ     = 1
    ACCESS_WRITE    = 2
    
    ACCESS_READWRITE = ACCESS_READ | ACCESS_WRITE

    def __init__ (self, parent, namespace, dom):
        super (Property, self).__init__ (parent, namespace, dom)

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

    def get_access (self):
        if self.access & self.ACCESS_READ and self.access & self.ACCESS_WRITE:
            return 'Read/Write'
        elif self.access & self.ACCESS_READ:
            return 'Read only'
        elif self.access & self.ACCESS_WRITE:
            return 'Write only'

class Arg (Typed):
    DIRECTION_IN, DIRECTION_OUT = range (2)

    def __init__ (self, parent, namespace, dom):
        super (Arg, self).__init__ (parent, namespace, dom)

        direction = dom.getAttribute ('direction')
        if direction == 'in':
            self.direction = self.DIRECTION_IN
        elif direction == 'out' or direction == '':
            self.direction = self.DIRECTION_OUT
        else:
            class UnknownDirection (Exception): pass
            raise UnknownDirection ("Unknown direction `%s' on %s" % (
                                    direction, self.parent))

class Signal (Base):
    def __init__ (self, parent, namespace, dom):
        super (Signal, self).__init__ (parent, namespace, dom)

        self.args = build_list (self, Arg, self.name,
                         dom.getElementsByTagName ('arg'))
    
    def get_args (self):
        return ', '.join (map (lambda a: a.spec_name (), self.args))

class Interface (Base):
    def __init__ (self, parent, namespace, dom):
        super (Interface, self).__init__ (parent, namespace, dom)

        # build a list of methods in this interface
        self.methods = build_list (self, Method, self.name,
                                   dom.getElementsByTagName ('method'))
        # build a list of properties in this interface
        self.properties = build_list (self, Property, self.name,
                                      dom.getElementsByTagName ('property'))
        # build a list of signals in this interface
        self.signals = build_list (self, Signal, self.name,
                                   dom.getElementsByTagName ('signal'))

        # build a list of types in this interface
        self.types = parse_types (self, dom, self.name)

        # find out if this interface causes havoc
        self.causes_havoc = dom.getAttributeNS (XMLNS_TP, 'causes-havoc')
        if self.causes_havoc == '': self.causes_havoc = None

        # find out what we're required to also implement
        self.requires = map (lambda n: n.getAttribute ('interface'),
                             getChildrenByName (dom, XMLNS_TP, 'requires'))

    def get_interface (self):
        return self

    def get_requires (self):
        spec = self.get_spec ()
        return map (lambda r: spec.lookup (r), self.requires)
    
    def get_url (self):
        return '%s.html' % self.name

class Error (Base):
    def get_url (self):
        return 'errors.html#%s' % self.name
    
    def get_root_namespace (self):
        return self.namespace

class DBusType (Base):
    """The base class for all D-Bus types referred to in the spec.

       Don't instantiate this class directly.
    """
    def __init__ (self, parent, namespace, dom):
        super (DBusType, self).__init__ (parent, namespace, dom)

        self.dbus_type = dom.getAttribute ('type')
    
    def get_root_namespace (self):
        return self.namespace

    def get_breakdown (self):
        return ''

    def get_title (self):
        return "%s %s" % (self.get_type_name (), self.name)

    def get_url (self):
        if isinstance (self.parent, Interface):
            html = self.parent.get_url ()
        else:
            html = 'generic-types.html'

        return '%s#%s' % (html, self.name)

class SimpleType (DBusType):
    def get_type_name (self):
        return 'Simple Type'

class StructLike (DBusType):
    """Base class for all D-Bus types that look kind of like Structs

       Don't instantiate this class directly.
    """
    class StructMember (Typed):
        def get_root_namespace (self):
            return self.parent.get_root_namespace ()
    
    def __init__ (self, parent, namespace, dom):
        super (StructLike, self).__init__ (parent, namespace, dom)
        
        self.members = build_list (self, StructLike.StructMember, None,
                        dom.getElementsByTagNameNS (XMLNS_TP, 'member'))

    def get_breakdown (self):
        str = ''
        str += '<ul>\n'
        for member in self.members:
            # attempt to lookup the member up in the type system
            t = member.get_type ()

            str += '<li>%s &mdash; %s' % (member.name, member.dbus_type)
            if t: str += ' (<a href="%s" title="%s">%s</a>)' % (
                            t.get_url (), t.get_title (), t.short_name)
            str += '</li>\n'
            str += member.get_docstring ()
        str += '</ul>\n'

        return str

class Mapping (StructLike):
    def __init__ (self, parent, namespace, dom):
        super (Mapping, self).__init__ (parent, namespace, dom)
        
        # rewrite the D-Bus type
        self.dbus_type = 'a{%s}' % ''.join (map (lambda m: m.dbus_type, self.members))

class Struct (StructLike):
    def __init__ (self, parent, namespace, dom):
        super (Struct, self).__init__ (parent, namespace, dom)
        
        # rewrite the D-Bus type
        self.dbus_type = '(%s)' % ''.join (map (lambda m: m.dbus_type, self.members))

class EnumLike (DBusType):
    """Base class for all D-Bus types that look kind of like Enums

       Don't instantiate this class directly.
    """
    class EnumValue (Base):
        def __init__ (self, parent, namespace, dom):
            super (EnumLike.EnumValue, self).__init__ (parent, namespace, dom)

            # rewrite self.name
            self.short_name = dom.getAttribute ('suffix')
            self.name = build_name (namespace, self.short_name)

            self.value = dom.getAttribute ('value')
        def get_root_namespace (self):
            return self.parent.get_root_namespace ()

    def get_breakdown (self):
        str = ''
        str += '<ul>\n'
        for value in self.values:
            # attempt to lookup the member.name as a type in the type system
            str += '<li>%s (%s)</li>\n' % (value.short_name, value.value)
            str += value.get_docstring ()
        str += '</ul>\n'

        return str

class Enum (EnumLike):
    def __init__ (self, parent, namespace, dom):
        super (Enum, self).__init__ (parent, namespace, dom)
        
        self.values = build_list (self, EnumLike.EnumValue, self.name,
                        dom.getElementsByTagNameNS (XMLNS_TP, 'enumvalue'))
    
class Flags (EnumLike):
    def __init__ (self, parent, namespace, dom):
        super (Flags, self).__init__ (parent, namespace, dom)
        
        self.values = build_list (self, EnumLike.EnumValue, self.name,
                        dom.getElementsByTagNameNS (XMLNS_TP, 'flag'))
        self.flags = self.values # in case you're looking for it

class Spec (object):
    def __init__ (self, dom):
        # build a dictionary of errors in this spec
        errorsnode = dom.getElementsByTagNameNS (XMLNS_TP, 'errors')[0]
        self.errors = build_dict (self, Error,
                        errorsnode.getAttribute ('namespace'),
                        errorsnode.getElementsByTagNameNS (XMLNS_TP, 'error'))

        # build a list of generic types
        try:
            self.generic_types = parse_types (self,
                    dom.getElementsByTagNameNS (XMLNS_TP, 'generic-types')[0])
        except IndexError:
            self.generic_types = []

        # build a list of interfaces in this spec
        self.interfaces = build_list (self, Interface, None,
                                 dom.getElementsByTagName ('interface'))

        # build a giant dictionary of everything (interfaces, methods, signals
        # and properties); also build a dictionary of types
        self.everything = {}
        self.types = {}

        for type in self.generic_types: self.types[type.short_name] = type

        for interface in self.interfaces:
                self.everything[interface.name] = interface

                for method in interface.methods:
                    self.everything[method.name] = method
                for signal in interface.signals:
                    self.everything[signal.name] = signal
                for property in interface.properties:
                    self.everything[property.name] = property

                for type in interface.types:
                    self.types[type.short_name] = type

        # get some extra bits for the HTML
        node = dom.getElementsByTagNameNS (XMLNS_TP, 'spec')[0]
        self.title = getText (getChildrenByName (node, XMLNS_TP, 'title')[0])
        self.version = getText (getChildrenByName (node, XMLNS_TP, 'version')[0])
        self.copyrights = map (getText,
                               getChildrenByName (node, XMLNS_TP, 'copyright'))

        try:
            license = getChildrenByName (node, XMLNS_TP, 'license')[0]
            license.tagName = 'div'
            license.namespaceURI = None
            license.setAttribute ('class', 'license')
            self.license = license.toxml ()
        except IndexError:
            self.license = ''

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

    def __repr__ (self):
        return '%s(%s)' % (self.__class__.__name__, self.title)

def build_dict (parent, type_, namespace, nodes):
    """Build a dictionary of D-Bus names to Python objects representing that
       name using the XML node for that item in the spec.

       e.g. 'org.freedesktop.Telepathy.Channel' : Interface(Channel)

       Works for any Python object inheriting from 'Base' whose XML node
       implements the 'name' attribute.
    """

    def build_tuple (node):
        o = type_ (parent, namespace, node)
        return (o.name, o)

    return dict (build_tuple (n) for n in nodes)

def build_list (parent, type_, namespace, nodes):
    return map (lambda node: type_ (parent, namespace, node), nodes)

def parse_types (parent, dom, namespace = None):
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

    types = []

    for (type_, tagname) in t:
        types += build_list (parent, type_, namespace,
                    dom.getElementsByTagNameNS (XMLNS_TP, tagname))

    return types

def parse (filename):
    dom = xml.dom.minidom.parse (filename)
    xincludator.xincludate (dom, filename)

    spec = Spec (dom)

    return spec

if __name__ == '__main__':
    parse (sys.argv[1])
