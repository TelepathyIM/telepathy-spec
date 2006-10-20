# telepathy-spec - Base classes defining the interfaces of the Telepathy framework
#
# Copyright (C) 2005,2006 Collabora Limited
# Copyright (C) 2005,2006 Nokia Corporation
# Copyright (C) 2006 INdT
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
import re
import weakref

from telepathy import *
from handle import Handle

from telepathy._generated.Connection import Connection as _Connection
from telepathy._generated.ConnectionInterfaceAliasing import ConnectionInterfaceAliasing as _ConnectionInterfaceAliasing
from telepathy._generated.ConnectionInterfaceAvatars import ConnectionInterfaceAvatars
from telepathy._generated.ConnectionInterfaceCapabilities import ConnectionInterfaceCapabilities as _ConnectionInterfaceCapabilities
from telepathy._generated.ConnectionInterfaceContactInfo import ConnectionInterfaceContactInfo

class Connection(_Connection, dbus.service.Object):
    def __init__(self, proto, account):
        """
        Parameters:
        proto - the name of the protcol this conection should be handling.
        account - a protocol-specific account name
        account - a unique identifier for this account which is used to identify this connection
        """
        clean_account = re.sub('[^a-zA-Z0-9_]', '_', account)
        bus_name = dbus.service.BusName('org.freedesktop.Telepathy.Connection.' + clean_account)
        object_path = '/org/freedesktop/Telepathy/Connection/' + clean_account
        dbus.service.Object.__init__(self, bus_name, object_path)

        # monitor clients dying so we can release handles
        self._bus.add_signal_receiver(self.name_owner_changed_callback,
                                      'NameOwnerChanged',
                                      'org.freedesktop.DBus',
                                      'org.freedesktop.DBus',
                                      '/org/freedesktop/DBus')

        self._proto = proto

        self._status = CONNECTION_STATUS_CONNECTING
        self._interfaces = set()

        self._handles = weakref.WeakValueDictionary()
        self._next_handle_id = 1
        self._client_handles = {}

        self._channels = set()
        self._next_channel_id = 0

    def check_parameters(self, parameters):
        """
        Uses the values of self._mandatory_parameters and
        self._optional_parameters to validate and type check all of the
        provided parameters, and check all mandatory parameters are present.
        Sets defaults according to the defaults if the client has not
        provided any.
        """
        for (parm, value) in parameters.iteritems():
            if parm in self._mandatory_parameters.keys():
                sig = self._mandatory_parameters[parm]
            elif parm in self._optional_parameters.keys():
                sig = self._optional_parameters[parm]
            else:
                raise InvalidArgument('unknown parameter name %s' % parm)

            if sig == 's':
                if not isinstance(value, unicode):
                    raise InvalidArgument('incorrect type to %s parameter, got %s, expected a string' % (parm, type(value)))
            elif sig == 'q':
                if not isinstance(value, int):
                    raise InvalidArgument('incorrect type to %s parameter, got %s, expected an int' % (parm, type(value)))
            elif sig == 'b':
                if not isinstance(value, bool):
                    raise InvalidArgument('incorrect type to %s parameter, got %s, expected an boolean' % (parm, type(value)))
            else:
                raise TypeError('unknown type signature %s in protocol parameters' % type)

        for (parm, value) in self._parameter_defaults.iteritems():
            if parm not in parameters:
                parameters[parm] = value

        missing = set(self._mandatory_parameters.keys()).difference(parameters.keys())
        if missing:
            raise InvalidArgument('required parameters %s not given' % missing)

    def check_connected(self):
        if self._status != CONNECTION_STATUS_CONNECTED:
            raise Disconnected('method cannot be called unless status is CONNECTION_STATUS_CONNECTED')

    def check_handle(self, handle_type, handle):
        if (handle_type, handle) not in self._handles:
            print "Connection.check_handle", handle, handle_type, self._handles.keys()
            print str(list( [ self._handles[x] for x in self._handles.keys() ] ) )
            raise InvalidHandle('handle number %s not valid' % handle)

    def check_handle_type(self, type):
        if (type < CONNECTION_HANDLE_TYPE_CONTACT or
            type > CONNECTION_HANDLE_TYPE_LIST):
            raise InvalidArgument('handle type %s not known' % type)

    def get_handle_id(self):
        id = self._next_handle_id
        self._next_handle_id += 1
        return id

    def add_client_handle(self, handle, sender):
        if sender in self._client_handles:
            self._client_handles[sender].add((handle.get_type(), handle))
        else:
            self._client_handles[sender] = set([(handle.get_type(), handle)])

    def name_owner_changed_callback(self, name, old_owner, new_owner):
        # when name and old_owner are the same, and new_owner is
        # blank, it is the client itself releasing its name... aka exiting
        if (name == old_owner and new_owner == "" and name in self._client_handles):
            print "deleting handles for", name
            del self._client_handles[name]

    def set_self_handle(self, handle):
        self._self_handle = handle

    def get_channel_path(self):
        ret = '%s/channel%d' % (self._object_path, self._next_channel_id)
        self._next_channel_id += 1
        return ret

    def add_channel(self, channel, handle, suppress_handler):
        """ add a new channel and signal its creation""" 
        self._channels.add(channel)
        self.NewChannel(channel._object_path, channel._type, handle.get_type(), handle.get_id(), suppress_handler)

    def remove_channel(self, channel):
        self._channels.remove(channel)

    @dbus.service.method(CONN_INTERFACE, in_signature='', out_signature='as')
    def GetInterfaces(self):
        self.check_connected()
        return self._interfaces

    @dbus.service.method(CONN_INTERFACE, in_signature='', out_signature='s')
    def GetProtocol(self):
        return self._proto

    @dbus.service.method(CONN_INTERFACE, in_signature='uau', out_signature='as')
    def InspectHandles(self, handle_type, handles):
        self.check_connected()
        self.check_handle_type(handle_type)

        for handle in handles:
            self.check_handle(handle_type, handle)

        ret = []
        for handle in handles:
            ret.append(self._handles[handle_type, handle].get_name())

        return ret

    @dbus.service.method(CONN_INTERFACE, in_signature='uas', out_signature='au', sender_keyword='sender')
    def RequestHandles(self, handle_type, names, sender):
        self.check_connected()
        self.check_handle_type(handle_type)

        ret = {}
        for name in names:
            id = self.get_handle_id()
            handle = Handle(id, handle_type, name)
            self._handles[handle_type, id] = handle
            self.add_client_handle(handle, sender)
            ret[name] = id

        return id

    @dbus.service.method(CONN_INTERFACE, in_signature='uau', out_signature='', sender_keyword='sender')
    def HoldHandles(self, handle_type, handles, sender):
        self.check_connected()
        self.check_handle_type(handle_type)

        for handle in handles:
            self.check_handle(handle_type, handle)

        for handle in handles:
            hand = self._handles[handle_type, handle]
            self.add_client_handle(hand, sender)

    @dbus.service.method(CONN_INTERFACE, in_signature='uau', out_signature='')
    def ReleaseHandles(self, handle_type, handles):
        self.check_connected()
        self.check_handle_type(handle_type)

        for handle in handles:
            self.check_handle(handle_type, handle)
            hand = self._handles[handle_type, handle]
            if sender in self._client_handles:
                if hand not in self._client_handles[sender]:
                    raise NotAvailable('client is not holding handle %s' % handle)
            else:
                raise NotAvailable('client does not hold any handles')

        for handle in handles:
            hand = self._handles[handle_type, handle]
            self._client_handles[sender].remove(hand)

    @dbus.service.method(CONN_INTERFACE, in_signature='', out_signature='u')
    def GetSelfHandle(self):
        self.check_connected()
        return self._self_handle

    @dbus.service.signal(CONN_INTERFACE, signature='uu')
    def StatusChanged(self, status, reason):
        self._status = status

    @dbus.service.method(CONN_INTERFACE, in_signature='', out_signature='u')
    def GetStatus(self):
        return self._status

    @dbus.service.method(CONN_INTERFACE, in_signature='', out_signature='a(osuu)')
    def ListChannels(self):
        self.check_connected()
        ret = []
        for channel in self._channels:
            chan = (channel._object_path, channel._type, channel._handle.get_type(), channel._handle)
            ret.append(chan)
        return ret

    @dbus.service.method(CONN_INTERFACE, in_signature='suub', out_signature='o')
    def RequestChannel(self, type, handle_type, handle, suppress_handler):
        self.check_connected()
        raise NotImplemented('unknown channel type %s' % type)


class ConnectionInterfaceAliasing(_ConnectionInterfaceAliasing):

    @dbus.service.method(CONN_INTERFACE_ALIASING, in_signature='', out_signature='u')
    def GetAliasFlags(self):
        return 0

class ConnectionInterfaceCapabilities(_ConnectionInterfaceCapabilities):
    def __init__(self):
        """
        Initialise the capabilities interface.
        """
        _ConnectionInterfaceCapabilities.__init__(self)
        self._own_caps = set()
        self._caps = {}

    @dbus.service.method(CONN_INTERFACE_CAPABILITIES, in_signature='au', out_signature='a(usuu)')
    def GetCapabilities(self, handles):
        if (handle != 0 and handle not in self._handles):
            raise InvalidHandle
        elif handle in self._caps:
            return self._caps[handle]
        else:
            return []

    @dbus.service.signal(CONN_INTERFACE_CAPABILITIES, signature='a(usuuuu)')
    def CapabilitiesChanged(self, caps):
        if handle not in self._caps:
            self._caps[handle] = set()

        self._caps[handle].update(added)
        self._caps[handle].difference_update(removed)

    @dbus.service.method(CONN_INTERFACE_CAPABILITIES, in_signature='a(su)as', out_signature='a(su)')
    def AdvertiseCapabilities(self, add, remove):
        # no-op implementation
        self.AdvertisedCapabilitiesChanged(self._self_handle, add, remove)


class ConnectionInterfaceForwarding(dbus.service.Interface):
    """
    A connection interface for services which can signal to contacts
    that they should instead contact a different user ID, effectively
    forwarding all incoming communication channels to another contact on
    the service.
    """
    def __init__(self):
        self._interfaces.add(CONN_INTERFACE_FORWARDING)
        self._forwarding_handle = 0

    @dbus.service.method(CONN_INTERFACE_FORWARDING, in_signature='', out_signature='u')
    def GetForwardingHandle(self):
        """
        Returns the current forwarding contact handle, or zero if none is set.

        Returns:
        an integer contact handle to whom incoming communication is forwarded

        Possible Errors:
        Disconnected, NetworkError, NotAvailable
        """
        return self._forwarding_handle

    @dbus.service.method(CONN_INTERFACE_FORWARDING, in_signature='u', out_signature='')
    def SetForwardingHandle(self, forward_to):
        """
        Set a contact handle to forward incoming communications to. A zero
        handle disables forwarding.

        Parameters:
        forward_to - an integer contact handle to forward incoming communications to

        Possible Errors:
        Disconnected, NetworkError, PermissionDenied, NotAvailable, InvalidHandle
        """
        pass

    @dbus.service.signal(CONN_INTERFACE_FORWARDING, signature='u')
    def ForwardingChanged(self, forward_to):
        """
        Emitted when the forwarding contact handle for this connection has been
        changed. An zero handle indicates forwarding is disabled.

        Parameters:
        forward_to - an integer contact handle to forward communication to
        """
        self._forwarding_handle = forward_to


class ConnectionInterfacePresence(dbus.service.Interface):
    """
    This interface is for services which have a concept of presence which can
    be published for yourself and monitored on your contacts. Telepathy's
    definition of presence is based on that used by the Galago project
    (see http://www.galago-project.org/).

    Presence on an individual (yourself or one of your contacts) is modelled as
    an last activity time along with a set of zero or more statuses, each of
    which may have arbitrary key/value parameters. Valid statuses are defined
    per connection, and a list of them can be obtained with the GetStatuses
    method.

    Each status has an arbitrary string identifier which should have an agreed
    meaning between the connection manager and any client which is expected to
    make use of it. The following well-known values (in common with those in
    Galago) should be used where possible to allow clients to identify common
    choices:
    - available
    - away
    - brb (Be Right Back)
    - busy
    - dnd (Do Not Disturb),
    - xa (Extended Away)
    - hidden (aka Invisible)
    - offline

    As well as these well-known status identifiers, every status also has a
    numerical type value which can be used by the client to classify even
    unknown statuses into different fundamental types:
    1 - CONNECTION_PRESENCE_TYPE_OFFLINE
    2 - CONNECTION_PRESENCE_TYPE_AVAILABLE
    3 - CONNECTION_PRESENCE_TYPE_AWAY
    4 - CONNECTION_PRESENCE_TYPE_EXTENDED_AWAY
    5 - CONNECTION_PRESENCE_TYPE_HIDDEN

    These numerical types exist so that even if a client does not understand
    the string identifier being used, and hence cannot present the presence to
    the user to set on themselves, it may display an approximation of the
    presence if it is set on a contact.

    The dictionary of variant types allows the connection manager to exchange
    further protocol-specific information with the client. It is recommended
    that the string (s) argument 'message' be interpreted as an optional
    message which can be associated with a presence status.

    If the connection has a 'subscribe' contact list, PresenceUpdate signals
    should be emitted to indicate changes of contacts on this list, and should
    also be emitted for changes in your own presence. Depending on the
    protocol, the signal may also be emitted for others such as people with
    whom you are communicating, and any user interface should be updated
    accordingly.

    On some protocols, RequestPresence may only succeed on contacts on your
    'subscribe' list, and other contacts will cause a PermissionDenied error.
    On protocols where there is no 'subscribe' list, and RequestPresence
    succeeds, a client may poll the server intermittently to update any display
    of presence information.
    """

    def __init__(self):
        self._interfaces.add(CONN_INTERFACE_PRESENCE)

    @dbus.service.method(CONN_INTERFACE_PRESENCE, in_signature='', out_signature='a{s(ubba{ss})}')
    def GetStatuses(self):
        """
        Get a dictionary of the valid presence statuses for this connection.
        This is only available when online because only some statuses will
        be available on some servers.

        Returns:
        a dictionary of string identifiers mapped to a struct for each status, containing:
        - a type value from one of the values above
        - a boolean to indicate if this status may be set on yourself
        - a boolean to indicate if this is an exclusive status which you may not set alongside any other
        - a dictionary of valid optional string argument names mapped to their types

        Possible Errors:
        Disconnected, NetworkError
        """
        pass

    @dbus.service.method(CONN_INTERFACE_PRESENCE, in_signature='au', out_signature='')
    def RequestPresence(self, contacts):
        """
        Request the presence for contacts on this connection. A PresenceUpdate
        signal will be emitted when they are received. This is not the same as
        subscribing to the presence of a contact, which must be done using the
        'subscription' Channel.Type.ContactList, and on some protocols presence
        information may not be available unless a subscription exists.

        Parameters:
        contacts - an array of the contacts whose presence should be obtained

        Possible Errors:
        Disconnected, NetworkError, InvalidHandle, PermissionDenied, NotAvailable (if the presence of the requested contacts is not reported to this connection)
        """
        pass

    @dbus.service.method(CONN_INTERFACE_PRESENCE, in_signature='au', out_signature='a{u(ua{sa{sv}})}')
    def GetPresence(self, contacts):
        """
        Get presence previously emitted by PresenceUpdate for the given
        contacts. Data is returned in the same structure as the PresenceUpdate
        signal. Using this method in favour of RequestPresence has the
        advantage that it will not wake up each client connected to the
        PresenceUpdate signal.

        Possible Errors:
        Disconnected, InvalidHandle, NotAvailable
        """

    @dbus.service.signal(CONN_INTERFACE_PRESENCE, signature='a{u(ua{sa{sv}})}')
    def PresenceUpdate(self, presence):
        """
        This signal should be emitted when your own presence has been changed,
        or the presence of the member of any of the connection's channels has
        been changed, or when the presence requested by RequestPresence is available.

        Parameters:
        a dictionary of contact handles mapped to a struct containing:
        - a UNIX timestamp of the last activity time (in UTC)
        - a dictionary mapping the contact's current status identifiers to:
          a dictionary of optional parameter names mapped to their 
          variant-boxed values
        """
        pass

    @dbus.service.method(CONN_INTERFACE_PRESENCE, in_signature='u', out_signature='')
    def SetLastActivityTime(self, time):
        """
        Request that the recorded last activity time for the user be updated on
        the server.

        Parameters:
        time - a UNIX timestamp of the user's last activity time (in UTC)

        Possible Errors:
        Disconnected, NetworkError, NotImplemented (this protocol has no concept of idle time)
        """
        pass

    @dbus.service.method(CONN_INTERFACE_PRESENCE, in_signature='a{sa{sv}}', out_signature='')
    def SetStatus(self, statuses):
        """
        Request that the user's presence be changed to the given statuses and
        desired parameters. Changes will be reflected by PresenceUpdate
        signals being emitted. On certain protocols, this method may be
        called on a newly-created connection which is still in the
        DISCONNECTED state, and will sign on with the requested status.
        If the requested status is not available after signing on,
        NotAvailable will be returned and the connection will remain
        offline, or if the protocol does not support signing on with
        a certain status, Disconnected will be returned.

        Parameters:
        a dictionary of status identifiers mapped to:
            a dictionary of optional parameter names mapped to their variant-boxed values

        Possible Errors:
        Disconnected, NetworkError, InvalidArgument, NotAvailable, PermissionDenied
        """
        pass

    @dbus.service.method(CONN_INTERFACE_PRESENCE, in_signature='', out_signature='')
    def ClearStatus(self):
        """
        Request that all of a user's presence statuses be removed. Be aware
        that this request may simply result in the statuses being replaced by a
        default available status. Changes will be indicated by PresenceUpdate
        signals being emitted.

        Possible Errors:
        Disconnected, NetworkError, PermissionDenied
        """
        pass

    @dbus.service.method(CONN_INTERFACE_PRESENCE, in_signature='sa{sv}', out_signature='')
    def AddStatus(self, status, parms):
        """
        Request that a single presence status is published for the user, along
        with any desired parameters. Changes will be indicated by PresenceUpdate
        signals being emitted.

        Parameters:
        status - the string identifier of the desired status
        parms - a dictionary of optional parameter names mapped to their variant-boxed values

        Possible Errors:
        Disconnected, NetworkError, InvalidArgument, NotAvailable, PermissionDenied
        """
        pass

    @dbus.service.method(CONN_INTERFACE_PRESENCE, in_signature='s', out_signature='')
    def RemoveStatus(self, status):
        """
        Request that the given presence status is no longer published for the
        user. Changes will be indicated by PresenceUpdate signals being
        emitted. As with ClearStatus, removing a status may actually result in
        it being replaced by a default available status.

        Parameters:
        status - the string identifier of the status not to publish anymore for the user

        Possible Errors:
        Disconnected, NetworkError, PermissionDenied, InvalidArgument (if the status
        requested is not currently set)
        """
        pass


class ConnectionInterfacePrivacy(dbus.service.Interface):
    """
    An interface to support getting and setting privacy modes to configure
    situations such as not being contactable by people who are not on your
    subscribe list. If this interface is not implemented, the default can be
    presumed to be allow-all (as defined in GetPrivacyModes).
    """
    def __init__(self, modes):
        """
        Initialise privacy interface.

        Parameters:
        modes - a list of privacy modes available on this interface
        """
        self._interfaces.add(CONN_INTERFACE_PRIVACY)
        self._privacy_mode = ''
        self._privacy_modes = modes

    @dbus.service.method(CONN_INTERFACE_PRIVACY, in_signature='', out_signature='as')
    def GetPrivacyModes(self):
        """
        Returns the privacy modes available on this connection. The following
        well-known names should be used where appropriate:
         allow-all - any contact may initiate communication
         allow-specified - only contacts on your 'allow' list may initiate communication
         allow-subscribed - only contacts on your subscription list may initiate communication

        Returns:
        an array of valid privacy modes for this connection
        """
        return self._privacy_modes

    @dbus.service.method(CONN_INTERFACE_PRIVACY, in_signature='', out_signature='s')
    def GetPrivacyMode(self):
        """
        Return the current privacy mode, which must be one of the values
        returned by GetPrivacyModes.

        Returns:
        a string of the current privacy mode

        Possible Errors:
        Disconnected, NetworkError
        """
        return self._privacy_mode

    @dbus.service.method(CONN_INTERFACE_PRIVACY, in_signature='s', out_signature='')
    def SetPrivacyMode(self, mode):
        """
        Request that the privacy mode be changed to the given value, which
        must be one of the values returned by GetPrivacyModes. Success is
        indicated by the method returning and the PrivacyModeChanged
        signal being emitted.

        Parameters:
        mode - the desired privacy mode

        Possible Errors:
        Disconnected, NetworkError, PermissionDenied, InvalidArgument
        """
        pass

    @dbus.service.signal(CONN_INTERFACE_PRIVACY, signature='s')
    def PrivacyModeChanged(self, mode):
        """
        Emitted when the privacy mode is changed or the value has been
        initially received from the server.

        Parameters:
        mode - the current privacy mode
        """
        self._privacy_mode = mode


class ConnectionInterfaceRenaming(dbus.service.Interface):
    """
    An interface on connections to support protocols where the unique
    identifiers of contacts can change. Because handles are immutable,
    this is represented by a pair of handles, that representing the
    old name, and that representing the new one.
    """
    def __init__(self):
        self._interfaces.add(CONN_INTERFACE_RENAMING)

    @dbus.service.method(CONN_INTERFACE_RENAMING, in_signature='s', out_signature='')
    def RequestRename(self, name):
        """
        Request that the users own identifier is changed on the server. Success
        is indicated by a Renamed signal being emitted. A new handle will be
        allocated for the user's new identifier, and remain valid for the
        lifetime of the connection.

        Parameters:
        name - a string of the desired identifier

        Possible Errors:
        Disconnected, NetworkError, NotAvailable, InvalidArgument, PermissionDenied
        """
        pass

    @dbus.service.signal(CONN_INTERFACE_RENAMING, signature='uu')
    def Renamed(self, original, new):
        """
        Emitted when the unique identifier of a contact on the server changes.

        Parameters:
        original - the handle of the original identifier
        new - the handle of the new identifier
        """
        pass

