#! /usr/bin/env python

import os
import sys
import subprocess
from configobj import ConfigObj
from distutils.core import setup

VERSION = "0.1"


def update_submodule(subpack):
    needs_init = 0 == len(os.listdir(subpack))
    cmd = ['git', 'submodule', 'update', ]
    if needs_init: 
        cmd += ['--init', '--']
    cmd += [subpack]
    print " ".join(cmd)
    rtn = subprocess.call(cmd)
    return rtn


def update_submodules():
    rtn = subprocess.call(['git', 'submodule', 'sync', ])
    rtn = subprocess.call(['git', 'submodule', 'update', ])
    subpackages = {}
    totrtn = 0
    conf = ConfigObj('.gitmodules')
    for value in conf.values():
        subpack = value['path']
        #rtn = update_submodule(subpack)
        totrtn += rtn
        if rtn != 0:
            print("failed to update {0}, skipping.".format(subpack))
            continue
        has_setup = 'setup.py' in os.listdir(subpack)
        if has_setup:
            print("setup.py found for {0}.".format(subpack))
            cmd = ['python', 'setup.py'] + sys.argv[1:]
            rtn = subprocess.call(cmd, cwd=subpack)
        else:
            print("setup.py not found for {0}, copying wholesale.".format(subpack))
            subpackages[subpack] = (subpack, ['*'])
    if 0 < totrtn:
        print("some submodules failed to update or install, please check your "
              "internet connection and try again later.")
    return subpackages


def main():
    packages = ["scisphinx",]
    package_dir = {"scisphinx": "scisphinx"},
    package_data = {'scisphinx': ['*.js', '*.css', '*.json']},

    subpackages = update_submodules()
    for subpack, (subdir, subdata) in sorted(subpackages.items()):
        packages.append(subpack)
        package_dir[subpack] = subdir
        package_data[subpack] = subdata

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
        keywords="sphinx numpy ipython scipy breath C++",
        author="Anthony Scopatz, et al.",
        author_email="scopatz@gmail.com",
        url="http://github.com/numfocus/scisphinx",
        license="BSD",
        requires=["sphinx (>= 1.0.1)"],
        )

    setup(**setupkw)

if __name__ == '__main__':
    main()
