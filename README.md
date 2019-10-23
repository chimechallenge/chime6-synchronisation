# CHiME-6 Signal Alignment

## About

Code for processing the CHiME-5 signal to:

- i/ Fix frame dropping misalignment by 0 insertion
- ii/ Compensation for clock drift and start-time mis-estimation using sox

## Dependencies

- Python 3.6 
- Sox. (I used v14.4.2. No new versions since 2015 so should not be a problem)

## Usage

`./run_all.sh`  The op level script which will 

- correct the audio by calling `correct_audio.sh` once for each of the 20 sessions. Currently using qsub.
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

- `audio_md5sums.txt` - md5sums for all the processed audio files

## Known issues

- S01_U03 - missing because video software failed to record audio. (unrecoverable)
- S01_U02 and SO1_U05 have not synchronised correctly. Should be recoverable but needs more time. e.g. experiments with declipping software or a better approach to the audio matching.
- S05_U04 - missing, video software was stopped and started, so have two avi files. Could probably fix this but it would require another bit of work. It's in the training data so might be easier to just drop it if we are pressed for time.
  



