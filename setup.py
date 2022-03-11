from setuptools import setup
from pymediaroom import version

long_description=open("README.rst").read()

setup(name='pymediaroom',
      version=version,
      description='Remote control your Mediaroom Set-up-box',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      url='http://github.com/dgomes/pymediaroom',
      author='Diogo Gomes',
      author_email='diogogomes@gmail.com',
      license='MIT',
      packages=['pymediaroom'],
      install_requires=[
        'async_timeout',
        'xmltodict',
      ],
      python_requires='>=3.5',
      download_url= 'https://github.com/dgomes/pymediaroom/tarball/0.6.4',
      )
