#!/usr/bin/env python3
#
# doc-generator.py
#
# Generates HTML documentation from the parsed spec
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
import os
import os.path
import shutil
import itertools

try:
    from jinja2 import Template
except ImportError as e:
    print(e, file=sys.stderr)
    print("Install `jinja2'?", file=sys.stderr)
    sys.exit(-1)

import specparser

# one day, OptionParser
allow_externals = False
if '--allow-externals' in sys.argv:
    allow_externals = True
    sys.argv.remove('--allow-externals')

program, spec_file, output_path, project, namespace = sys.argv

template_path = os.path.join(os.path.dirname(program), '../doc/templates')

# make the output path
try:
    os.mkdir(output_path)
except OSError:
    pass

# copy in the static files
static = [ 'style.css',
           'jquery.min.js',
           'ui-icons_222222_256x240.png',
           'magic.js',
           'favicon.png'
         ]
for s in static:
    shutil.copy(os.path.join(template_path, s), output_path)

def load_template(filename):
    try:
        file = open(os.path.join(template_path, filename))
        template_def = file.read()
        file.close()
    except IOError as e:
        print("Could not load template file `%s'" % filename, file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(-1)

    return template_def

def render_template(name, context, target=None):
    if target is None:
        target = name
    template_def = load_template(name)
    t = Template(template_def).render(context)
    with open(os.path.join(output_path, target), 'w') as out:
      out.write(t)

spec = specparser.parse(spec_file, namespace, allow_externals=allow_externals)

# write out HTML files for each of the interfaces

all_values = list(spec.everything.values()) + list(spec.errors.values()) + list(spec.types.values())

star = [ (item.short_name, item) for item in all_values ]
star.sort(key = lambda t: t[0].title())
groups = [ (l, list(g)) for l, g in (itertools.groupby(star, key = lambda t: t[0][0].upper())) ]
letters = set(map(lambda t: t[0], groups))
all_letters = list(map(chr, range(ord('A'), ord('Z')+1)))

context = { 'spec': spec, 'star': star, 'groups': groups,
            'letters': letters, 'all_letters': all_letters }
render_template('fullindex.html', context)

context = { 'spec': spec, 'name': project, 'all_values': all_values }
render_template('devhelp.devhelp2', context, target=('%s.devhelp2' % project))

# Not using render_template here to avoid recompiling it n times.
context = { 'spec': spec }
template_def = load_template('interface.html')
t = Template(template_def)
for interface in spec.interfaces:
    context['interface'] = interface
    # open the output file
    with open(os.path.join(output_path, '%s.html'
        % interface.name_for_bindings), 'w') as out:
      out.write(t.render(context))

context = { 'spec': spec }
if len(spec.generic_types) > 0:
    render_template('generic-types.html', context)
if len(spec.errors) > 0:
    render_template('errors.html', context)
render_template('interfaces.html', context)

# write out the TOC last, because this is the file used as the target in the
# Makefile.
render_template('index.html', context)
