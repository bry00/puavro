import re
from os import path
from io import open
from setuptools import setup
NAME = 'puavro'
PACKAGE = 'puavro'
DESCRIPTION = "Pulsar AVRO interface allowing to read/write AVRO messages from/to dict"

here = path.abspath(path.dirname(__file__))

def readme():
    try:
        with open('README.md', "r", encoding="utf-8") as f:
            return f.read()
    except:
        return DESCRIPTION


def read(*parts):
    with open(path.join(here, *parts), "r", encoding="utf-8") as f:
        return f.read()


def find_version(*file_paths):
    version_file = read(*file_paths, "__init__.py")
    version_match = re.search(r"^\s*__version__\s*=\s*['\"]([^'\"]*)['\"].*",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


VERSION = find_version(PACKAGE)


setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=readme(),
      long_description_content_type='text/markdown',
      url="https://github.com/bry00/puavro",
      author='Bartek Rybak',
      license='MIT',
      packages=[PACKAGE],
      keywords="pulsar avro",
      zip_safe=False,
      install_requires=[
          'fastavro>=1.4.4',
          'pulsar-client>=2.7.0',
      ],
      python_requires='>=3.8',
      classifiers=[
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
      ])

