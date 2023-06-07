#!/bin/bash

cd "$(dirname "$0")" || exit 1
git pull
/Users/vandafarsad/.pyenv/versions/link/bin/python main.py
