#!/bin/bash

# Script to submit jobs for correcting alignment of all CHiME-5 audio

sessions="S01 S02 S03 S04 S05 S06 S07 S08 S09 S12 S13 S16 S17 S18 S19 S20 S21 S22 S23 S24"

for session in $sessions; do
    export session
    qsub -v session -j y correct_audio.sh
done

source ./paths.sh

# module load apps/python/conda
# source activate chime5


mkdir -p $CHiME6_ROOT/transcriptions/eval  $CHiME6_ROOT/transcriptions/dev $CHiME6_ROOT/transcriptions/train

python correct_transcript_for_clock_drift.py --clock_drift_data chime6_audio_edits.json $CHiME5_ROOT/transcriptions $CHiME6_ROOT/transcriptions
