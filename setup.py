from setuptools import setup

_dosocs2_version = '0.16.1'

install_requires=[
    'jinja2',
    'python-magic',
    'docopt',
    'SQLAlchemy',
    'psycopg2'
    ]

tests_require=[
    'pytest',
    'mock'
    ]

setup(
    name='dosocs2',
    version=_dosocs2_version,
    description='SPDX 2.0 document creation and storage',
    long_description='',
    url='https://github.com/DoSOCSv2/DoSOCSv2',
    author='Thomas T. Gurney',
    author_email='tgurney@unomaha.edu',
    license='GNU General Public License v2 or later (GPLv2+)',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        ],

    keywords='spdx license licenses',
    packages=['dosocs2', 'dosocs2.scanners'],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'tests': install_requires + tests_require,
        },
    package_data={'dosocs2': ['templates/*', 'fixtures/*']},

    entry_points={'console_scripts': ['dosocs2=dosocs2.dosocs2:main']},
    test_suite='py.test',

    zip_safe=False,
)
