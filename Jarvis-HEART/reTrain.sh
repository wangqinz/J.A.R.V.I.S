#! /bin/bash

# Author: QiyangHe
# script used for retrain core ML system (both nlu core and dialogue)

cd data_loading
python loading.py lfc
cd ..
python bot.py train-nlu
python bot.py train-dialogue