This file contains the same edited highlights as the announcement emails.
For full details, see the ChangeLog in tarballs, or "git log" in Git
checkouts.

telepathy-spec 0.27.2 (2013-09-24)
==================================

API additions and clarifications:

• The Connection.SelfID property has been added containing the identifier of
  the user on the connection.

• The Connection.SelfHandleChanged signal has been deprecated and replaced
  by the new Connection.SelfContactChanged signal.

telepathy-spec 0.27.1 (2013-09-16)
==================================

The “substitute burger buns” release.

Changes:

• The handle-name property in room lists' room details is now mandatory
  (Xavier)

New stable API:

• Account.Interface.Addressing has change-notification via the standard
  D-Bus Properties.PropertiesChanged signal (fd.o #40393, Guillaume)

Clarifications:

• More Tubes properties are marked up as immutable (Will)

telepathy-spec 0.27.0 (2012-05-09)
==================================

This is the first release in the 0.27 development branch.

Changes since 0.26.0:

• Mark ConnectionManager's Protocols and Protocol.I.Presence's Statuses
  properties immutable (Andre Moreira Magalhae)

• Add GetContactByID to get contact attributes for a single contact identifier
  (Xavier Claessens)

telepathy-spec 0.26.0 (2012-04-02)
==================================

This is the start of a new stable branch of the Telepathy
specification.

Changes since 0.25.2:

• Small miscellaneous fixes to Call-related interfaces.

Other notable changes since the 0.24 stable branch:

• The Call1 family of interfaces is now considered stable after
  substantial from previous drafts.

• A Metadata file transfer interface has been added to transfer extra
  data about a transfer in the channel.

• A Picture channel interface has been added to retrieve and set
  pictures for text channels and calls.

telepathy-spec 0.25.2 (2012-02-20)
==================================

The "you know what they said? Well, some of it was true" release.

New stable API:

• The Call1 family of interfaces (except for the Mute interface) is now
  considered stable, with significant changes since 0.25.1:

  · Content.Removed signal removed, use Call1.ContentRemoved instead
  · Content.I.DTMF added; this supersedes everything in Channel.I.DTMF
    except the InitialTones property
  · Various redundant contact handles removed from Content.I.Media
  · MediaDescription.Reject has an "in" argument, not a nonsensical "out"
    argument
  · Stream.I.Media no longer has Pending_Pause or Paused states
  · The Ringing state has been renamed to Initialising to avoid confusion
    with the Ringing flag
  · Call1.AddContent takes an initial direction as its new last parameter
  · Call_Flag_Locally_Muted has been removed and the other Call_Flags
    have been renumbered
  · Call_Member_Flag_Ringing has been removed and the other Call_Member_Flags
    have been renumbered
  · The destination of a forwarded call is published in the CallStateDetails,
    rather than abusing the Actor member of CallStateReason

• Connection.I.Addressing1 is now stable, and identical to
  Connection.I.Addressing.DRAFT in 0.25.1 except for its name

• Account.Supersedes has been added

• Connection.I.ContactList.DownloadAtConnection has been added, together with
  the Download method

• A serialization has been defined for arrays of object path in .manager
  files (and by extension, anything sharing that format)

Clarifications:

• Account.Service should also be used for IRC networks

• Channel.I.DTMF.InitialTones should only be used in conjunction with
  InitialAudio=TRUE

• The policy for versioned interfaces is now documented

Changes to experimental API:

• Channel.I.Addressing1 is the new name for Channel.I.Addressing.DRAFT,
  but is still considered experimental

telepathy-spec 0.25.1 (2011-11-23)
==================================

The “farewell whiskey chess” release.

API additions and clarifications:

• Call1.Content.Interface.AudioControl is a wonderful new interface to
  allow the connection manager to recommend volume changes during calls.

• The various values of Socket_Access_Control have enjoyed some
  clarification of their meanings on different tube types.

• Protocol.Interface.Addressing has been undrafted, with NormalizeURI
  renamed to NormalizeContactURI.

• Connection.Interface.Addressing is still a draft, but its methods have
  been changed to split the return values into two mappings.

telepathy-spec 0.25.0 (2011-11-10)
==================================

API additions and clarifications:

• Channel.Interface.FileTransfer.Metadata has been added.

• Channel.Interface.Picture has been added.

• "windows-live" has been added as a known account service name.

• Channel.Interface.Subject: clarify default values for properties in
  the unknown case.

• RoomConfig: add a PasswordHint property which does what you think it
  does.

• Room: add Creator, CreatorHandle and CreationTimestamp properties.

• Channel.Type.ContactList has been deprecated.

telepathy-spec 0.24.0 (2011-10-10)
==================================

The “underestimating the future” release.  This is the start of a new
stable branch of the Telepathy specification.

Changes since 0.23.4:

• Channel.Interface.Room has been undrafted, with a few changes:
  · The RoomID property has become RoomName;
  · The Subject property has been split off onto a separate interface,
    Channel.Interface.Subject (which is also undrafted).

• Channel.Interface.RoomConfig has been defined to replace the remaining
  klunky Telepathy.Properties on Channel.Type.Text.

• As a result, the Telepathy.Properties interface has been deprecated,
  since all interfaces which historically used it now have better
  replacements.

Other notable changes since the 0.22 stable branch:

• Most interfaces now provide both handles and identifiers for contacts.
  This makes life easier for telepathy-glib and telepathy-qt4 (and, by
  extension, application authors).

• A new revision of the Call family of interfaces has landed. It is
  still marked experimental.

• ChannelDispatcher has a pair of new methods, DelegateChannels() and
  PresentChannel(), to aid user interfaces where channels can be shown
  in a number of places (like Gnome 3).

• FileTransfer now has a URI property to indicate the on-disk location
  of the file being sent or received.

telepathy-spec 0.23.4 (2011-09-29)
==================================

API additions and clarifications:

• Always give contact identifiers together with handles in
  Channel.Interface.Group. This helps clients to create contact objects without
  extra async operations. Additions are:
    • Channel.Interface.Group.MemberIdentifiers;
    • Channel.Interface.Group.SelfContactChanged; and
    • Channel.Interface.Group.HandleOwnersChangedDetailed.

• AccountManager: remove note about service activation. Mission Control is
  service-activatable and is probably the only implementation we'll ever have.

• Clarify possible errors returned by AM.CreateAccount.

Spec HTML improvements:

• Now <tp:value-ref> is used to reference a value in a enumeration.

Call DRAFT2 landed

• Call interfaces are now versioned. For example
  org.freedesktop.Telepathy.Channel.Type.Call.DRAFT is now renamed to
  org.freedesktop.Telepathy.Channel.Type.Call1.

telepathy-spec 0.23.3 (2011-07-14)
==================================

API additions and clarifications:

• The semantics of the 'supersedes' header in Messages have been clarified, and
  'original-message-sent' and 'original-message-received' headers have been
  defined to make the timestamps used for message edits unambiguous.
  (fd.o#37413, David)

• A tonne of properties on FileTransfer have been marked as requestable and/or
  immutable. Also, as a clarification, the spec now explicitly says that
  approvers may set the URI property, and that handlers MUST obey this.
  (Xavier)

• A new ChannelRequest hint, DelegateToPreferredHandler, has been added.
  (fd.o#38240, Danni)

Spec HTML improvements:

• Jumping to anchors within the spec HTML will no longer move the text you're
  looking for underneath the title bar with Webkit. Yay! (Danni (my heroine))

• The generated HTML spec now has a beautiful favicon. (fd.o#38594, Guillaume)

And for spec developers:

• `make upload-branch` now takes an optional UPLOAD_BRANCH_TO Makefile
  variable, which allows you to override the default server, namely
  “people.freedesktop.org” (João Paulo Rechi Vita)

telepathy-spec 0.23.2 (2011-05-16)
==================================

Changes to existing API
-----------------------

• ChannelDispatcher.DelegateChannels() now calls HandleChannels once per
  Channel. It also returns the list of Channels which have been delegated
  and those which have not. (fdo #37109, Guillaume)

telepathy-spec 0.23.1 (2011-05-09)
==================================

This first release in the 0.23 development branch contains all the fixes and
additions from 0.22.3.

Enhancements:

• Channel.Interface.SMS.GetSMSLength() to allow SMS message chunking to be
  shown to the user. (Danni)

• ChannelDispatcher.DelegateChannels() to move channels between handlers.
  (fdo #25293, Guillaume)

• ChannelDispatcher.PresentChannel(): convenient API to re-ensure an existing
  channel. (fdo #25293, Guillaume)


telepathy-spec 0.22.3 (2011-05-09)
==================================

Fixes:

• Correct DBus_Property-parameter boilerplate. (fdo #37005, Will)

telepathy-spec 0.22.2 (2011-04-20)
==================================

The “every cell stayed the same” release.

Once again, this release in the stable series includes some minor API
additions.

Enhancements:

• Channel.Interface.SMS now includes some sample contact capabilities.
  (Danni)

• Connection.Interface.Balance now has a ManageCreditURI property.
  (fd.o#36254, Danni)

• Connection.Interface.SimplePresence now has a
  MaximumStatusMessageLength property. (fd.o#33054, André)

• SimplePresence defines two new well-known status identifiers: "pstn"
  and "chat". (fd.o#36159, Danni vs. Will)

Fixes:

• Protocol.Interface.Avatars properties are documented to be immutable.
  (Guillaume)

• The tables in SimplePresence and Call's HTML documentation look nicer.

telepathy-spec 0.22.1 (2011-03-30)
==================================

The “we can change the things we know” release.

Unconventionally, this release in the 0.22 stable series of the
specification contains minor API additions. This is not intended to
become a trend; once major changes land in the specification and a
release is made in the 0.23.x unstable series, no new API will be added
to the stable branch.

• A new error code, InsufficientBalance, has been added, along with a
  balance-required key for the CallStateDetails dictionary. (Danni)

• Media.StreamHandler has grown two new method/signal pairs, namely
  SetRemoteFeedbackMessages/SupportedFeedbackMessages and
  SetRemoteHeaderExtensions/SupportedHeaderExtensions, plus some related
  types, for enabling exciting RTP header extensions and RTCP feedback
  messages.

telepathy-spec 0.22.0 (2011-03-21)
==================================

The “literate small talk” release.

This is a new stable version of telepathy-spec, intended to serve as a
reference point for future work. There were no API changes since
development release 0.21.13; significant additions and changes to
non-DRAFT interfaces from the year-and-a-half of development since
0.20.0 are summarized below.

The versions of libraries, connection managers and Mission Control
recommended for use with GNOME 3.0 (such as the upcoming telepathy-glib
0.14) can be expected to support most of the API from this spec release.

Changes to existing API
-----------------------

• Handles are no longer expected to be reference-counted - instead, they
  persist as long as the Connection does. A new property,
  HasImmortalHandles, indicates whether this is the case. Versions of
  telepathy-glib since 0.13.8 implement these semantics, and set that
  property, automatically for most connection managers.

• message-token has been redefined from "globally unique"
  to "whatever's in the underlying protocol", replacing the unimplemented
  protocol-token. This makes it feasible to implement message-token again.
  Note that connection managers implementing message-token should not be
  backported to Maemo 5, since its event logger assumes that message-token
  is guaranteed to be unique, which is usually unimplementable.

• The Messages interface is now mandatory for Text channels.

Enhancements to core API
------------------------

• The Connection has a pair of new methods, AddClientInterest and
  RemoveClientInterest, to allow clients to subscribe to potentially
  bandwidth-costly interfaces (such as MailNotification) in a generic
  way.

• ChannelDispatcher and ChannelRequest now support "request hints"
  (metadata passed through from the requester to the handler), and the
  SucceededWithChannel signal.

New optional interfaces
-----------------------

• The ContactList and ContactGroups interfaces for
  connections are now considered stable, and a new ContactBlocking
  interface has been added. Between them, these interfaces replace
  ContactList channels.

• The Connection.Interface.ClientTypes,
  Connection.Interface.MailNotification,
  Connection.Interface.Powersaving, and Protocol.Interface.Presence
  interfaces are now considered stable.

• Chan.T.ServerAuthentication and Chan.I.SASLAuthentication provide
  interactive querying for credentials, allowing connection without
  saving a password if there is a handler for these channels

• Chan.I.Securable indicates whether a channel is secure

• Account.Interface.Addressing stores user preferences for use of
  accounts for non-primary protocols, such as using SIP for telephony.

Enhancements to optional interfaces
-----------------------------------

• Add a FileTransfer.URI property which can be used to tell other
  Telepathy clients about the location of the transferred
  file.

Changes since 0.21.13
---------------------

• A server-message key for the Details dictionary in the ConnectionError
  signal has been defined. (wjt)
