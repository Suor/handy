from setuptools import setup

setup(
    name='handy',
    version='0.6',
    author='Alexander Schepanovski',
    author_email='suor.web@gmail.com',

    description='A collection of tools to make your django life easier.',
    long_description=open('README.rst').read(),
    url='http://github.com/Suor/handy',
    license='BSD',

    packages=['handy', 'handy.forms', 'handy.models'],
    install_requires=[
        'Django>=1.2',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',

        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
