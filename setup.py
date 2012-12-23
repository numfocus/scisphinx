#! /usr/bin/env python

import os
import sys
import subprocess
from configobj import ConfigObj
from distutils.core import setup

VERSION = "0.1"


def update_submodules():
    rtn  = subprocess.call(['git', 'submodule', 'sync'])
    rtn += subprocess.call(['git', 'submodule', 'update'])
    if 0 < rtn:
        print("some submodules failed to sync or update, please check your "
              "internet connection and try again later.")
    subpackages = {}
    totrtn = 0
    conf = ConfigObj('.gitmodules')
    for value in conf.values():
        subpack = value['path']
        has_setup = 'setup.py' in os.listdir(subpack)
        if has_setup:
            print("setup.py found for {0}.".format(subpack))
            cmd = ['python', 'setup.py'] + sys.argv[1:]
            rtn = subprocess.call(cmd, cwd=subpack)
        else:
            print("setup.py not found for {0}, copying wholesale.".format(subpack))
            subpackages[subpack] = (subpack, ['*'])
    return subpackages


def main():
    packages = ["scisphinx",]
    package_dir = {"scisphinx": "scisphinx"}
    package_data = {'scisphinx': ['*.js', '*.css', '*.json']}

    initsadded = []
    subpackages = update_submodules()
    for subpack, (subdir, subdata) in sorted(subpackages.items()):
        for root, dirs, files in os.walk(subpack):
            subname = root.replace(os.path.sep, '.')
            packages.append(subname)
            package_dir[subname] = root
            #package_data[subname] = subdata
            package_data[subname] = files
            if '__init__.py' not in files:
                initfile = os.path.join(root, '__init__.py')
                with open(initfile, 'w'):
                    pass
                initsadded.append(initfile)
            hiddendirs = [d for d in dirs if d.startswith('.')]
            for d in hiddendirs:
                dirs.remove(d)

    setupkw = dict(
        name="scisphinx",
        packages=packages,
        package_dir=package_dir,
        package_data=package_data,
        version=VERSION,
        description="Sphinx extensions common to the scientific computing ecosystem.",
        # classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers=["Development Status :: 3 - Alpha",
                     "Environment :: Plugins",
                     "License :: OSI Approved :: BSD License",
                     "Topic :: Documentation"],
        keywords="sphinx numpy ipython scipy nbconvert breath C++",
        author="Anthony Scopatz, et al.",
        author_email="scopatz@gmail.com",
        url="http://github.com/numfocus/scisphinx",
        license="BSD",
        requires=["sphinx (>= 1.0.1)"],
        )

    try:
        setup(**setupkw)
    finally:
        for f in initsadded:
            os.remove(f)


if __name__ == '__main__':
    main()
