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
    Swift data locker middleware
    See above for a full description.
    """

    def __init__(self, app, conf):
        self.logger = utils.get_logger(conf, log_route='data-locker')

        self.app = app
        self.conf = conf

    @swob.wsgify
    def __call__(self, req):

        return self.app


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    # Registers information to be retrieved on /info
    utils.register_swift_info('data_locker')

    def filter(app):
        return DataLocker(app, conf)

    return filter
