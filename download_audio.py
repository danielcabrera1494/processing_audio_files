#
# For licensing see accompanying LICENSE file.
# Copyright (C) 2021 Apple Inc. All Rights Reserved.
#

"""
For each podcast episode:
* Download the raw mp3/m4a file
* Convert it to a 16k mono wav file
# Remove the original file
"""

import os
import pathlib
import subprocess

import numpy as np

import argparse
import pandas as pd

import gdown

parser = argparse.ArgumentParser(description='Download raw audio files for SEP-28k or FluencyBank and convert to 16k hz mono wavs.')
parser.add_argument('--episodes', type=str, required=True,
                   help='Path to the labels csv files (e.g., SEP-28k_episodes.csv)')
parser.add_argument('--wavs', type=str, default="wavs",
                   help='Path where audio files from download_audio.py are saved')


args = parser.parse_args()
episode_uri = args.episodes
wav_dir = args.wavs

# Load the CSV file
data = pd.read_csv(episode_uri, header=None)
# Strip whitespace from all string columns
data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
print(data.head())

# Convert DataFrame to NumPy array if necessary
table = data.values
print(table)

urls = table[:,2]
n_items = len(urls)

audio_types = [".mp3", ".m4a", ".mp4", ".wav"]


for i in range(n_items):
    # Get show/episode IDs
    show_abrev = table[i, -2]
    ep_idx = table[i, -1]
    episode_url = table[i, 2]

    print("Show Abrev: "+show_abrev)
    print("Ep Id: "+str(ep_idx))
    print("Episode URL: "+episode_url)

    # Check file extension
    ext = ''
    for ext in audio_types:
        if ext in episode_url:
            break

    # Ensure the base folder exists for this episode
    episode_dir = pathlib.Path(f"{wav_dir}/{show_abrev}/")
    os.makedirs(episode_dir, exist_ok=True)

    # Get file paths
    audio_path_orig = pathlib.Path(f"{episode_dir}/{ep_idx}{ext}")
    wav_path = pathlib.Path(f"{episode_dir}/{ep_idx}.wav")

    print("Audio Path Origin: "+f"{episode_dir}/{ep_idx}{ext}")
    print("Wav Path: "+f"{episode_dir}/{ep_idx}.wav")

    # Check if this file has already been downloaded
    if os.path.exists(wav_path):
        continue

    print("Processing", show_abrev, ep_idx)
    # Download raw audio file. This could be parallelized.
    if not os.path.exists(audio_path_orig):
      line = f"wget -O {audio_path_orig} {episode_url}"
      print("Executing wget command:", line)
      process = subprocess.Popen([(line)],shell=True)
      process.wait()

    # Temporary output path
    temp_wav_path = wav_path.with_suffix('.temp.wav')
    print(temp_wav_path)

    # Convert to 16khz mono wav file
    line = f"ffmpeg -i {audio_path_orig} -ac 1 -ar 16000 {temp_wav_path}"
    print("Executing FFmpeg command:", line)
    process = subprocess.Popen([(line)],shell=True)
    process.wait()

    # Remove the original mp3/m4a file
    os.remove(audio_path_orig)
    os.replace(temp_wav_path, wav_path)