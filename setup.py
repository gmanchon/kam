
from setuptools import setup, find_packages

import os

with open("requirements.txt") as f:
    content = f.readlines()
requirements = [x.strip() for x in content]

setup(name="kam",
      version="0.1",
      description="kam",
      packages=find_packages(),
      install_requires=requirements,
      scripts=[os.path.join("scripts", "kam")])
