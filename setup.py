from setuptools import setup

install_requires=[
    'jinja2',
    'python-magic',
    'docopt',
    'SQLAlchemy',
    'xmltodict',
    ]

tests_require=[
    'pytest'
    ]

postgres_requires=[
    'psycopg2'
    ]

setup(
    name='dosocs2',
    version='0.13.0',
    description='SPDX 2.0 document creation and storage',
    long_description='',
    url='https://github.com/ttgurney/dosocs2',
    author='Thomas T. Gurney',
    author_email='tgurney@unomaha.edu',
    license='Apache Software License',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        ],

    keywords='spdx license licenses',
    packages=['dosocs2'],
    install_requires=[
        'jinja2',
        'python-magic',
        'docopt',
        'SQLAlchemy',
        'xmltodict',
        ],
    tests_require=tests_require,
    extras_require={
        'tests': install_requires + tests_require,
        'postgres': install_requires + postgres_requires,
        },
    package_data={'dosocs2': ['templates/*']},

    entry_points={'console_scripts': ['dosocs2=dosocs2.dosocs2:main']},
    test_suite='py.test',

    zip_safe=False,
)
