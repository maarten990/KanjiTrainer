#!/usr/bin/env python3
from flask import Flask, jsonify, request, make_response
from argparse import ArgumentParser
from collections import defaultdict
from proficiency import get_all, predict
import csv
import random
import uuid
import pickle
import sqlite3
import compareKanji as ck

user_grade = 1

app = Flask(__name__)
prev_char = "" #the previously shown character
prev_correct = "" #the previously correct meaning
with open('kanjitrainer.html', 'r') as f:
    html_page = f.read()

pending_answers = {}
kanji = defaultdict(lambda: [])

with open('static/kanjidic.pickle', 'rb') as f:
    conn = sqlite3.connect('static/kanji.db')
    c = conn.cursor()

    for grade in range(1, 11):
        for row in c.execute('SELECT literal, meanings FROM kanji WHERE grade=?',
                             repr(user_grade)):
            kanji[grade].append((row[0], row[1].split(', ')))

    conn.close()

def get_kanji(grade=user_grade):
    char, meaning = random.choice(kanji[grade])

    return char, meaning


def random_choice_list(n=4, difficulty="hard"):
    global prev_char

    #draw a character not equal to the last one
    char, meanings = get_kanji()
    meaning = ', '.join(meanings)
    while char==prev_char:
        char, meanings = get_kanji()
        meaning = ', '.join(meanings)
    
    otherOptions = ck.giveChoicesKanji(char, difficulty, n-1)
    SQLotherOptions = str(otherOptions).replace("[","(").replace("]",")")
    conn = sqlite3.connect('static/kanji.db')
    c = conn.cursor()
    c.execute('SELECT meanings FROM kanji WHERE grade=? AND literal IN ' +  SQLotherOptions, repr(user_grade))
    otherMeanings = c.fetchall()
    conn.close()
    choices = [otherMeanings[x][0] for x in range(0, len(otherMeanings))] + [meaning] 
    random.shuffle(choices)
    correct = choices.index(meaning)
    correct_meaning = meaning
    print(choices)

    return char, choices, correct, correct_meaning


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

    resp = make_response(html_page)
    resp.set_cookie('id', id)
    resp.set_cookie('history', '1') #FIXME: initialize empty history

    return resp



@app.route('/_validate', methods=['POST'])
def validate():
    global prev_char
    global prev_correct

    id = request.cookies.get('id')
    history = [int(x) for x in request.cookies.get('history').split(' ')]
    correct = pending_answers[id]
    answer = request.form['answer']
    
    # the answer is either the full string from the button, or one of the words
    # in the comma-separated list
    meaning_list = [meaning.strip() for meaning in correct.split(',')]
    if answer == correct or answer.strip() in meaning_list:
        img = 'static/dog.jpg'
        history.append(1)

        if random.random() <= 0.01:
            img = 'static/streak.jpg'
    else:
        img = 'static/suzanne.png'
        history.append(0)

    char, choices, correct, correct_meaning = random_choice_list()
    pending_answers[id] = choices[correct]

    score, total, perc, ewma, streak, top_streak = get_all(history)
    prediction = predict(history)

    time = request.form['time']
    
    resp = make_response(jsonify(kanji_char=char, choices=choices,
                                 happy_img=img, score=score, total=total, perc=perc, 
                                 ewma=ewma, streak=streak, top_streak=top_streak, 
                                 predict=prediction, correct=correct, time=time, 
                                 kanji_prev_char=prev_char, prev_correct_value=prev_correct))
    history_string = ''
    for ans in history: 
        history_string += str(ans) + " "
    
    prev_char = char
    prev_correct = correct_meaning
    
    resp.set_cookie('history', history_string.strip())
    return resp


# TODO: remove code duplication between this and the validate function
@app.route('/_initial_data', methods=['POST'])
def initial_data():
    global prev_char
    global prev_correct
    
    id = request.cookies.get('id')
    history = [int(x) for x in request.cookies.get('history').split(' ')]
    char, choices, correct, correct_meaning = random_choice_list()
    pending_answers[id] = choices[correct]
    img = 'static/dideriku.png'
    prediction = predict(history)

    resp = make_response(jsonify(kanji_char=char, choices=choices,
                                 happy_img=img, score=0, total=0, perc=0, 
                                 ewma=0, streak=0, top_streak=0, 
                                 predict=prediction, correct=correct))

    prev_char = char
    prev_correct = correct_meaning
                                 
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
