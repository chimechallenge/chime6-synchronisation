!#/bin/bash

### 

source paths.sh  # Paths for CHiME5 and CHiME6

## Lines below load anaconda python on Sheffield HPC
## and activate a conda environment supplying the
## requirements in requirement.txt
#
# module load apps/python/anaconda3-2.5.0
# source env3/bin/activate 

###

echo $session  # session variable passed in via qsub

###

IN_PATH = $CHiME5_ROOT/audio    
OUT_PATH = $CHiME6_ROOT/audio
TMP_PATH = $CHiME6_ROOT/audio_tmp

mkdir -p $OUT_PATH/train $OUT_PATH/eval $OUT_PATH/dev
mkdir -p $TMP_PATH/train $TMP_PATH/eval $TMP_PATH/dev

# Correct for frame dropping
python correct_signals_for_frame_drops.py --session=$session chime6_audio_edits.json $IN_PATH $TMP_PATH

# Sox processing for correcting clock drift
python correct_signals_for_clock_drift.py --session=$session  --sox_path $SOX_PATH chime6_audio_edits.json $TMP_PATH $OUT_PATH