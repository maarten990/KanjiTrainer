ssh -p2732 kanjitrainer@maarten.sexy 'cd KanjiTrainer; git pull'
ssh -p2732 kanjitrainer@maarten.sexy 'nohup sh -c "( (cd KanjiTrainer; nohup ./run.sh &>/dev/null) & )"'
