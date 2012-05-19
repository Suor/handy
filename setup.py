from setuptools import setup

setup(
    name='handy',
    version='0.1',
    author='Alexander Schepanovski',
    author_email='suor.web@gmail.com',

    description='A collection of tools to make your django life easier.',
    long_description=open('README.rst').read(),
    url='http://github.com/Suor/handy',
    license='BSD',

    packages=['handy'],
    install_requires=[
        'django>=1.2',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
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
