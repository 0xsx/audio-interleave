#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interleaves source sound files to produce raw audio ready for encoding.
"""

from __future__ import division, absolute_import, print_function


import argparse
import json
import numpy as np
import os
import soundfile
import struct



def read_config_file(config_filename):
  """Reads configuration parameters from the specified JSON file."""

  # Strip comments while keeping line numbers.
  config_str = ""
  with open(config_filename, "r") as f_in:
    for line in f_in:
      line = line.rstrip()
      comment_pos = line.find("//")
      if comment_pos > -1:
        line = line[:comment_pos]
      config_str += line + "\n"

  config = json.loads(config_str)

  return config






def load_source_data(base_dir, extension, sources):

  source_data = {}
  source_rate = None
  data_len = None

  for ch_name in sources:
    f_name = os.path.realpath(os.path.join(base_dir, "%s.%s" % (sources[ch_name], extension)))
    data, sr = soundfile.read(f_name, dtype="int16")

    if source_rate is not None and sr != source_rate:
      raise ValueError("Sample rate %d does not match expected %d." % (sr, source_rate))
    source_rate = sr

    if len(data.shape) > 1:
      raise ValueError("Expected single channel audio, got %d channels." % len(data.shape))

    source_data[ch_name] = data
    if data_len is None:
      data_len = len(data)
    elif len(data) > data_len:
      data_len = len(data)


  for ch_name in source_data:
    padded_data = np.zeros((data_len,), dtype="int16")
    padded_data[:len(source_data[ch_name])] = source_data[ch_name]
    source_data[ch_name] = padded_data


  return source_data, source_rate




  


def interleave_sources_8(source_data):

  channel_names = ["fl", "fr", "c", "lfe", "bl", "br", "sl", "sr"]

  if source_data.keys() - set(channel_names):
    raise ValueError("Invalid channel names for 8-channel sources.")

  num_samples = len(source_data["fl"])

  interleaved_data = np.zeros((num_samples, 8), dtype="int16")

  for i in range(8):
    ch_name = channel_names[i]
    interleaved_data[:, i] = source_data[ch_name]

  interleaved_data = interleaved_data.tobytes()

  return interleaved_data







def main(config_filename):
  """Entry point method."""

  config = read_config_file(config_filename)

  # TODO validate config structure

  source_data, source_rate = load_source_data(config["source_dir"],
                                              config["source_ext"],
                                              config["sources"])


  if len(source_data) == 8:

    raw_data = interleave_sources_8(source_data)

  else:
    raise ValueError("Invalid number of channels specified: %d." % len(source_data))



  f_name = os.path.realpath(os.path.join(config["source_dir"], config["output_file"]))
  
  with open(f_name, "wb") as f_out:
    f_out.write(raw_data)








if __name__ == "__main__":

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--config", default="config.json", type=str, metavar="f",
                      help="Configuration json file (default: config.json)")

  args = parser.parse_args()

  main(os.path.realpath(args.config))






