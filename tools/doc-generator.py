#!/usr/bin/env python

import sys
import os.path

try:
    from Cheetah.Template import Template
except ImportError, e:
    print >> sys.stderr, e
    print >> sys.stderr, "Install `python-cheetah'?"
    sys.exit (-1)

import specparser

template_path = os.path.join (os.path.dirname (sys.argv[0]),
                              '../doc/templates')
output_path = os.path.join (os.path.dirname (sys.argv[0]),
                              '../doc/spec')

def load_template (filename):
    try:
        file = open (os.path.join (template_path, filename))
        template_def = file.read ()
        file.close ()
    except IOError, e:
        print >> sys.stderr, "Could not load template file `%s'" % filename
        print >> sys.stderr, e
        sys.exit (-1)

    return template_def

interfaces = specparser.parse (sys.argv[1])

# write out HTML files for each of the interfaces
template_def = load_template ('interface.html')
for interface in interfaces.values ():
    namespace = { 'interface': interface }
    t = Template (template_def, namespaces = [namespace])
    
    # open the output file
    out = open (os.path.join (output_path, '%s.html' % interface.name), 'w')
    print >> out, t
    out.close ()

# write out a TOC
template_def = load_template ('index.html')
namespace = { 'interfaces': interfaces }
t = Template (template_def, namespaces = [namespace])

# open the output file
out = open (os.path.join (output_path, 'index.html'), 'w')
print >> out, t
out.close ()
