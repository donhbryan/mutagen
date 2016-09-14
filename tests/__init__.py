# -*- coding: utf-8 -*-

import re
import os
import warnings
import shutil
from tempfile import mkstemp
from unittest import TestCase as BaseTestCase

try:
    import pytest
except ImportError:
    raise SystemExit("pytest missing: sudo apt-get install python-pytest")

from mutagen._compat import PY3
from mutagen._toolsutil import fsencoding, is_fsnative


DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
if os.name == "nt" and not PY3:
    DATA_DIR = DATA_DIR.decode("ascii")
assert is_fsnative(DATA_DIR)


if os.name != "nt":
    try:
        u"öäü".encode(fsencoding())
    except ValueError:
        raise RuntimeError("This test suite needs a unicode locale encoding. "
                           "Try setting LANG=C.UTF-8")


# Make sure we see all deprecation warnings so we either have to avoid them
# or capture them in the test suite
warnings.simplefilter("always")
warnings.simplefilter("ignore", PendingDeprecationWarning)


def get_temp_copy(path):
    """Returns a copy of the file with the same extension"""

    ext = os.path.splitext(path)[-1]
    fd, filename = mkstemp(suffix=ext)
    os.close(fd)
    shutil.copy(path, filename)
    return filename


def get_temp_empty(ext=""):
    """Returns an empty file with the extension"""

    fd, filename = mkstemp(suffix=ext)
    os.close(fd)
    return filename


class TestCase(BaseTestCase):

    def failUnlessRaisesRegexp(self, exc, re_, fun, *args, **kwargs):
        def wrapped(*args, **kwargs):
            try:
                fun(*args, **kwargs)
            except Exception as e:
                self.failUnless(re.search(re_, str(e)))
                raise
        self.failUnlessRaises(exc, wrapped, *args, **kwargs)

    # silence deprec warnings about useless renames
    failUnless = BaseTestCase.assertTrue
    failIf = BaseTestCase.assertFalse
    failUnlessEqual = BaseTestCase.assertEqual
    failUnlessRaises = BaseTestCase.assertRaises
    failUnlessAlmostEqual = BaseTestCase.assertAlmostEqual
    failIfEqual = BaseTestCase.assertNotEqual
    failIfAlmostEqual = BaseTestCase.assertNotAlmostEqual
    assertEquals = BaseTestCase.assertEqual
    assertNotEquals = BaseTestCase.assertNotEqual
    assert_ = BaseTestCase.assertTrue

    def assertReallyEqual(self, a, b):
        self.assertEqual(a, b)
        self.assertEqual(b, a)
        self.assertTrue(a == b)
        self.assertTrue(b == a)
        self.assertFalse(a != b)
        self.assertFalse(b != a)
        if not PY3:
            self.assertEqual(0, cmp(a, b))
            self.assertEqual(0, cmp(b, a))

    def assertReallyNotEqual(self, a, b):
        self.assertNotEqual(a, b)
        self.assertNotEqual(b, a)
        self.assertFalse(a == b)
        self.assertFalse(b == a)
        self.assertTrue(a != b)
        self.assertTrue(b != a)
        if not PY3:
            self.assertNotEqual(0, cmp(a, b))
            self.assertNotEqual(0, cmp(b, a))


def check():
    return pytest.main(args=[os.path.join("tests", "quality")])


def unit(run=[], exitfirst=False):
    args = []

    if run:
        args.append("-k")
        args.append(" or ".join(run))

    if exitfirst:
        args.append("-x")

    args.extend(["-m", "not quality"])

    args.append("tests")

    return pytest.main(args=args)
