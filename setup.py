#!/usr/bin/python3
#-*- coding: utf-8 -*-
"""
Created on Tue Feb 05 16:16:55 2019 

@author: baneel

Description: setup for DeikeLabe experimental and numerics toolkit package.
"""

from setuptools import setup, find_packages
import versioneer

setup(name='cobubbles',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Surface collective bubbles simulation',
      url='https://github.com/DeikeLab/collective-bubbles',
      author='baneel',
      author_email='neel.b@princeton.edu',
      license='GNU-GPL3',
      packages=find_packages(),
      )
