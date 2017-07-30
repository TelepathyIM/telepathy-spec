#!/usr/bin/env python3

import sys
import os.path

test_dir = os.path.dirname (sys.argv[0])
sys.path.insert (0, os.path.join (test_dir, '../tools/'))

import specparser

spec_path = os.path.join (test_dir, 'input/all.xml')

def test_specparser ():
    """
>>> spec = specparser.parse (spec_path, 'org.freedesktop.Telepathy.SpecAutoGenTest')
>>> spec
Spec(telepathy-spec tools test case)

>>> spec.interfaces
[Interface(org.freedesktop.Telepathy.SpecAutoGenTest)]

>>> sorted(spec.errors.items())
[('org.freedesktop.Telepathy.SpecAutoGenTest.MiscError', Error(org.freedesktop.Telepathy.SpecAutoGenTest.MiscError)), ('org.freedesktop.Telepathy.SpecAutoGenTest.OtherError', Error(org.freedesktop.Telepathy.SpecAutoGenTest.OtherError))]

>>> spec.generic_types
[]
>>> sorted(spec.types)
['Adjective', 'Test_Flags', 'UV']
>>> [ spec.types[x] for x in sorted(spec.types) ]
[Enum(Adjective), Flags(Test_Flags), Struct(UV)]

>>> i = spec.interfaces[0]
>>> i
Interface(org.freedesktop.Telepathy.SpecAutoGenTest)

>>> print(i.causes_havoc)
None

>>> i.methods
[Method(org.freedesktop.Telepathy.SpecAutoGenTest.DoStuff)]

>>> i.methods[0].args
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'Method' object has no attribute 'args'
>>> i.methods[0].in_args
[Arg(org.freedesktop.Telepathy.SpecAutoGenTest.DoStuff.badger:b), Arg(org.freedesktop.Telepathy.SpecAutoGenTest.DoStuff.mushroom:a{sv}), Arg(org.freedesktop.Telepathy.SpecAutoGenTest.DoStuff.snake:s)]
>>> i.methods[0].out_args
[Arg(org.freedesktop.Telepathy.SpecAutoGenTest.DoStuff.misc:a(uv))]

>>> i.methods[0].possible_errors
[PossibleError(org.freedesktop.Telepathy.SpecAutoGenTest.MiscError), PossibleError(org.freedesktop.Telepathy.SpecAutoGenTest.OtherError)]
>>> list(map (lambda e: e.get_error (), i.methods[0].possible_errors))
[Error(org.freedesktop.Telepathy.SpecAutoGenTest.MiscError), Error(org.freedesktop.Telepathy.SpecAutoGenTest.OtherError)]

>>> i.signals
[Signal(org.freedesktop.Telepathy.SpecAutoGenTest.StuffHappened)]

>>> i.signals[0].args
[Arg(org.freedesktop.Telepathy.SpecAutoGenTest.StuffHappened.stoat:ay), Arg(org.freedesktop.Telepathy.SpecAutoGenTest.StuffHappened.ferret:s), Arg(org.freedesktop.Telepathy.SpecAutoGenTest.StuffHappened.weasel:b)]

>>> i.properties
[Property(org.freedesktop.Telepathy.SpecAutoGenTest.Introspective:b)]

>>> i.properties[0].type
''
>>> i.properties[0].dbus_type
'b'
>>> print(i.properties[0].get_type())
None

>>> i.types
[Enum(Adjective), Flags(Test_Flags), Struct(UV)]

>>> i.types[0].values
[EnumValue(Adjective.Leveraging), EnumValue(Adjective.Synergistic)]
>>> list(map (lambda v: (v.short_name, v.value), i.types[0].values))
[('Leveraging', '0'), ('Synergistic', '1')]

>>> i.types[1].values
[EnumValue(Test_Flags.LowBit), EnumValue(Test_Flags.HighBit)]
>>> list(map (lambda v: (v.short_name, v.value), i.types[1].values))
[('LowBit', '1'), ('HighBit', '128')]

>>> sorted(spec.everything.items())
[('org.freedesktop.Telepathy.SpecAutoGenTest', ClientInterest(org.freedesktop.Telepathy.SpecAutoGenTest)), ('org.freedesktop.Telepathy.SpecAutoGenTest.DoStuff', Method(org.freedesktop.Telepathy.SpecAutoGenTest.DoStuff)), ('org.freedesktop.Telepathy.SpecAutoGenTest.Introspective', Property(org.freedesktop.Telepathy.SpecAutoGenTest.Introspective:b)), ('org.freedesktop.Telepathy.SpecAutoGenTest.StuffHappened', Signal(org.freedesktop.Telepathy.SpecAutoGenTest.StuffHappened)), ('org.freedesktop.Telepathy.SpecAutoGenTest.wobbly', AwkwardTelepathyProperty(org.freedesktop.Telepathy.SpecAutoGenTest.wobbly:b)), ('org.freedesktop.Telepathy.SpecAutoGenTest/badgers', ClientInterest(org.freedesktop.Telepathy.SpecAutoGenTest/badgers))]


>>> list(map (lambda o: i.added, spec.everything.values ()))
[None, None, None, None, None, None]
>>> list(map (lambda o: i.deprecated, spec.everything.values ()))
[None, None, None, None, None, None]
    """

if __name__ == '__main__':
    import doctest
    doctest.testmod ()
