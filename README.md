# Swift Data Locker

``data_locker`` is a middleware which prevents data from being miss changed.
Once the data-locker middleware is properly set, any request that could change
data will be blocked (403 Frobidden).

This middleware don't intend to fully protect your data from being
changed/deleted. Anyone with the proper credentials, can unset the
``data-locker`` header and delete/modify your data. It only protects from being
changed by accident.

``data_locker`` uses ``x-(account|container)-meta-data-locker`` metadata entry
to lock the data.

The ``data_locker`` middleware should be added to the pipeline in
your ``/etc/swift/proxy-server.conf`` file just after any auth middleware.
For example:

    [pipeline:main]
    pipeline = catch_errors cache tempauth data_locker proxy-server

    [filter:data_locker]
    use = egg:swift_data_locker#data_locker

To block delete requests on account level:

    swift post -m data-locker:delete

To block delete requests on container level:

    swift post container -m data-locker:delete

To block put/post requests on account level:

    swift post -m data-locker:create

To block put/post requests on container level:

    swift post container -m data-locker:create

To block put/post/delete requests on account level:

    swift post -m data-locker:'create,delete'

To block put/post requests on container level:

    swift post container -m data-locker:'create,delete'

To unlock requests:

    swift post -m data-locker:

# Usage example:

    $ swift post test
    $ echo "test" > test_file
    $ swift upload test test_file
    test_file
    $ swift list test
    test_file
    $ swift delete test test_file
    test_file
    $ swift list test
    $ swift post test -m data-locker:delete
    $ swift upload test test_file
    test_file
    $ swift list test
    test_file
    $ swift delete test test_file
    Error Deleting: test/test_file: Object DELETE failed: http://saio:8080/v1/AUTH_test/test/test_file 403 Forbidden  [first 60 chars of response] <html><h1>Forbidden</h1><p>Access was denied to this resourc
    $ swift post test -m data-locker:
    $ swift delete test test_file
    test_file
    $ swift list test
    $

# Testing

    pip install -r requirements_test.txt
    make tests

# Team

Created by Storm @ Globo.com
