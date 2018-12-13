#!/usr/bin/env bash

# Convenience script for encoding raw sources in FLAC format. To use, make
# sure bits per sample, number of channels and sample rate all match the
# source files. Set RAW_INFILE to the output file specified in config.json,
# then run the script with the flac filename as parameter: ./make.sh out.flac



set -e


ARTIST=m
SAMPLE_RATE=48000
BPS=16
NUM_CHANNELS=8

PYTHON=python3
RAW_INFILE=/path/to/flac_sources/interleaved.raw

OUTFILE=${1}

${PYTHON} interleave.py

flac -o "${OUTFILE}" -f -T ARTIST="${ARTIST}" --endian=little --channels=${NUM_CHANNELS} \
--sample-rate=${SAMPLE_RATE} -8 --bps=${BPS} --sign=signed --force-raw-format "${RAW_INFILE}"


