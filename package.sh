#!/bin/bash

version=$(grep version package.json | cut -d: -f2 | cut -d\" -f2)

rm -f SHA256SUMS
sha256sum *.py LICENSE > SHA256SUMS
rm -rf lib
mkdir lib
pip3 install -r requirements.txt -t lib

rm -rf *.tgz package
mkdir package
cp -r lib LICENSE SHA256SUMS package.json *.py package/
tar czf "tplink-adapter-${version}.tgz" package
