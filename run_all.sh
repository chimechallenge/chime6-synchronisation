#/bin/bash

# Script to submit jobs for correcting alignment of all CHiME-5 audio

sessions="S01 S02 S03 S04 S05 S06 S07 S08 S09 S12 S13 S16 S17 S18 S19 S20 S21 S22 S23 S24"

for session in $sessions; do
    export session
    qsub -v session correct_audio.sh
done
