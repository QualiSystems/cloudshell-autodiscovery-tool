from setuptools import setup
from setuptools import find_packages


def get_file_content(file_name):
    with open(file_name) as f:
        return f.read()

setup(name='cloudshell-autodiscovery',
      version='1.0.1',
      description="",
      long_description=get_file_content('README.md'),
      author='Quali',
      author_email='anton.p@qualisystems.com',
      packages=find_packages() + ['examples', 'data', 'json_schemes'],
      include_package_data=True,
      install_requires=get_file_content('requirements.txt'),
      license="Apache Software License 2.0",
      entry_points={
          "console_scripts": ['autodiscovery=autodiscovery.cli:cli']
      })
