#!/bin/bash
cd ..

mkdir -p examples
echo "Creating examples into /examples/"

pipenv run python parser/cli.py -n 7 --per day --nlargest 3 --minduration 120 --level 0 > examples/L0.txt
echo "Saved"

pipenv run python parser/cli.py -n 7 --per day --nlargest 3 --minduration 120 --level 1 > examples/L1.txt
echo "Saved"

pipenv run python parser/cli.py -n 7 --per day --nlargest 3 --minduration 120 --level 2 > examples/L2.txt
echo "Saved"

pipenv run python parser/cli.py -n 7 --per day --nlargest 3 --minduration 120 --level 3 > examples/L3.txt
echo "Saved"

pipenv run python parser/cli.py -n 7 --per day --nlargest 3 --minduration 120 --level 4 > examples/L4.txt
echo "Saved"

pipenv run python parser/cli.py -n 7 --per day --nlargest 3 --minduration 120 --level 5 > examples/L5.txt
echo "Saved"

pipenv run python parser/cli.py -n 7 --per day --nlargest 3 --minduration 120 --level 6 > examples/L6.txt
echo "Saved"

pipenv run python parser/cli.py -n 1 --per day --nlargest 3 --minduration 60 --level 7 > examples/L7.txt
echo "Saved"

echo "Done"