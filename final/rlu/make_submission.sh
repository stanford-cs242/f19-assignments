#!/bin/bash

pushd program
cargo clean
popd

zip -r -0 final.zip program written/final.pdf
