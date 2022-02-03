#!/bin/bash

rm -rf build
rm -rf dist

python3 setup.py bdist_wheel sdist
twine upload dist/*

rm -rf build
rm -rf dist
