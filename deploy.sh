FILES='kanjitrainer.html kanjitrainer.py requirements.txt static'

rsync -rv --rsh='ssh -p2732' $FILES kanjitrainer@maarten.sexy:~/
