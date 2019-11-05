#!/bin/bash
cd ..

find parser/ -name '*.py' | while read in ; do pipenv run black "${in}"; done
