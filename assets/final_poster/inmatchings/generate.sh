#!/usr/bin/env bash

python generate.py
cp output.gif ../assets/inmatchings.gif
ffmpeg -i ../assets/inmatchings.gif -vf "select=eq(n\,0)" -q:v 3 ../assets/inmatchings-static.png
