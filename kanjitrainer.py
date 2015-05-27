from flask import Flask, jsonify, request, make_response
from jinja2 import Template, Environment, PackageLoader
from argparse import ArgumentParser
import csv
import random
import uuid

app = Flask(__name__)
env = Environment(loader=PackageLoader('kanjitrainer', '.'))
html_template = env.get_template('kanjitrainer.html')
kanji = []

pending_answers = {}

with open('static/kanji.csv', 'r') as f:
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        id, char, _, meaning = row
        kanji.append((id, char, meaning))


def get_kanji():
    return random.choice(kanji)


def random_choice_list(n=3):
    _, char, meaning = get_kanji()
    choices = [random.choice(kanji)[2] for _ in range(n-1)] + [meaning]
	#if the list contains duplicates, redraw
    while len(set(choices))!= len(choices):
        choices = [random.choice(kanji)[2] for _ in range(n-1)] + [meaning]
    random.shuffle(choices)
    correct = choices.index(meaning)

    return char, choices, correct


@app.route('/')
def root():
    # check if the user already exists
    try:
        id = request.cookies.get('id')
        score, total = request.cookies.get('correct_total')
    except:
        # create a unique id
        id = uuid.uuid1().hex
        score, total = 0, 0

    char, choices, correct = random_choice_list()
    img = 'static/dog.jpg'

    pending_answers[id] = correct

    resp = make_response(html_template.render(kanji_char=char, choices=choices,
                                              happy_img=img))
    resp.set_cookie('id', id)
    resp.set_cookie('correct_total', '0,0')

    return resp



@app.route('/_validate', methods=['POST'])
def validate():
    id = request.cookies.get('id')
    score, total = [int(x) for x in
                    request.cookies.get('correct_total').split(',')]
    correct = pending_answers[id]
    answer = int(request.form['answer'])

    total += 1
    if answer == correct:
        img = 'static/dog.jpg'
        score += 1
    else:
        img = 'static/wrong.jpg'

    char, choices, correct = random_choice_list()
    pending_answers[id] = correct

    resp = make_response(jsonify(kanji_char=char, choices=choices, correct_value=correct,
                                 happy_img=img, score=score, total=total))
    resp.set_cookie('correct_total', '{},{}'.format(score, total))

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
