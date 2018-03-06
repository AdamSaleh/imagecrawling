"""Tests for our main imagecrawling CLI module."""


from subprocess import PIPE, Popen as popen
from unittest import TestCase

from imagecrawling import __version__ as VERSION

class TestHelp(TestCase):
    def test_returns_usage_information(self):
        output = popen(['imagecrawling', '-h'], stdout=PIPE).communicate()[0]
        self.assertTrue('Usage:' in output)

        output = popen(['imagecrawling', '--help'], stdout=PIPE).communicate()[0]
        self.assertTrue('Usage:' in output)
