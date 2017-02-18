import unittest

from swift.common import swob
from data_locker import middleware as md


class FakeApp(object):

    def __call__(self, env, start_response):
        return swob.Response('Fake Test App')(env, start_response)


class DataLockerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = md.DataLocker(FakeApp(), {})
