from setuptools import setup, find_packages

README = 'Rezilion agentless'

requires = []
tests_require = [
    'pytest==6.2.5',
    'coverage==6.3'
]


def packages(namespace, dir):
    packages = find_packages(dir)
    return [f'{namespace}.{package}' for package in packages]


setup(name='rezilion-agentless',
      version='2.0.0',
      description=README,
      long_description=README,
      package_dir={'': 'source'},
      classifiers=[
          "Programming Language :: Python",
      ],
      author='Rezilion',
      packages=packages('rezilion', 'source/rezilion'),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
      },
      install_requires=requires,
      namespace_packages=['rezilion']
      )
