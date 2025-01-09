#!/bin/sh


if [ "$#" -ne 1 ]; then
	echo "Usage: create_animation.sh <python binary>"
	exit
fi
mkdir -p frames
rm frames/*
$1 game.py
ffmpeg -f image2 -framerate 12 -i frames/img-%03d.png game.mp4
