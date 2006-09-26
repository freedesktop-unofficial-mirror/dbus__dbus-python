#!/usr/bin/env python
import sys
import os
import unittest
import time

builddir = os.environ["DBUS_TOP_BUILDDIR"]
pydir = builddir

sys.path.insert(0, pydir)
sys.path.insert(0, pydir + 'dbus')

import _dbus_bindings
import dbus
import dbus.types as types

pkg = dbus.__file__
if not pkg.startswith(pydir):
    raise Exception("DBus modules (%s) are not being picked up from the package"%pkg)

if not _dbus_bindings.__file__.startswith(pydir):
    raise Exception("DBus modules (%s) are not being picked up from the package"%_dbus_bindings.__file__)

class TestTypes(unittest.TestCase):

    def test_append(self):
        aeq = self.assertEquals
        from _dbus_bindings import SignalMessage
        s = SignalMessage('/', 'foo.bar', 'baz')
        s.append([types.Byte(1)], signature='ay')
        aeq(s.get_signature(), 'ay')
        aeq(s.get_args_list(), [[types.Byte(1)]])

        s = SignalMessage('/', 'foo.bar', 'baz')
        s.append([], signature='ay')
        aeq(s.get_args_list(), [[]])

    def test_append_ByteArray(self):
        aeq = self.assertEquals
        from _dbus_bindings import SignalMessage
        s = SignalMessage('/', 'foo.bar', 'baz')
        s.append(types.ByteArray('ab'), signature='ay')
        aeq(s.get_args_list(), [[types.Byte('a'), types.Byte('b')]])
        s = SignalMessage('/', 'foo.bar', 'baz')
        s.append(types.ByteArray('ab'), signature='av')
        aeq(s.get_args_list(), [[types.Variant(types.Byte('a')),
                                 types.Variant(types.Byte('b'))]])

    def test_append_Variant(self):
        a = self.assert_
        aeq = self.assertEquals
        from _dbus_bindings import SignalMessage
        s = SignalMessage('/', 'foo.bar', 'baz')
        s.append(types.Variant(1, signature='i'),
                 types.Variant('a', signature='s'),
                 types.Variant([(types.Variant('a', signature='y'), 'b'),
                                (types.Variant(123, signature='u'), 1)],
                               signature='a(vy)'))
        aeq(s.get_signature(), 'vvv')
        args = s.get_args_list()
        aeq(args[0].__class__, types.Variant)
        aeq(args[0].signature, 'i')
        aeq(args[0].object.__class__, types.Int32)
        aeq(args[0].object, 1)
        aeq(args[1].__class__, types.Variant)
        aeq(args[1].signature, 's')
        a(isinstance(args[1].object, unicode))
        aeq(args[2].__class__, types.Variant)
        aeq(args[1].object, 'a')
        aeq(args[2].signature, 'a(vy)')
        avy = args[2].object
        aeq(avy.__class__, types.Array)
        aeq(len(avy), 2)
        aeq(avy[0].__class__, tuple)
        aeq(len(avy[0]), 2)
        aeq(avy[0][0].__class__, types.Variant)
        aeq(avy[0][0].signature, 'y')
        aeq(avy[0][0].object.__class__, types.Byte)
        aeq(avy[0][0].object, types.Byte('a'))
        aeq(avy[0][1].__class__, types.Byte)
        aeq(avy[0][1], types.Byte('b'))
        aeq(avy[1].__class__, tuple)
        aeq(len(avy[1]), 2)
        aeq(avy[1][0].__class__, types.Variant)
        aeq(avy[1][0].signature, 'u')
        aeq(avy[1][0].object.__class__, types.UInt32)
        aeq(avy[1][0].object, 123)
        aeq(avy[1][1].__class__, types.Byte)
        aeq(avy[1][1], types.Byte(1))

    def test_Variant(self):
        Variant = types.Variant
        a = self.assert_
        a(Variant(1, 'i') == Variant(1, 'i'))
        a(not (Variant(1, 'i') == Variant(1, 'u')))
        a(not (Variant(1, 'i') == Variant(2, 'i')))
        a(not (Variant(1, 'i') == Variant(2, 'u')))
        a(not (Variant(1, 'i') != Variant(1, 'i')))
        a(Variant(1, 'i') != Variant(1, 'u'))
        a(Variant(1, 'i') != Variant(2, 'i'))
        a(Variant(1, 'i') != Variant(2, 'u'))

    def test_Signature(self):
        self.assertRaises(Exception, types.Signature, 'a')
        self.assertEquals(types.Signature('ab'), 'ab')
        self.assert_(isinstance(types.Signature('ab'), str))
        self.assertEquals(tuple(types.Signature('ab(xt)a{sv}')),
                          ('ab', '(xt)', 'a{sv}'))
        self.assert_(isinstance(tuple(types.Signature('ab'))[0],
                                types.Signature))

    def test_guess_signature(self):
        aeq = self.assertEquals
        from _dbus_bindings import Message
        aeq(Message.guess_signature(('a','b')), '(ss)')
        aeq(Message.guess_signature('a','b'), 'ss')
        aeq(Message.guess_signature(['a','b']), 'as')
        aeq(Message.guess_signature(('a',)), '(s)')
        aeq(Message.guess_signature('abc'), 's')
        aeq(Message.guess_signature(types.Int32(123)), 'i')
        aeq(Message.guess_signature(('a',)), '(s)')
        aeq(Message.guess_signature(['a']), 'as')
        aeq(Message.guess_signature({'a':'b'}), 'a{ss}')

if __name__ == '__main__':
    unittest.main()
