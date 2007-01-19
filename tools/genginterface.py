#!/usr/bin/python

import sys
import os.path
import xml.dom.minidom
import dbus

def cmdline_error():
    print "usage: gen-ginterface xmlfile classname [output_basename]"
    sys.exit(1)

def camelcase_to_lower(s):
    out ="";
    out += s[0].lower()
    last_upper=False
    if s[0].isupper():
        last_upper=True
    for i in range(1,len(s)):
        if s[i].isupper():
            if last_upper:
                if (i+1) < len(s) and  s[i+1].islower():
                    out += "_" + s[i].lower()
                else:
                    out += s[i].lower()
            else:
                out += "_" + s[i].lower()
            last_upper=True
        else:
            out += s[i]
            last_upper=False
    return out

def camelcase_to_upper(s):
    return camelcase_to_lower(s).upper()

def type_to_gtype(s):
    if s == 'y': #byte
        return ("guchar ", "G_TYPE_UCHAR","UCHAR", False)
    elif s == 'b': #boolean
        return ("gboolean ", "G_TYPE_BOOLEAN","BOOLEAN", False)
    elif s == 'n': #int16
        return ("gint ", "G_TYPE_INT","INT", False)
    elif s == 'q': #uint16
        return ("guint ", "G_TYPE_UINT","UINT", False)
    elif s == 'i': #int32
        return ("gint ", "G_TYPE_INT","INT", False)
    elif s == 'u': #uint32
        return ("guint ", "G_TYPE_UINT","UINT", False)
    elif s == 'x': #int64
        return ("gint ", "G_TYPE_INT64","INT64", False)
    elif s == 't': #uint32
        return ("guint ", "G_TYPE_UINT64","UINT64", False)
    elif s == 'd': #double
        return ("gdouble ", "G_TYPE_DOUBLE","DOUBLE", False)
    elif s == 's': #string
        return ("gchar *", "G_TYPE_STRING", "STRING", True)
    elif s == 'g': #signature - FIXME
        return ("gchar *", "DBUS_TYPE_G_SIGNATURE", "STRING", True)
    elif s == 'o': #object path
        return ("gchar *", "DBUS_TYPE_G_OBJECT_PATH", "STRING", True)
    elif s == 'v':  #variant
        return ("GValue *", "G_TYPE_VALUE", "BOXED", True)
    elif s == 'as':  #array of strings
        return ("gchar **", "G_TYPE_STRV", "BOXED", True)
    elif s == 'ay': #byte array
        return ("GArray *", "DBUS_TYPE_G_BYTE_ARRAY", "BOXED", True)
    elif s == 'au': #uint array
        return ("GArray *", "DBUS_TYPE_G_UINT_ARRAY", "BOXED", True)
    elif s == 'ai': #int array
        return ("GArray *", "DBUS_TYPE_G_INT_ARRAY", "BOXED", True)
    elif s == 'ax': #int64 array
        return ("GArray *", "DBUS_TYPE_G_INT64_ARRAY", "BOXED", True)
    elif s == 'at': #uint64 array
        return ("GArray *", "DBUS_TYPE_G_UINT64_ARRAY", "BOXED", True)
    elif s == 'ad': #double array
        return ("GArray *", "DBUS_TYPE_G_DOUBLE_ARRAY", "BOXED", True)
    elif s == 'ab': #boolean array
        return ("GArray *", "DBUS_TYPE_G_BOOLEAN_ARRAY", "BOXED", True)
    elif s[:2] == 'a(': #array of structs, recurse
        gtype = type_to_gtype(s[1:])[1]
        return ("GPtrArray *", "(dbus_g_type_get_collection (\"GPtrArray\", "+gtype+"))", "BOXED", True)
    elif s == 'a{ss}': #hash table of string to string
        return ("GHashTable *", "DBUS_TYPE_G_STRING_STRING_HASHTABLE", "BOXED", False)
    elif s[:2] == 'a{':  #some arbitrary hash tables
        if s[2] not in ('y', 'b', 'n', 'q', 'i', 'u', 's', 'o', 'g'):
            raise Exception, "can't index a hashtable off non-basic type " + s
        first = type_to_gtype(s[2])
        second = type_to_gtype(s[3:-1])
        return ("GHashTable *", "(dbus_g_type_get_map (\"GHashTable\", " + first[1] + ", " + second[1] + "))", "BOXED", False)
    elif s[:1] == '(': #struct
        gtype = "(dbus_g_type_get_struct (\"GValueArray\", "
        for subsig in dbus.Signature(s[1:-1]):
            gtype = gtype + type_to_gtype(subsig)[1] + ", "
        gtype = gtype + "G_TYPE_INVALID))"
        return ("GValueArray *", gtype, "BOXED", True)

    # we just don't know ..
    raise Exception, "don't know the GType for " + s


def signal_to_marshal_type(signal):
    """
    return a list of strings indicating the marshalling type for this signal.
    """

    mtype=[]
    for i in signal.getElementsByTagName("arg"):
        name =i.getAttribute("name")
        type = i.getAttribute("type")
        mtype.append(type_to_gtype(type)[2])

    return mtype

def signal_to_marshal_name(signal, prefix):
    glib_marshallers = set(['VOID', 'BOOLEAN', 'CHAR', 'UCHAR', 'INT',
            'STRING', 'UINT', 'LONG', 'ULONG', 'ENUM', 'FLAGS', 'FLOAT',
            'DOUBLE', 'STRING', 'PARAM', 'BOXED', 'POINTER', 'OBJECT',
            'UINT_POINTER'])

    mtype = signal_to_marshal_type(signal)
    if len(mtype):
        name = '_'.join(mtype)
    else:
        name = 'VOID'

    if name in glib_marshallers:
        return 'g_cclosure_marshal_VOID__' + name
    else:
        return prefix + '_marshal_VOID__' + name

def signal_to_gtype_list(signal):
    gtype=[]
    for i in signal.getElementsByTagName("arg"):
        name =i.getAttribute("name")
        type = i.getAttribute("type")
        gtype.append(type_to_gtype(type)[1])

    return gtype


def print_license(stream, filename, description):
    stream.write(
"""/*
 * %s - %s
 * Copyright (C) 2005 Collabora Ltd.
 * Copyright (C) 2005 Nokia Corporation
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

""" % (filename, description))

def print_header_begin(stream, prefix):
    guardname = '__'+prefix.upper()+'_H__'
    stream.write ("#ifndef "+guardname+"\n")
    stream.write ("#define "+guardname+"\n\n")

    stream.write ("#include <glib-object.h>\n\n")
    stream.write ("G_BEGIN_DECLS\n\n")

def print_header_end(stream, prefix):
    guardname = '__'+prefix.upper()+'_H__'
    stream.write ("\nG_END_DECLS\n\n")
    stream.write ("#endif /* #ifndef "+guardname+"*/\n")

def print_class_defn(stream, prefix, classname, methods):
    stream.write ("/* dummy struct representing any implementation */\n")
    stream.write ("typedef struct _%s %s;\n" % (classname,classname))
    stream.write ("typedef struct _%sClass %sClass;\n\n" % (classname,classname))
    stream.write ("struct _%sClass {\n" % classname)
    stream.write ("    GObjectClass parent_class;\n")

    for method in methods:
        m, h, b = do_method(method)
        stream.write(m)

    stream.write ("};\n\n")

    stream.write(
"""
GType %(prefix)s_get_type(void);

""" % {'prefix':prefix,'uprefix':prefix.upper()})

    macro_prefix = prefix.upper().split('_',1)
    gtype = '_TYPE_'.join(macro_prefix)

    stream.write(
"""/* TYPE MACROS */
#define %(type)s \\
  (%(prefix)s_get_type())
#define %(main)s_%(sub)s(obj) \\
  (G_TYPE_CHECK_INSTANCE_CAST((obj), %(type)s, %(name)s))
#define %(main)s_%(sub)s_CLASS(klass) \\
  (G_TYPE_CHECK_CLASS_CAST((klass), %(type)s, %(name)sClass))
#define %(main)s_IS_%(sub)s(obj) \\
  (G_TYPE_CHECK_INSTANCE_TYPE((obj), %(type)s))
#define %(main)s_IS_%(sub)s_CLASS(klass) \\
  (G_TYPE_CHECK_CLASS_TYPE((klass), %(type)s))
#define %(main)s_%(sub)s_GET_CLASS(obj) \\
  (G_TYPE_INSTANCE_GET_INTERFACE ((obj), %(type)s, %(name)sClass))

""" % {"main":macro_prefix[0], "sub":macro_prefix[1], "type":gtype, "name":classname, "prefix":prefix})
 

def signal_emit_stub(signal):
    dbus_name = signal.getAttributeNode("name").nodeValue
    c_emitter_name = prefix + '_emit_' + camelcase_to_lower(dbus_name)
    c_signal_name = (prefix + '_' + camelcase_to_lower(dbus_name)).replace('_','-')

    decl = 'void ' + c_emitter_name + ' (' + classname + ' *self'
    args = ''

    for i in signal.getElementsByTagName("arg"):
        name = i.getAttribute("name")
        type = i.getAttribute("type")
        info = type_to_gtype(type)
        gtype = info[0]
        if gtype[3]:
            gtype = 'const ' + gtype
        decl += ',\n    ' + gtype + ' ' + name
        args += ', ' + name
    decl += ')'

    header = decl + ';\n\n'
    body = decl + ('\n{\n  g_signal_emit_by_name (self, "%s"%s);\n}\n\n'
                   % (c_signal_name, args))
    return header, body


def do_method(method):
    dbus_method_name = method.getAttributeNode("name").nodeValue
    c_method_name = prefix + '_' + camelcase_to_lower(dbus_method_name)
    ret_method_name = prefix + '_return_from_' + camelcase_to_lower(dbus_method_name)
    async=True
    ret_count=0

    header = ''
    body = ''

    #for i in method.getElementsByTagName("annotation"):
    #    if i.getAttribute("name") == "org.freedesktop.DBus.GLib.Async":
    #        async=True

    if async:
        c_decl = "void\n"
        method_decl = "  void (*" + camelcase_to_lower(dbus_method_name) + ') ('
        ret_decl = 'static inline void\n'
        ret_body = '{\n  dbus_g_method_return (dbus_context'
    else:
        c_decl = "gboolean\n"
        method_decl = "  gboolean (*" + camelcase_to_lower(dbus_method_name) + ') ('
        ret_decl = ''
        ret_call = ''

    tmp = c_method_name+' ('
    pad = ' ' * len(tmp)
    c_decl += tmp+classname+' *self'

    method_pad = ' ' * len(method_decl)
    method_decl += classname + ' *'
    args = 'self'

    if async:
        tmp = ret_method_name+' ('
        ret_pad = ' ' * len(tmp)
        ret_decl += tmp+'DBusGMethodInvocation *dbus_context'

    for i in method.getElementsByTagName("arg"):
        name =i.getAttribute("name")
        direction = i.getAttribute("direction")
        type = i.getAttribute("type")

        if not name and direction == "out":
            if ret_count==0:
                name = "ret"
            else:
                name = "ret"+str(ret_count)
            ret_count += 1

        gtype = type_to_gtype(type)[0]
        if direction == "out" and not async:
            gtype+='*'
        else:
            if type_to_gtype(type)[3]:
                gtype="const "+gtype
        if not async or direction != "out":
            c_decl +=",\n"+pad+gtype+name
            method_decl +=",\n"+method_pad+gtype+name
            args += ', '+name
        else:
            ret_decl += ",\n"+ret_pad+gtype+name
            ret_body += ', '+name

    if async:
        c_decl += ",\n"+pad+"DBusGMethodInvocation *context)"
        method_decl += ",\n"+method_pad+"DBusGMethodInvocation *);\n"
        args += ', context'
    else:
        c_decl += ",\n"+pad+"GError **error)"
        method_decl += ",\n"+method_pad+"GError **);\n"
        args += ', error'

    interface = method.parentNode.getAttribute("name");
    if async:
        ret_decl += ')\n'
        ret_body += ');\n}\n'
        header += (ret_decl + ret_body)
    header += (c_decl+";\n\n")
    body += (
"""
/**
 * %(c_method_name)s
 *
 * Implements D-Bus method %(method)s
 * on interface %(interface)s
 *""" % {'c_method_name':c_method_name, 'method':dbus_method_name, 'interface':interface})
    if async:
        body += (
"""
 * @context: The D-Bus invocation context to use to return values
 *           or throw an error.
 */
""")
    else:
        body += (
"""
 * @error: Used to return a pointer to a GError detailing any error
 *         that occurred, D-Bus will throw the error only if this
 *         function returns FALSE.
 *
 * Returns: TRUE if successful, FALSE if an error was thrown.
 */
""")

    if async:
        body += (c_decl+"\n{\n  %s_GET_CLASS (self)->%s (%s);\n}\n\n" % (prefix.upper(),
            camelcase_to_lower(dbus_method_name), args))
    else:
        body += (c_decl+"\n{\n  return TRUE;\n}\n\n")
    return (method_decl, header, body)

if __name__ == '__main__':
    try:
        classname = sys.argv[2]
    except IndexError:
        cmdline_error()

    prefix = camelcase_to_lower(classname)

    if len(sys.argv) > 3:
        basename = sys.argv[3]
    else:
        basename = prefix.replace('_','-')

    outname_header = basename + ".h"
    outname_body = basename + ".c"
    outname_signal_marshal = basename + "-signals-marshal.list"

    header=open(outname_header,'w')
    body=open(outname_body, 'w')

    if len(sys.argv) > 4:
        signal_marshal_prefix = sys.argv[4]
    else:
        signal_marshal_prefix = prefix

    signal_marshal=open(outname_signal_marshal, 'w')

    try:
        dom = xml.dom.minidom.parse(sys.argv[1])
    except IndexError:
        cmdline_error()

    signals = dom.getElementsByTagName("signal")
    signals.sort(key=lambda n: n.getAttributeNode("name").nodeValue)
    methods = dom.getElementsByTagName("method")
    methods.sort(key=lambda n: n.getAttributeNode("name").nodeValue)

    print_license(header, outname_header, "Header for " + classname)
    print_license(body, outname_body, "Source for " + classname)
    print_header_begin(header,prefix)

    print_class_defn(header, prefix, classname, methods)

    body.write(
"""#include <dbus/dbus-glib.h>
#include <stdio.h>
#include <stdlib.h>

#include "%s"
""" % outname_header)

    if signal_marshal_prefix == prefix:
        body.write('#include "%s-signals-marshal.h"\n' % basename)
    else:
        # assume part of telepathy-glib
        # FIXME: make this configurable
        body.write('#include "signals-marshal.h"\n')

    body.write("""\
#include "%s-glue.h"

""" % (basename))

    gtypename = '_TYPE_'.join(prefix.upper().split('_',1))

    body.write(
"""
static void
%(prefix)s_base_init (gpointer klass)
{
  static gboolean initialized = FALSE;

  if (initialized) return;
  initialized = TRUE;
""" % {'classname':classname, 'gtypename':gtypename, 'prefix':prefix, 'uprefix':prefix.upper()})

    header.write("\n")

    marshallers = set()
    for signal in signals:
        dbus_name = signal.getAttributeNode("name").nodeValue
        gtypelist = signal_to_gtype_list(signal)
        marshal_name = signal_to_marshal_name(signal, signal_marshal_prefix)

        body.write(
"""
  g_signal_new ("%s",
                G_OBJECT_CLASS_TYPE (klass),
                G_SIGNAL_RUN_LAST | G_SIGNAL_DETAILED,
                0,
                NULL, NULL,
                %s,
                G_TYPE_NONE, %s);
""" % (
            (prefix + '_' + camelcase_to_lower(dbus_name)).replace('_','-'),
            marshal_name,
            ', '.join([str(len(gtypelist))] + gtypelist)))

        if not marshal_name.startswith('g_cclosure_marshal_VOID__'):
            mtype = signal_to_marshal_type(signal)
            assert(len(mtype))
            marshallers.add(','.join(mtype))

    for marshaller in marshallers:
        signal_marshal.write("VOID:"+marshaller+"\n")

    body.write(
"""
  dbus_g_object_type_install_info (%(prefix)s_get_type(), &dbus_glib_%(prefix)s_object_info);
}

GType
%(prefix)s_get_type (void)
{
  static GType type = 0;

  if (G_UNLIKELY (type == 0)) {
    static const GTypeInfo info = {
      sizeof (%(classname)sClass),
      %(prefix)s_base_init, /* base_init */
      NULL, /* base_finalize */
      NULL, /* class_init */
      NULL, /* class_finalize */
      NULL, /* class_data */
      0,
      0, /* n_preallocs */
      NULL /* instance_init */
    };

    type = g_type_register_static (G_TYPE_INTERFACE, "%(classname)s", &info, 0);
  }

  return type;
}

""" % {'classname':classname,'prefix':prefix, 'uprefix':prefix.upper()})

    for method in methods:
        m, h, b = do_method(method)
        header.write(h)
        body.write(b)

    for signal in signals:
        h, b = signal_emit_stub(signal)
        header.write(h)
        body.write(b)

    header.write('\n')

    print_header_end(header,prefix)
    header.close()
    body.close()
