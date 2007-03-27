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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from telepathy._generated.interfaces import *
from telepathy._generated.interfaces import \
        CONNECTION_MANAGER as CONN_MGR_INTERFACE, \
        CONNECTION as CONN_INTERFACE, \
        CONNECTION_INTERFACE_ALIASING as CONN_INTERFACE_ALIASING, \
        CONNECTION_INTERFACE_AVATARS as CONN_INTERFACE_AVATARS, \
        CONNECTION_INTERFACE_CAPABILITIES as CONN_INTERFACE_CAPABILITIES, \
        CONNECTION_INTERFACE_CONTACT_INFO as CONN_INTERFACE_CONTACT_INFO, \
        CONNECTION_INTERFACE_FORWARDING as CONN_INTERFACE_FORWARDING, \
        CONNECTION_INTERFACE_PRESENCE as CONN_INTERFACE_PRESENCE, \
        CONNECTION_INTERFACE_PRIVACY as CONN_INTERFACE_PRIVACY, \
        CONNECTION_INTERFACE_RENAMING as CONN_INTERFACE_RENAMING, \
        CHANNEL as CHANNEL_INTERFACE
