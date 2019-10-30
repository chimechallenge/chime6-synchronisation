#!/usr/bin/env python3

# Copyright 2019 University of Sheffield (Jon Barker)
# MIT License (https://opensource.org/licenses/MIT)

"""
correct_signals_for_frame_drops.py

Inserts 0s into the CHiME-5 audio signals to correct the mis-alignment caused
when audio frames were dropped by the Kinect API
"""

import argparse
import json
import os  # Needed for symlink creation
import wave

import numpy as np

import transcript_utils as tu

def apply_edits(x, edits):
    """ Apply the list of edits to the signal x
         and returns a modified signal, x_new.
    """

    # Pre-allocate space for editted signal
    max_space = edits[-1][2] + edits[-1][1] - edits[-1][0]
    # x_new = np.zeros_like(x, shape=max_space)
    x_new = np.zeros(shape=max_space, dtype=type(x[0]))
    length_x = len(x)

    for edit in edits:
        in_from = edit[0]
        in_to = min(edit[1], length_x)
        out_from = edit[2]
        out_to = out_from + in_to - in_from
        if in_from > length_x:
            break
        x_new[out_from-1: out_to] = x[in_from-1: in_to]

    # Trim off excess
    x_new = x_new[0:out_to]
    return x_new


def read_wav(filename):
    """Read a 16-bit wav file as an numpy array of shorts"""
    wave_read = wave.open(filename, 'r')
    n_samples = wave_read.getnframes()
    byte_data = wave_read.readframes(n_samples)
    x = np.frombuffer(byte_data, dtype=np.short)
    return x


def write_wav(x, filename):
    """Write array of shorts to a 16-bit wav file."""
    wave_write = wave.open(filename, 'w')
    wave_write.setnchannels(1)
    wave_write.setsampwidth(2)
    wave_write.setframerate(16000)
    wave_write.writeframes(x)


def fix_audio_files(in_wav_fn, out_wav_fn, frame_drops):
    """Apply frame drop correction edits to wav file."""
    x = read_wav(in_wav_fn)
    x_fixed = apply_edits(x, frame_drops)
    write_wav(x_fixed, out_wav_fn)


def correct_all_devices(session, frame_drop_data, inpath, outpath):
    """Apply framedrop correction to all devices in a given session."""

    chime_data = tu.chime_data()

    dataset = chime_data[session]['dataset'] # eval, dev or train

    # Frame drop correction only applied to the kinect signals
    devices = chime_data[session]['kinects']

    session_frame_drops= frame_drop_data[session]

    for device in devices:
        if device not in session_frame_drops:
            print("WARNING: device " + device + " missing for session " + session)
            continue

        frame_drops = session_frame_drops[device]['edits']
        
        # Processing all 4 kinect channels for this device
        for chan in [1, 2, 3, 4]:
            name = session + "_" + device + ".CH" + str(chan)
            in_wav_fn = inpath + "/" + dataset + "/" + session + "_" + device + ".CH" + str(chan) + ".wav"
            out_wav_fn = outpath + "/" + dataset + "/" + session + "_" + device + ".CH" + str(chan) + ".wav"
            fix_audio_files(in_wav_fn, out_wav_fn, frame_drops)

    # For binaural mics add symbolic links so that complete set of signals
    # is available in output dir
    for device in chime_data[session]['pids']:
        in_wav_fn = inpath + "/" + dataset + "/" + session + "_" + device + ".wav"
        out_wav_fn = outpath + "/" + dataset + "/" + session + "_" + device + ".wav"
        os.symlink(os.path.realpath(in_wav_fn), os.path.realpath(out_wav_fn))


def main():
    """main."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", help="list of sessions to process (defaults to all)")   
    parser.add_argument('frame_drop_data',
                        help="A JSON file containing the edit description")
    parser.add_argument("inpath", help="path to input audio")  
    parser.add_argument("outpath", help="path to output audio")   

    args = parser.parse_args()

    if args.sessions is None:
        sessions = tu.chime_data()
    else:
        sessions = args.sessions.split()

    with open(args.frame_drop_data) as f:
        frame_drop_data = json.load(f)

    for session in sessions:
        correct_all_devices(session, frame_drop_data, args.inpath, args.outpath)



if __name__ == '__main__':
    main()


# e.g.,
# python correct_signals_for_frame_drops.py frame_drops.json CHiME5/audio CHiME5_proc/audio 
