import os
import sys
from codecs import open
import setuptools

here = os.path.abspath(os.path.dirname(__file__))

os.chdir(here)

version_contents = {}
with open(os.path.join(here, "gridmarkets", "version.py"), encoding="utf-8") as f:
    exec(f.read(), version_contents)

setuptools.setup(
    name="gridmarkets-envoy-client",
    version=version_contents["VERSION"],
    author="GridMarkets",
    author_email="support@gridmarkets.com",
    description="Python client for GridMarkets API",
    packages=["gridmarkets"],
    install_requires=["future", "requests"]
)
