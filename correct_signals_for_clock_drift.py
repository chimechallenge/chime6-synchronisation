#!/usr/bin/env python3

# Copyright 2019 University of Sheffield (Jon Barker)
# MIT License (https://opensource.org/licenses/MIT)

import argparse
import transcript_utils as tu
import json
import subprocess

def process_device(session, device, linear_fit, inpath, outpath, dataset, filename, sox_path):
    """Process a specific device."""

    padding = linear_fit['padding']
    speed = linear_fit['speed']
    infile = f'{inpath}/{dataset}/{filename}.wav'
    outfile = f'{outpath}/{dataset}/{filename}.wav'
    sox_cmd = f'{sox_path}/sox'

    if padding > 0:
        # Change speed and pad
        # The -R to suppress dithering so that command produces identical results each time
        command = [sox_cmd, '-D', '-R', infile, outfile, 'speed', f'{speed}','pad', f'{padding}s','0s']
    else:
        # change speed and trim
        command = [sox_cmd, '-D', '-R', infile, outfile, 'speed', f'{speed}','trim', f'{-padding}s']
        # Note, the order of speed vs trim/pad makes a difference
        # I believe sox actually applies the speed transform after the padding.
        # but speed is so close to 1 and the padding so short that it will
        # come out about the same either way around.

    print(command)
    subprocess.call(command)


def process_all_devices(session, linear_fit_data, inpath, outpath, sox_path):
    """Process all devices."""

    chime_data = tu.chime_data()
    dataset = chime_data[session]['dataset']
    devices = chime_data[session]['pids'] + chime_data[session]['kinects']

    session_fits = linear_fit_data[session]

    # Note, skipping the first pid from list of devices as this is the reference device to which all others are being aligned.
    # (Or could insert pad 0 and scale 1 into json so that it is still processed through sox??)
    for device in devices:
        if device not in session_fits:
            print(f'WARNING: device {device} missing for session {session}')
            continue

        linear_fit = session_fits[device]
        
        if device[0] == 'P':
            # Processing binaural mic signal
            name = f"{session}_{device}"
            process_device(session, device, linear_fit, inpath, outpath, dataset, name, sox_path)
        elif device[0] == 'U':
            # Processing kinect signal
            for chan in [1, 2, 3, 4]:
                name = f"{session}_{device}.CH{chan}"
                process_device(session, device, linear_fit, inpath, outpath, dataset, name, sox_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", help="list of sessions to process (defaults to all)")   
    parser.add_argument("--sox_path", help="path for sox command (defaults to .)")  
    parser.add_argument("clock_drift_data", help="json file storing clock drift data") 
    parser.add_argument("inpath", help="path to input audio")  
    parser.add_argument("outpath", help="path to output audio")   
 
    args = parser.parse_args()

    if args.sox_path is None:
        sox_path = "."
    else:
        sox_path = args.sox_path

    if args.sessions is None:
        sessions = tu.chime_data()
    else:
        sessions = args.sessions.split()

    with open(args.clock_drift_data) as f:
        linear_fit_data = json.load(f)

    for session in sessions:
        process_all_devices(session, linear_fit_data, args.inpath, args.outpath, sox_path)


if __name__ == '__main__':
    main()


# python correct_signals_for_clock_drift.py --session=S04 --sox_path /usr/local/bin linear_fit.json CHiME5/audio CHiME5/audio_proc 