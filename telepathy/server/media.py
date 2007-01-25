# telepathy-spec - Base classes defining the interfaces of the Telepathy framework
#
# Copyright (C) 2005,2006 Collabora Limited
# Copyright (C) 2005,2006 Nokia Corporation
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import dbus.service

from telepathy._generated.Channel_Interface_Media_Signalling import ChannelInterfaceMediaSignalling
from telepathy._generated.Media_Session_Handler import MediaSessionHandler as _MediaSessionHandler
from telepathy._generated.Media_Stream_Handler import MediaStreamHandler as _MediaStreamHandler

class MediaSessionHandler(_MediaSessionHandler, dbus.service.Object):
    def __init__(self, bus_name, object_path):
        _MediaSessionHandler.__init__(self)
        dbus.service.Object.__init__(self, bus_name, object_path)

class MediaStreamHandler(_MediaStreamHandler, dbus.service.Object):
    def __init__(self, bus_name, object_path):
        _MediaStreamHandler.__init__(self)
        dbus.service.Object.__init__(self, bus_name, object_path)
