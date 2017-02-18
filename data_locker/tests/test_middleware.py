import unittest

from mock import patch
from swift.common import swob
from data_locker import middleware as md


class FakeApp(object):

    def __call__(self, env, start_response):
        return swob.Response('Fake Test App')(env, start_response)


class DataLockerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = md.DataLocker(FakeApp(), {})

    def test_get_request(self):
        response = swob.Request.blank(
            '/v1/a/c/o',
            environ={'REQUEST_METHOD': 'GET'}
        ).get_response(self.app)

        self.assertEqual(response.status, '200 OK')

    def test_unlocked_delete_request(self):
        response = swob.Request.blank(
            '/v1/a/c/o',
            environ={'REQUEST_METHOD': 'DELETE'}
        ).get_response(self.app)

        self.assertEqual(response.status, '200 OK')

    @patch('data_locker.middleware.get_container_info')
    def test_delete_req_with_container_locked(self, mock):

        mock.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'delete'
            }
        }

        response = swob.Request.blank(
            '/v1/a/c/o',
            environ={'REQUEST_METHOD': 'DELETE'}
        ).get_response(self.app)

        self.assertEqual(response.status, '403 Forbidden')

    @patch('data_locker.middleware.get_account_info')
    def test_delete_req_with_account_locked(self, mock):

        mock.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'delete'
            }
        }

        response = swob.Request.blank(
            '/v1/a/c/o',
            environ={'REQUEST_METHOD': 'DELETE'}
        ).get_response(self.app)

        self.assertEqual(response.status, '403 Forbidden')

    @patch('data_locker.middleware.get_container_info')
    def test_put_req_with_container_locked_for_delete(self, mock):
        """
        Test PUT request in a container locked for delete. It should work
        properly
        """

        mock.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'delete'
            }
        }

        response = swob.Request.blank(
            '/v1/a/c/o',
            environ={'REQUEST_METHOD': 'PUT'}
        ).get_response(self.app)

        self.assertEqual(response.status, '200 OK')

    @patch('data_locker.middleware.get_account_info')
    def test_put_req_with_account_locked_for_delete(self, mock):
        """
        Test PUT request in a account locked for delete. It should work
        properly
        """

        mock.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'delete'
            }
        }

        response = swob.Request.blank(
            '/v1/a/c/o',
            environ={'REQUEST_METHOD': 'PUT'}
        ).get_response(self.app)

        self.assertEqual(response.status, '200 OK')

    @patch('data_locker.middleware.get_container_info')
    def test_put_post_req_with_container_locked(self, mock):
        """ Test PUT request in a container locked. It should be forbidden """

        mock.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'create'
            }
        }

        response = swob.Request.blank(
            '/v1/a/c/o',
            environ={'REQUEST_METHOD': 'PUT'}
        ).get_response(self.app)

        self.assertEqual(response.status, '403 Forbidden')

        response = swob.Request.blank(
            '/v1/a/c/o',
            environ={'REQUEST_METHOD': 'POST'}
        ).get_response(self.app)

        self.assertEqual(response.status, '403 Forbidden')

    @patch('data_locker.middleware.get_account_info')
    def test_put_post_req_with_account_locked(self, mock):
        """ Test PUT request in a account locked. It should be forbidden """

        mock.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'create'
            }
        }

        response = swob.Request.blank(
            '/v1/a/c/o',
            environ={'REQUEST_METHOD': 'PUT'}
        ).get_response(self.app)

        self.assertEqual(response.status, '403 Forbidden')

        response = swob.Request.blank(
            '/v1/a/c/o',
            environ={'REQUEST_METHOD': 'POST'}
        ).get_response(self.app)

        self.assertEqual(response.status, '403 Forbidden')


class GetLockersTestCase(unittest.TestCase):
    """ Testacase for the _get_req_lockers method """

    def setUp(self):
        self.app = md.DataLocker(FakeApp(), {})

    @patch('data_locker.middleware.get_container_info')
    @patch('data_locker.middleware.get_account_info')
    def test_no_lockers_set(self, mock_acc, mock_con):

        req = swob.Request.blank('/v1/a/c/o')
        lockers = self.app._get_req_lockers(req)

        self.assertEqual(lockers, [])

    @patch('data_locker.middleware.get_container_info')
    @patch('data_locker.middleware.get_account_info')
    def test_delete_on_container(self, mock_acc, mock_con):
        """ Delete set on container """

        mock_con.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'delete'
            }
        }

        req = swob.Request.blank('/v1/a/c/o')
        computed = self.app._get_req_lockers(req)
        expected = md.METHODS['delete']

        self.assertEqual(computed, expected)

    @patch('data_locker.middleware.get_container_info')
    @patch('data_locker.middleware.get_account_info')
    def test_delete_on_account(self, mock_acc, mock_con):
        """ Delete set on account """

        mock_acc.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'delete'
            }
        }

        req = swob.Request.blank('/v1/a/c/o')
        computed = self.app._get_req_lockers(req)
        expected = md.METHODS['delete']

        self.assertEqual(computed, expected)

    @patch('data_locker.middleware.get_container_info')
    @patch('data_locker.middleware.get_account_info')
    def test_delete_on_both(self, mock_acc, mock_con):
        """ Delete set on account and container """

        mock_acc.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'delete'
            }
        }

        mock_con.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'delete'
            }
        }

        req = swob.Request.blank('/v1/a/c/o')
        computed = self.app._get_req_lockers(req)
        expected = md.METHODS['delete']

        self.assertEqual(computed, expected)

    @patch('data_locker.middleware.get_container_info')
    @patch('data_locker.middleware.get_account_info')
    def test_delete_on_account_create_on_container(self, mock_acc, mock_con):
        """ Delete set on account, create on container """

        mock_acc.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'delete'
            }
        }

        mock_con.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'create'
            }
        }

        req = swob.Request.blank('/v1/a/c/o')
        computed = self.app._get_req_lockers(req)
        expected = md.METHODS['delete'] + md.METHODS['create']

        self.assertEqual(sorted(computed), sorted(expected))

    @patch('data_locker.middleware.get_container_info')
    @patch('data_locker.middleware.get_account_info')
    def test_create_on_account_delete_on_container(self, mock_acc, mock_con):
        """ Delete set on account, create on container """

        mock_acc.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'create'
            }
        }

        mock_con.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'delete'
            }
        }

        req = swob.Request.blank('/v1/a/c/o')
        computed = self.app._get_req_lockers(req)
        expected = md.METHODS['delete'] + md.METHODS['create']

        self.assertEqual(sorted(computed), sorted(expected))

    @patch('data_locker.middleware.get_container_info')
    @patch('data_locker.middleware.get_account_info')
    def test_create_on_both(self, mock_acc, mock_con):
        """ Delete set on account and container """

        mock_acc.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'create'
            }
        }

        mock_con.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'create'
            }
        }

        req = swob.Request.blank('/v1/a/c/o')
        computed = self.app._get_req_lockers(req)
        expected = md.METHODS['create']

        self.assertEqual(sorted(computed), sorted(expected))

    @patch('data_locker.middleware.get_container_info')
    @patch('data_locker.middleware.get_account_info')
    def test_create_on_container(self, mock_acc, mock_con):
        """ Delete set on container """

        mock_con.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'create'
            }
        }

        req = swob.Request.blank('/v1/a/c/o')
        computed = self.app._get_req_lockers(req)
        expected = md.METHODS['create']

        self.assertEqual(sorted(computed), sorted(expected))

    @patch('data_locker.middleware.get_container_info')
    @patch('data_locker.middleware.get_account_info')
    def test_create_on_account(self, mock_acc, mock_con):
        """ Delete set on container """

        mock_acc.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'create'
            }
        }

        req = swob.Request.blank('/v1/a/c/o')
        computed = self.app._get_req_lockers(req)
        expected = md.METHODS['create']

        self.assertEqual(sorted(computed), sorted(expected))

    @patch('data_locker.middleware.get_container_info')
    @patch('data_locker.middleware.get_account_info')
    def test_create_and_delete_on_container(self, mock_acc, mock_con):
        """ Delete set on container """

        mock_con.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'create, delete'
            }
        }

        req = swob.Request.blank('/v1/a/c/o')
        computed = self.app._get_req_lockers(req)
        expected = md.METHODS['delete'] + md.METHODS['create']

        self.assertEqual(sorted(computed), sorted(expected))

    @patch('data_locker.middleware.get_container_info')
    @patch('data_locker.middleware.get_account_info')
    def test_create_and_delete_on_account(self, mock_acc, mock_con):
        """ Delete set on container """

        mock_acc.return_value = {
            'meta': {
                md.META_DATA_LOCKER: 'delete, create'
            }
        }

        req = swob.Request.blank('/v1/a/c/o')
        computed = self.app._get_req_lockers(req)
        expected = md.METHODS['create'] + md.METHODS['delete']

        self.assertEqual(sorted(computed), sorted(expected))


if __name__ == '__main__':
    unittest.main()
