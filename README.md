# Swift Data Locker

Middleware for OpenStack Swift that implements a locker to protect data from being changed.

``data_locker`` is a middleware which prevents important data from be changed by
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

# Testing

    pip install -r requirements_test.txt
    make tests

# Team

Created by Storm @ Globo.com
