#!/usr/bin/env python

import sys
import os.path

test_dir = os.path.dirname (sys.argv[0])
sys.path.insert (0, os.path.join (test_dir, '../tools/'))

import specparser

spec_path = os.path.join (test_dir, 'input/all.xml')

def test_specparser ():
    """
>>> spec = specparser.parse (spec_path, 'im.telepathy.v1.SpecAutoGenTest')
>>> spec
Spec(telepathy-spec tools test case)

>>> spec.interfaces
[Interface(im.telepathy.v1.SpecAutoGenTest)]

>>> sorted(spec.errors.items())
[(u'im.telepathy.v1.SpecAutoGenTest.MiscError', Error(im.telepathy.v1.SpecAutoGenTest.MiscError)), (u'im.telepathy.v1.SpecAutoGenTest.OtherError', Error(im.telepathy.v1.SpecAutoGenTest.OtherError))]

>>> spec.generic_types
[]
>>> spec.types
{u'Adjective': Enum(Adjective), u'Test_Flags': Flags(Test_Flags), u'UV': Struct(UV)}

>>> i = spec.interfaces[0]
>>> i
Interface(im.telepathy.v1.SpecAutoGenTest)

>>> print i.causes_havoc
None

>>> i.methods
[Method(im.telepathy.v1.SpecAutoGenTest.DoStuff)]

>>> i.methods[0].args
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'Method' object has no attribute 'args'
>>> i.methods[0].in_args
[Arg(im.telepathy.v1.SpecAutoGenTest.DoStuff.badger:b), Arg(im.telepathy.v1.SpecAutoGenTest.DoStuff.mushroom:a{sv}), Arg(im.telepathy.v1.SpecAutoGenTest.DoStuff.snake:s)]
>>> i.methods[0].out_args
[Arg(im.telepathy.v1.SpecAutoGenTest.DoStuff.misc:a(uv))]

>>> i.methods[0].possible_errors
[PossibleError(im.telepathy.v1.SpecAutoGenTest.MiscError), PossibleError(im.telepathy.v1.SpecAutoGenTest.OtherError)]
>>> map (lambda e: e.get_error (), i.methods[0].possible_errors)
[Error(im.telepathy.v1.SpecAutoGenTest.MiscError), Error(im.telepathy.v1.SpecAutoGenTest.OtherError)]

>>> i.signals
[Signal(im.telepathy.v1.SpecAutoGenTest.StuffHappened)]

>>> i.signals[0].args
[Arg(im.telepathy.v1.SpecAutoGenTest.StuffHappened.stoat:ay), Arg(im.telepathy.v1.SpecAutoGenTest.StuffHappened.ferret:s), Arg(im.telepathy.v1.SpecAutoGenTest.StuffHappened.weasel:b)]

>>> i.properties
[Property(im.telepathy.v1.SpecAutoGenTest.Introspective:b)]

>>> i.properties[0].type
''
>>> i.properties[0].dbus_type
u'b'
>>> print i.properties[0].get_type ()
None

>>> i.types
[Enum(Adjective), Flags(Test_Flags), Struct(UV)]

>>> i.types[0].values
[EnumValue(Adjective.Leveraging), EnumValue(Adjective.Synergistic)]
>>> map (lambda v: (v.short_name, v.value), i.types[0].values)
[(u'Leveraging', u'0'), (u'Synergistic', u'1')]

>>> i.types[1].values
[EnumValue(Test_Flags.LowBit), EnumValue(Test_Flags.HighBit)]
>>> map (lambda v: (v.short_name, v.value), i.types[1].values)
[(u'LowBit', u'1'), (u'HighBit', u'128')]

>>> sorted(spec.everything.items())
[(u'im.telepathy.v1.SpecAutoGenTest', ClientInterest(im.telepathy.v1.SpecAutoGenTest)), (u'im.telepathy.v1.SpecAutoGenTest.DoStuff', Method(im.telepathy.v1.SpecAutoGenTest.DoStuff)), (u'im.telepathy.v1.SpecAutoGenTest.Introspective', Property(im.telepathy.v1.SpecAutoGenTest.Introspective:b)), (u'im.telepathy.v1.SpecAutoGenTest.StuffHappened', Signal(im.telepathy.v1.SpecAutoGenTest.StuffHappened)), (u'im.telepathy.v1.SpecAutoGenTest/badgers', ClientInterest(im.telepathy.v1.SpecAutoGenTest/badgers))]


>>> map (lambda o: i.added, spec.everything.values ())
[None, None, None, None, None]
>>> map (lambda o: i.deprecated, spec.everything.values ())
[None, None, None, None, None]
    """

if __name__ == '__main__':
    import doctest
    doctest.testmod ()
