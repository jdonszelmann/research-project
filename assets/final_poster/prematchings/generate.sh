#!/usr/bin/env bash

python generate.py
cp output.gif ../assets/prematchings.gif
ffmpeg -i ../assets/prematchings.gif -vf "select=eq(n\,0)" -q:v 3 ../assets/prematchings-static.png
