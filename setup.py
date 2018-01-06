from setuptools import setup

setup(name='capacity',
      version='0.1',
      description='Marcel plays with des',
      author='Marcel Flores',
      license='BSD',
      packages=['capacity'],
      install_requires=[
        "networkx",
        "simpy",
      ],
      entry_points = {
                      'console_scripts': ['capacity=capacity.main:main'],
                     },
      )
