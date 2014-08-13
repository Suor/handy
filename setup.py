from setuptools import setup

setup(
    name='handy',
    version='0.3',
    author='Alexander Schepanovski',
    author_email='suor.web@gmail.com',

    description='A collection of tools to make your django life easier.',
    long_description=open('README.rst').read(),
    url='http://github.com/Suor/handy',
    license='BSD',

    packages=['handy', 'handy.forms', 'handy.models'],
    install_requires=[
        'django>=1.2',
        'pytz>=2012j',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',

        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
