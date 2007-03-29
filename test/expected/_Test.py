# Generated from the Telepathy spec
"""Copyright (C) 2006 Collabora Limited

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
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
USA.
  
"""

import dbus.service


class Test(dbus.service.Interface):
    """\
      A test case for the spec processing.
    """
    def __init__(self):
        self._interfaces.add('org.freedesktop.Telepathy.SpecAutoGenTest')


    @dbus.service.method('org.freedesktop.Telepathy.SpecAutoGenTest', in_signature='ba{sv}s', out_signature='a(uv)')
    def DoStuff(self, badger, mushroom, snake):
        """
        Does stuff.
      
        """
        raise NotImplementedError
  
    @dbus.service.signal('org.freedesktop.Telepathy.SpecAutoGenTest', signature='aysb')
    def StuffHappened(self, stoat, ferret, weasel):
        """
        Emitted when stuff happened.
      
        """
        pass
  