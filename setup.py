from setuptools import setup

setup(name='capacity',
      version='0.1',
      description='Marcel plays with des',
      author='Marcel Flores',
      license='None',
      packages=['capacity'],
      install_requires=[
        "networkx",
        "simpy",
        "matplotlib",
        "feedparser",
        "requests",
      ],
      entry_points = {
                      'console_scripts': ['capacity=capacity.main:main',
                                          'plot=capacity.plot:plot_traveler_time',
                                          'update_gtfs=capacity.gtfs_fetch:update_gtfs'],
                     },
      )
