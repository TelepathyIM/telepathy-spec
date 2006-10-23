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

from telepathy import *

from telepathy._generated.Channel import Channel as _Channel

from telepathy._generated.ChannelTypeContactSearch \
        import ChannelTypeContactSearch \
        as _ChannelTypeContactSearch
from telepathy._generated.ChannelTypeContactList \
        import ChannelTypeContactList \
        as _ChannelTypeContactList
from telepathy._generated.ChannelTypeStreamedMedia \
        import ChannelTypeStreamedMedia \
        as _ChannelTypeStreamedMedia
from telepathy._generated.ChannelTypeRoomList \
        import ChannelTypeRoomList \
        as _ChannelTypeRoomList
from telepathy._generated.ChannelTypeText \
        import ChannelTypeText \
        as _ChannelTypeText

from telepathy._generated.ChannelInterfaceDTMF \
        import ChannelInterfaceDTMF
from telepathy._generated.ChannelInterfaceHold \
        import ChannelInterfaceHold
from telepathy._generated.ChannelInterfacePassword \
        import ChannelInterfacePassword \
        as _ChannelInterfacePassword
from telepathy._generated.ChannelInterfaceGroup \
        import ChannelInterfaceGroup \
        as _ChannelInterfaceGroup
from telepathy._generated.ChannelInterfaceTransfer \
        import ChannelInterfaceTransfer

class Channel(_Channel, dbus.service.Object):
    def __init__(self, connection, type, handle):
        """
        Initialise the base channel object.

        Parameters:
        connection - the parent Connection object
        type - interface name for the type of this channel
        handle - the channels handle if applicable
        """
        self._conn = connection
        object_path = self._conn.get_channel_path()
        dbus.service.Object.__init__(self, self._conn._name, object_path)
        _Channel.__init__(self)

        self._type = type
        self._handle = handle
        self._interfaces = set()

    @dbus.service.method(CHANNEL_INTERFACE, in_signature='', out_signature='')
    def Close(self):
        self.Closed()
        self._conn.remove_channel(self)

    @dbus.service.method(CHANNEL_INTERFACE, in_signature='', out_signature='s')
    def GetChannelType(self):
        return self._type

    @dbus.service.method(CHANNEL_INTERFACE, in_signature='', out_signature='uu')
    def GetHandle(self):
        if self._handle:
            return self._handle.get_type(), self._handle
        else:
            return (CONNECTION_HANDLE_TYPE_NONE, 0)

    @dbus.service.method(CHANNEL_INTERFACE, in_signature='', out_signature='as')
    def GetInterfaces(self):
        return self._interfaces


class ChannelTypeContactSearch(_ChannelTypeContactSearch, Channel):
    def __init__(self, connection):
        """
        Initialise the contact search channel.
        """
        Channel.__init__(self, connection, CHANNEL_TYPE_CONTACT_SEARCH)
        _ChannelTypeContactSearch.__init__(self, connection)
        self._search_state = CHANNEL_SEARCH_STATE_BEFORE

    @dbus.service.method(CHANNEL_TYPE_CONTACT_SEARCH, in_signature='', out_signature='u')
    def GetSearchState(self):
        return self._search_state

    @dbus.service.signal(CHANNEL_TYPE_CONTACT_SEARCH, signature='u')
    def SearchStateChanged(self, state):
        self._search_state = state


class ChannelTypeContactList(_ChannelTypeContactList, Channel):
    _dbus_interfaces = [CHANNEL_TYPE_CONTACT_LIST]

    def __init__(self, connection, handle):
        """
        Initialise the channel.

        Parameters:
        connection - the parent Telepathy Connection object
        """
        Channel.__init__(self, connection, CHANNEL_TYPE_CONTACT_LIST, handle)
        _ChannelTypeContactList.__init__(self)


class ChannelTypeStreamedMedia(_ChannelTypeStreamedMedia, Channel):
    def __init__(self, connection, handle):
        """
        Initialise the channel.

        Parameters:
        connection - the parent Telepathy Connection object
        """
        Channel.__init__(self, connection, CHANNEL_TYPE_STREAMED_MEDIA, handle)
        _ChannelTypeStreamedMedia.__init__(self)


class ChannelTypeRoomList(_ChannelTypeRoomList, Channel):
    def __init__(self, connection):
        """
        Initialise the channel.

        Parameters:
        connection - the parent Telepathy Connection object
        """
        Channel.__init__(self, connection, CHANNEL_TYPE_ROOM_LIST)
        _ChannelTypeRoomList.__init__(self)
        self._listing_rooms = False
        self._rooms = {}

    @dbus.service.method(CHANNEL_TYPE_ROOM_LIST, in_signature='', out_signature='b')
    def GetListingRooms(self):
        return self._listing_rooms

    @dbus.service.signal(CHANNEL_TYPE_ROOM_LIST, signature='b')
    def ListingRooms(self, listing):
        self._listing_rooms = listing


class ChannelTypeText(_ChannelTypeText, Channel):

    def __init__(self, connection, handle):
        """
        Initialise the channel.

        Parameters:
        connection - the parent Telepathy Connection object
        """
        Channel.__init__(self, connection, CHANNEL_TYPE_TEXT, handle)
        _ChannelTypeText.__init__(self)

        self._pending_messages = {}
        self._message_types = [CHANNEL_TEXT_MESSAGE_TYPE_NORMAL]

    @dbus.service.method(CHANNEL_TYPE_TEXT, in_signature='', out_signature='au')
    def GetMessageTypes(self):
        return self._message_types

    @dbus.service.method(CHANNEL_TYPE_TEXT, in_signature='au', out_signature='')
    def AcknowledgePendingMessages(self, ids):
        for id in ids:
            if id not in self._pending_messages:
                raise telepathy.InvalidArgument("the given message ID was not found")

        for id in ids:
            del self._pending_messages[id]

    @dbus.service.method(CHANNEL_TYPE_TEXT, in_signature='b', out_signature='a(uuuuus)')
    def ListPendingMessages(self, clear):
        messages = []
        for id in self._pending_messages.keys():
            (timestamp, sender, type, flags, text) = self._pending_messages[id]
            message = (id, timestamp, sender, type, flags, text)
            messages.append(message)
            if clear:
                del self._pending_messages[id]
        messages.sort(cmp=lambda x,y:cmp(x[1], y[1]))
        return messages

    @dbus.service.signal(CHANNEL_TYPE_TEXT, signature='uus')
    def Sent(self, timestamp, type, text):
        """
        Signals that a message has been sent on this channel.

        Parameters:
        timestamp - the unix timestamp indicating when the message was sent
        type - the message type (normal, action, notice, etc)
        text - the text of the message
        """
        pass

    @dbus.service.signal(CHANNEL_TYPE_TEXT, signature='uuus')
    def SendError(self, error, timestamp, type, text):
        """
        Signals that an outgoing message has failed to send. The error
        will be one of the following values:
        0 - CHANNEL_TEXT_SEND_ERROR_UNKNOWN
            An unknown error occured.
        1 - CHANNEL_TEXT_SEND_ERROR_OFFLINE
            The requested contact was offline.
        2 - CHANNEL_TEXT_SEND_ERROR_INVALID_CONTACT
            The requested contact is not valid.
        3 - CHANNEL_TEXT_SEND_ERROR_PERMISSION_DENIED
            The user does not have permission to speak on this channel.
        4 - CHANNEL_TEXT_SEND_ERROR_TOO_LONG
            The outgoing message was too long and was rejected by the
            server.

        Parameters:
        error - one of the above integer errors
        timestamp - the unix timestamp indicating when the message was sent
        type - the message the (normal, action, notice, etc)
        text - the text of the message
        """
        pass

    @dbus.service.signal(CHANNEL_TYPE_TEXT, signature='uuuuus')
    def Received(self, id, timestamp, sender, type, flags, text):
        """
        Signals that a message with the given id, timestamp, sender, type
        and text has been received on this channel. Applications that catch
        this signal and reliably inform the user of the message should
        acknowledge that they have dealt with the message with the
        AcknowledgePendingMessage method.

        Parameters:
        id - a numeric identifier for acknowledging the message
        timestamp - a unix timestamp indicating when the message was received
        sender - the handle of the contact who sent the message
        type - the type of the message (normal, action, notice, etc)
        flags - a bitwise OR of the message flags as defined above
        text - the text of the message
        """
        self._pending_messages[id] = (timestamp, sender, type, text)


class ChannelInterfaceGroup(_ChannelInterfaceGroup):
    def __init__(self):
        _ChannelInterfaceGroup.__init__(self)
        self._group_flags = 0
        self._members = set()
        self._local_pending = set()
        self._remote_pending = set()

    @dbus.service.method(CHANNEL_INTERFACE_GROUP, in_signature='', out_signature='u')
    def GetGroupFlags(self):
        return self._group_flags

    @dbus.service.signal(CHANNEL_INTERFACE_GROUP, signature='uu')
    def GroupFlagsChanged(self, added, removed):
        self._group_flags |= added
        self._group_flags &= ~removed

    @dbus.service.method(CHANNEL_INTERFACE_GROUP, in_signature='', out_signature='au')
    def GetMembers(self):
        return self._members

    @dbus.service.method(CHANNEL_INTERFACE_GROUP, in_signature='', out_signature='u')
    def GetSelfHandle(self):
        self_handle = self._conn.GetSelfHandle()
        if (self_handle in self._members or
            self_handle in self._local_pending or
            self_handle in self._remote_pending):
            return self_handle
        else:
            return 0

    @dbus.service.method(CHANNEL_INTERFACE_GROUP, in_signature='', out_signature='au')
    def GetLocalPendingMembers(self):
        return self._local_pending

    @dbus.service.method(CHANNEL_INTERFACE_GROUP, in_signature='', out_signature='au')
    def GetRemotePendingMembers(self):
        return self._remote_pending

    @dbus.service.method(CHANNEL_INTERFACE_GROUP, in_signature='', out_signature='auauau')
    def GetAllMembers(self):
        return (self._members, self._local_pending, self._remote_pending)

    @dbus.service.signal(CHANNEL_INTERFACE_GROUP, signature='sauauauauuu')
    def MembersChanged(self, message, added, removed, local_pending, remote_pending, actor, reason):
        """
        Emitted when contacts join any of the three lists (members, local
        pending or remote pending).  Contacts are listed in the removed
        list when they leave any of the three lists. There may also be
        a message from the server regarding this change, which may be
        displayed to the user if desired.

        The reason value will be one of the following:
        0 - CHANNEL_GROUP_CHANGE_REASON_NONE
            No reason was provided for this change.
        1 - CHANNEL_GROUP_CHANGE_REASON_OFFLINE
            The change is due to a user going offline.
        2 - CHANNEL_GROUP_CHANGE_REASON_KICKED
            The change is due to a kick operation.
        3 - CHANNEL_GROUP_CHANGE_REASON_BUSY
            The change is due to a busy indication.
        4 - CHANNEL_GROUP_CHANGE_REASON_INVITED
            The change is due to an invitation.
        5 - CHANNEL_GROUP_CHANGE_REASON_BANNED
            The change is due to a kick+ban operation.

        Parameters:
        message - a string message from the server, or blank if not
        added - a list of members added to the channel
        removed - a list of members removed from the channel
        local_pending - a list of members who are pending local approval
        remote_pending - a list of members who are pending remote approval
        actor - the contact handle of the person who made the change, or 0
            if not known
        reason - a reason for the change from one of the above values
        """

        self._members.update(added)
        self._members.difference_update(removed)

        self._local_pending.update(local_pending)
        self._local_pending.difference_update(added)
        self._local_pending.difference_update(removed)

        self._remote_pending.update(remote_pending)
        self._remote_pending.difference_update(added)
        self._remote_pending.difference_update(removed)


class ChannelInterfacePassword(_ChannelInterfacePassword):
    def __init__(self):
        _ChannelInterfacePassword.__init__(self)
        self._password_flags = 0
        self._password = ''

    @dbus.service.method(CHANNEL_INTERFACE_PASSWORD, in_signature='', out_signature='u')
    def GetPasswordFlags(self):
        return self._password_flags

    @dbus.service.signal(CHANNEL_INTERFACE_PASSWORD, signature='uu')
    def PasswordFlagsChanged(self, added, removed):
        self._password_flags |= added
        self._password_flags &= ~removed
