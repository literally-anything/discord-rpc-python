from setuptools import setup
import discord_rpc

# Use README for the PyPI page
with open('README.md') as f:
    long_description = f.read()

# https://setuptools.readthedocs.io/en/latest/setuptools.html
setup(name='discord-rpc-python',
      author='literally-anything',
      url='https://github.com/qwertyquerty/pypresence',
      version=discord_rpc.__version__,
      packages=['discord_rpc'],
      python_requires='>=3.8',
      platforms=['Windows', 'Linux', 'OSX'],
      zip_safe=True,
      license='MIT',
      description='Discord RPC client written in Python',
      long_description=long_description,
      # PEP 566, PyPI Warehouse, setuptools>=38.6.0 make markdown possible
      long_description_content_type='text/markdown',
      keywords='discord rich presence discord_rpc rpc api wrapper gamers chat irc',

      # Used by PyPI to classify the project and make it searchable
      # Full list: https://pypi.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: MIT License',

          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',

          'Programming Language :: Python',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',

          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: Implementation :: CPython',

          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: Libraries',
          'Topic :: Communications :: Chat',
          'Framework :: AsyncIO',
      ]
      )
