#!/usr/bin/env python3
from flask import Flask, jsonify, request, make_response
from jinja2 import Template, Environment, PackageLoader
from argparse import ArgumentParser
from proficiency import get_all, predict
import csv
import random
import uuid
import pickle


app = Flask(__name__)
env = Environment(loader=PackageLoader('kanjitrainer', '.'))
html_template = env.get_template('kanjitrainer.html')

pending_answers = {}

with open('static/kanjidic.pickle', 'rb') as f:
    kanji = pickle.load(f)

def get_kanji():
    k = random.choice(kanji)
    char = k.literal
    meaning = ', '.join(k.meanings)

    return char, meaning


def random_choice_list(n=3):
    char, meaning = get_kanji()
    choices = [', '.join(random.choice(kanji).meanings) for _ in range(n-1)] + [meaning]
    #if the list contains duplicates, redraw
    while len(set(choices))!= len(choices):
        choices = [', '.join(random.choice(kanji).meanings) for _ in range(n-1)] + [meaning]

    random.shuffle(choices)
    correct = choices.index(meaning)

    return char, choices, correct


@app.route('/')
def root():
    # check if the user already exists
    try:
        id = request.cookies.get('id')
        history = request.cookies.get('history')

        # ducttape fix, this should not be necessary, help
        if id == None or history == None:
            raise Exception()
    except:
        # create a unique id
        id = uuid.uuid1().hex
        history = []

    char, choices, correct = random_choice_list()
    img = 'static/dideriku.png'

    pending_answers[id] = correct

    resp = make_response(html_template.render(kanji_char=char, choices=choices,
                                              happy_img=img))
    resp.set_cookie('id', id)
    resp.set_cookie('history', '1') #FIXME: initialize empty history

    return resp



@app.route('/_validate', methods=['POST'])
def validate():
    id = request.cookies.get('id')
    history = [int(x) for x in request.cookies.get('history').split(' ')]
    correct = pending_answers[id]
    answer = int(request.form['answer'])
    
    if answer == correct:
        img = 'static/dog.jpg'
        history.append(1)
    else:
        img = 'static/wrong.jpg'
        history.append(0)

    char, choices, correct = random_choice_list()
    pending_answers[id] = correct

    score, total, perc, ewma, streak, top_streak = get_all(history)
    prediction = predict(history)
    resp = make_response(jsonify(kanji_char=char, choices=choices, correct_value=correct,
                                 happy_img=img, score=score, total=total, perc=perc, 
                                 ewma=ewma, streak=streak, top_streak=top_streak, predict = prediction))
    history_string = ''
    for ans in history: 
        history_string += str(ans) + " "
    
    resp.set_cookie('history', history_string.strip())
    return resp



def main():
    parser = ArgumentParser(description='A web-based interactive Kanji trainer.')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='run locally in debug mode')
    args = parser.parse_args()

    if args.debug:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()
