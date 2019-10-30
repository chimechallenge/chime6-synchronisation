# CHiME-6 Signal Alignment

## About

Code for processing the CHiME-5 signal to:

- i/ Fix frame dropping misalignment by 0 insertion
- ii/ Compensation for clock drift and start-time mis-estimation using sox

## Dependencies

- Python 3.5+
- Sox v14.4.2 (We confirmed that it produces the different result with v14.4.1. Please make sure to use v14.4.2, which is the latest version)

## Usage

`./run_all.sh`  The op level script which will 

- correct the audio by calling `correct_audio.sh` once for each of the 20 sessions. Currently using `qsub`.
- correct the transcripts called `correct_transcript_for_clock_drift.py`

`correct_audio.sh` processes a single CHiME session in two steps calling
- correct_signals_for_frame_drops.py
- correct_signals_for_clock_drift.py
Should not take more than 30-40 mins per session.

Note, the tools are making the corrections according to data stored in `chime6_audio_edits.json`. These data has been derived using tools operating on the audio from the AVI video files that have not been released. 

## Configuration

- Check paths.sh and set the paths for CHiME5, CHiME6 and sox
- You'll need a python3 environment with modules listed in requirements.txt

## Other

- `audio_md5sums.txt` - md5sums for all the processed audio files, you can check it with the following command:
```bash
. ./paths.sh
cd $CHiME6_ROOT/../
md5sum -c audio_md5sums.txt
```
If your processing is successfully done, you'll finally get the following results:
```
CHiME6/audio/train/S08_U02.CH3.wav: OK
CHiME6/audio/train/S08_U03.CH3.wav: OK
CHiME6/audio/dev/S09_U01.CH3.wav: OK
CHiME6/audio/train/S19_U04.CH1.wav: OK
CHiME6/audio/train/S05_U01.CH1.wav: OK
:
:
```

## Known issues

- S01_U03 - missing because video software failed to record audio. (unrecoverable)
- S01_U02 and SO1_U05 have not synchronised correctly. Should be recoverable but needs more time. e.g. experiments with declipping software or a better approach to the audio matching.
- S05_U04 - missing, video software was stopped and started, so have two avi files. Could probably fix this but it would require another bit of work. It's in the training data so might be easier to just drop it if we are pressed for time.
  



