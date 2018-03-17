from setuptools import setup

setup(name='pymediaroom',
      version='0.5',
      description='Remote control your Mediaroom Set-up-box',
      url='http://github.com/dgomes/pymediaroom',
      author='Diogo Gomes',
      author_email='diogogomes@gmail.com',
      license='MIT',
      packages=['pymediaroom'],
      install_requires=[
          'xmltodict',
      ],
      download_url= 'https://github.com/dgomes/pymediaroom/tarball/0.5',
      )
