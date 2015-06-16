#!/usr/bin/env python3
from flask import Flask, jsonify, request, make_response, g, redirect, url_for
from argparse import ArgumentParser
from collections import defaultdict
from proficiency import get_all, predict
from sqlreader import db_path, db_commit
from chunks import ChunkGenerator, Parameters
from parameter_sampling import sample_parameters
import os.path
import csv
import random
import uuid
import pickle
import sqlite3
import compareKanji as ck


app = Flask(__name__)

with open('kanjitrainer.html', 'r') as f:
    html_page = f.read()
with open('feedback.html', 'r') as f:
    feedback_page = f.read()
with open('welcome.html', 'r') as f:
    welcome_page = f.read()

user_level = {} 
user_chunks = {}
user_parameters = {}
kanji = defaultdict(lambda: [])
radicalMeanings = pickle.load(open("static/radicalMeanings.p", "rb"))

db = sqlite3.connect(db_path)
cursor = db.cursor()
for grade in range(1, 10):
    for row in cursor.execute('SELECT literal, meanings, stroke_count FROM kanji WHERE grade=?',
                              repr(grade)):
        kanji[grade].append((row[0], row[1], row[2]))
db.close()

chunkgen = ChunkGenerator(kanji, radicalMeanings)
db.close()


@app.route('/questions', methods=['POST', 'GET'])
def questions():
    # check if the user already exists
    try:
        id = request.cookies.get('id')

        # ducttape fix, this should not be necessary, help
        if id == None:
            raise Exception()
    except:
        # create a unique id
        id = uuid.uuid1().hex

    # set user_level 
    if request.method == 'POST': 
        user_level[id] = int(request.form.get('level'))
        
    # randomly sample the parameters unless the debug option is given
    if request.args.get('debug'):
        params = Parameters(**{p: request.args.get(p) for p in Parameters.params()
                               if request.args.get(p) != None})
    else:
        params = sample_parameters(user_level[id])
        print(params)
        
    user_parameters[id] = params

    resp = make_response(html_page)
    resp.set_cookie('id', id)
    
    return resp


@app.route('/giveHint', methods=['POST'])
def giveHint():
    id = request.cookies.get('id')
    chunk = user_chunks[id]
    hint = chunk.get_hint()
    return jsonify(hint=hint)


@app.route('/_validate', methods=['POST'])
def validate():
    id = request.cookies.get('id')
    answer = request.form['answer']
    time_taken = request.form['time']
    hint_requested = request.form['hint']

    chunk = user_chunks[id]
    correct = chunk.validate_previous_question(answer, time_taken, hint_requested)

    # if the chunk has ended, do something
    if chunk.done():
        return jsonify(end_of_chunk=True, history=chunk.history)
    else:
        question, item, choices = chunk.next_question()

        return jsonify(question=question, item=item, choices=choices)

@app.route('/javascript_validate', methods=['POST'])
def javascript_validate():
    id = request.cookies.get('id')
    chunk = user_chunks[id]
    _, _, answer, options, _ = chunk.questions[chunk.next_question_idx - 1]
    correct_id = options.index(answer)
    return jsonify(correct_id=correct_id)  

@app.route('/_initial_data', methods=['POST'])
def initial_data():
    id = request.cookies.get('id')

    # generate a chunk for this user
    # resample the parameters if no chunk can be generated
    params = user_parameters[id]
    chunk = None
    while not chunk:
        try:
            chunk = chunkgen.generate(params)
        except Exception as e:
            print("---Error----:", str(e))
            params = sample_parameters(user_level[id])
            user_parameters[id] = params

    user_chunks[id] = chunk
    question, item, choices = chunk.next_question()

    return jsonify(question=question, item=item, choices=choices)

@app.route('/', methods=['GET'])
def root():
    return welcome_page

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'GET':
        return feedback_page
    else:
        id = request.cookies.get('id')
        chunk = user_chunks[id]
        chunk.score = request.form.get('score')

        # save data
        hist = repr(chunk.history)
        score = chunk.score
        params = repr(chunk.parameters)
        query = 'INSERT INTO training_data VALUES(?, ?, ?)'

        db_commit(query, [hist, params, score])

        return redirect(url_for('questions'))


def main():
    parser = ArgumentParser(description='A web-based interactive Kanji trainer.')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='run locally in debug mode')
    args = parser.parse_args()

    if args.debug:
        app.run(debug=True, extra_files=['kanjitrainer.html',
                                         'feedback.html',
                                         'welcome.html',
                                         'static/kanjitrainer.css',
                                         'static/kanjitrainer.js'])
    else:
        app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()
