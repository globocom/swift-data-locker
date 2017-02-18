"""
``data_locker`` is a middleware which prevents important data be changed by
mistake. It works like a real locker, when it is closed, the data will not be
modified.

``data_locker`` uses ``x-(account|container)-meta-data-locker``
metadata entry to lock the data.

The ``data_locker`` middleware should be added to the pipeline in
your ``/etc/swift/proxy-server.conf`` file just after any auth middleware.
For example:

    [pipeline:main]
    pipeline = catch_errors cache tempauth data_locker proxy-server

    [filter:data_locker]
    use = egg:swift#data_locker

To enable the metadata indexing on an account level:

    swift post -m data-locker:delete

To enable the metadata indexing on an container level:

    swift post container -m data-locker:delete

Remove the metadata indexing:

    swift post -m data-locker:
"""

from swift.common import swob, utils
from swift.proxy.controllers.base import get_account_info, get_container_info

META_DATA_LOCKER = 'data-locker'
METHODS = {
    'delete': ['delete'],
    'create': ['post', 'put']
}


class DataLocker(object):
    """
    Swift Data Locker middleware
    See above for a full description.
    """

    def __init__(self, app, conf):
        self.logger = utils.get_logger(conf, log_route='data-locker')

        self.app = app
        self.conf = conf

        self.logger.info('Data Locker middleware started...')

    @swob.wsgify
    def __call__(self, req):

        # Get will never be locked
        if req.method.lower() == 'get':
            return self.app

        locked_methods = self._get_req_lockers(req)

        if req.method.lower() in locked_methods:
            self.logger.info('{} {} blocked'.format(req.method, req.path_info))
            return swob.HTTPForbidden()

        return self.app

    def _get_req_lockers(self, req):
        """ GET container and account locker metadata from request """

        locker_methods = []

        sysmeta_acc = get_account_info(req.environ, self.app).get('meta')
        lockers_acc = sysmeta_acc.get(META_DATA_LOCKER, '').split(',')

        for locker in lockers_acc:
            _locker = locker.strip().lower()
            locker_methods = locker_methods + METHODS.get(_locker, [])

        sysmeta_con = get_container_info(req.environ, self.app).get('meta')
        lockers_con = sysmeta_con.get(META_DATA_LOCKER, '').split(',')

        for locker in lockers_con:
            _locker = locker.strip().lower()
            locker_methods = locker_methods + METHODS.get(_locker, [])

        return list(set(locker_methods))


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    # Registers information to be retrieved on /info
    utils.register_swift_info('data_locker')

    def filter(app):
        return DataLocker(app, conf)

    return filter
