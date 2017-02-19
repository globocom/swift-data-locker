from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name="swift_data_locker",
    version=version,
    description='Swift Search Middleware',
    license='Apache License (2.0)',
    author='Storm Team Globo.com',
    author_email='storm@corp.globo.com',
    url='https://git@github.com:globocom/swift-data-locker.git',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Environment :: No Input/Output (Daemon)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    scripts=[],
    entry_points={
        'paste.filter_factory': [
            ('data_locker=data_locker.middleware:'
             'filter_factory')
        ]
    }
)
