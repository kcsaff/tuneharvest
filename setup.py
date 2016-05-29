import os
from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession

version = '0.9.0b'

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()

try:
   import pypandoc
   description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
   description = read('README.md')

install_reqs = parse_requirements('requirements.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(name='tuneharvest',
      version=version,
      description='A tool to harvest links from slack into youtube playlists',
      long_description=description,
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Other Audience',
          'Programming Language :: Python :: 3'],
      author='K.C.Saff',
      author_email='kc@saff.net',
      url='https://github.com/kcsaff/tuneharvest',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'slacker>=0.9.0',
          'parse>=1.6.6',
          'google-api-python-client>=1.5.0',
      ],
      entry_points={
          'console_scripts': ['tuneharvest = tuneharvest:main']
      },
      include_package_data=False,
)
