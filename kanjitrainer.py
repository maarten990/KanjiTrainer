#!/usr/bin/env python3
from flask import Flask, jsonify, request, make_response
from argparse import ArgumentParser
from collections import defaultdict
from proficiency import get_all, predict
from sqlreader import SQLReader
from chunks import ChunkGenerator
import csv
import random
import uuid
import pickle
import sqlite3
import compareKanji as ck


app = Flask(__name__)

with open('kanjitrainer.html', 'r') as f:
    html_page = f.read()

user_chunks = {}
kanji = defaultdict(lambda: [])
radicalMeanings = pickle.load(open("static/radicalMeanings.p", "rb"))

sql = SQLReader('static/kanji.db')

for grade in range(1, 10):
    for row in sql.fetch_iterator('SELECT literal, meanings FROM kanji WHERE grade=?',
                                  repr(grade)):
        kanji[grade].append((row[0], row[1]))

chunkgen = ChunkGenerator(kanji, radicalMeanings, sql)


@app.route('/')
def root():
    # check if the user already exists
    try:
        id = request.cookies.get('id')

        # ducttape fix, this should not be necessary, help
        if id == None or history == None:
            raise Exception()
    except:
        # create a unique id
        id = uuid.uuid1().hex

    resp = make_response(html_page)
    resp.set_cookie('id', id)
    
    return resp


@app.route('/giveHint', methods=['POST'])
def giveHint():
    id = request.cookies.get('id')
    chunk = user_chunks[id]

    current_kanji = request.form['current_kanji']
    kanji_radicals = sql.fetch_one('SELECT radicals FROM kanji WHERE grade=' + repr(chunk.grade) + ' AND literal = ' + repr(current_kanji))
    radical_text = "<ul>" 
    for radical in kanji_radicals[0].strip('\n').split(', '):
        if radical == current_kanji:
            radical_text += "<li>" + radical + ": ?""</li>"
        else:
            radical_text += "<li>" + radical + ": " + radicalMeanings[radical] + "</li>"
    radical_text += "</ul>"
    hint = "Hint:<br>The kanji " + current_kanji + " consist of the following radicals:<br>" + radical_text
    resp = make_response(jsonify(hint_txt=hint))
    return resp


@app.route('/_validate', methods=['POST'])
def validate():
    id = request.cookies.get('id')
    answer = request.form['answer']
    time_taken = request.form['time']

    chunk = user_chunks[id]
    correct = chunk.validate_previous_question(answer, time_taken)

    # if the chunk has ended, do something
    if chunk.done():
        return jsonify(end_of_chunk=True, history=chunk.history)
    else:
        kanji_char, choices = chunk.next_question()

        return jsonify(kanji_char=kanji_char, choices=choices)
    

# TODO: get parameters from somewhere
@app.route('/_initial_data', methods=['POST'])
def initial_data():
    id = request.cookies.get('id')

    # generate a chunk for this user
    chunk = chunkgen.generate(size=4, n_answers=4, kanji_similarity=0.5,
                              answer_similarity=0.5, grade=1)
    user_chunks[id] = chunk
    kanji_char, choices = chunk.next_question()

    return jsonify(kanji_char=kanji_char, choices=choices)


@app.route('/game_over', methods=['GET'])
def game_over():
    id = request.cookies.get('id')
    chunk = user_chunks[id]
    return str(chunk.history)


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
