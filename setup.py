import os
from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession

version = '0.9.0'

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()

install_reqs = parse_requirements('requirements.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(name='tuneharvest',
      version=version,
      description='A tool to harvest links from slack into youtube playlists',
      long_description=read('README.md'),
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Other Audience',
          'Programming Language :: Python :: 3'],
      author='K.C.Saff',
      author_email='kc@saff.net',
      url='https://github.com/kcsaff/tuneharvest',
      license='MIT',
      packages=find_packages(),
      install_requires=reqs,
      entry_points={
          'console_scripts': ['tuneharvest = tuneharvest:main']
      },
      include_package_data=False,
)
