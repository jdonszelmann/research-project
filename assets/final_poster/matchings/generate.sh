#!/usr/bin/env bash

python generate.py
cp output.gif ../assets/matchings.gif
ffmpeg -i ../assets/matchings.gif -vf "select=eq(n\,0)" -q:v 3 ../assets/matchings-one.png
ffmpeg -i ../assets/matchings.gif -vf "select=eq(n\,0)" -q:v 3 ../assets/matchings-static.png
ffmpeg -i ../assets/matchings.gif -vf "select=eq(n\,3)" -q:v 3 ../assets/matchings-two.png