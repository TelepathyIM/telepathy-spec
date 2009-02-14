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

interfaces = specparser.parse (sys.argv[1])

# load the template
template_path = os.path.join (os.path.dirname (sys.argv[0]),
                              '../doc/templates')
output_path = os.path.join (os.path.dirname (sys.argv[0]),
                              '../doc/spec')

try:
    file = open (os.path.join (template_path, 'interface.html'))
    template_def = file.read ()
    file.close ()
except IOError, e:
    print >> sys.stderr, "Could not load template file `interface.html'"
    print >> sys.stderr, e
    sys.exit (-1)

for interface in interfaces.values ():
    namespace = { 'interface': interface }
    t = Template (template_def, namespaces = [namespace])
    
    # open the output file
    out = open (os.path.join (output_path, '%s.html' % interface.name), 'w')
    print >> out, t
    out.close ()
