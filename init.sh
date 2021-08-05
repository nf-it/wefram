#!/bin/bash

yarn set version berry
python3 -m venv .venv
source .venv/bin/activate
pip3 install --upgrade pip
pip3 install wheel
python3 manage first-install-prepare
python3 manage build
python3 manage rebuild-db
