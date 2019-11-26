#!/usr/bin/env python3

# Copyright 2019 University of Sheffield (Jon Barker)
# MIT License (https://opensource.org/licenses/MIT)

import argparse
import transcript_utils as tu
import json
import subprocess
import tempfile

def process_device(session, device, linear_fit, inpath, outpath, dataset, filename, sox_path):
    """Process a specific device."""

    speeds = linear_fit['speed']
    padding = linear_fit['padding']
    infile = inpath + '/' + dataset + '/' + filename + '.wav'
    sox_cmd = sox_path + '/sox'
    
    if isinstance(speeds, list):
        # multisegment fit - only needed for S01_U02 and S01_U05
        starts = padding
        ends = padding[1:] + [-1]  # -1 means end of signal
        command_concat = [sox_cmd]
        samples_to_lose = 0

        tmpdir = tempfile.mkdtemp()

        for seg, (start, end, speed) in enumerate(zip(starts, ends, speeds)):
            # print(seg, start, speed, end)
            outfile1 = tmpdir + '/' + filename + '.' + str(seg) + '.wav'
            outfile2 = tmpdir + '/' + filename + '.x' + str(seg) + '.wav'

            command1 = [sox_cmd, '-D', '-R', infile, outfile1]
            if seg == 0:
                # 'start' has a different meaning for first segment
                # Acts like padding does in the simple one-piece case
                if start < 0:
                    start = -start
                    trim = ['trim', str(start) + 's']
                else:
                    trim = ['pad', str(start) + 's', '0s', 'trim', '0s']
            else:
                start += samples_to_lose  # may need to truncate some samples
                trim = ['trim', str(int(start)) + 's']
            command1 += trim
            if end > 0:  # segment of given duration
                duration = end - start
                command1 += [str(duration) + 's']

            if speed < 0:
                # Negative speed means backward in time, 
                # Effectively have to remove some samples
                # This happen in S01_U05.
                samples_to_lose = -duration/speed
            else:
                samples_to_lose = 0
                command2 = [sox_cmd, '-D', '-R', outfile1, outfile2, 'speed', str(speed)]
                subprocess.call(command1)
                subprocess.call(command2)
                command_concat.append(outfile2)
        
        command_concat.append(outpath + '/' + dataset + '/' + filename + '.wav')
        subprocess.call(command_concat)
    else:
        # Original linear fit
        outfile = outpath + '/' + dataset + '/' + filename + '.wav'

        if padding > 0:
            # Change speed and pad
            # The -R to suppress dithering so that command produces identical results each time
            command = [sox_cmd, '-D', '-R', infile, outfile, 'speed', str(speeds), 'pad', str(padding) + 's', '0s']
        else:
            # change speed and trim
            command = [sox_cmd, '-D', '-R', infile, outfile, 'speed', str(speeds), 'trim', str(-padding) + 's']
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
            name = session + '_' + device
            process_device(session, device, linear_fit, inpath, outpath, dataset, name, sox_path)
        elif device[0] == 'U':
            # Processing kinect signal
            for chan in [1, 2, 3, 4]:
                name = session + '_' + device + '.CH' + str(chan)
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

