from flask import Flask, jsonify, request
from jinja2 import Template, Environment, PackageLoader
from argparse import ArgumentParser
import csv
import random

app = Flask(__name__)
env = Environment(loader=PackageLoader('kanjitrainer', '.'))
html_template = env.get_template('kanjitrainer.html')
kanji = []

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
    random.shuffle(choices)
    correct = choices.index(meaning)

    return char, choices, correct


@app.route('/')
def hello():
    char, choices, correct = random_choice_list()
    img = 'static/dog.jpg'

    return html_template.render(kanji_char=char, choices=choices,
                                correct_value=correct, happy_img=img)


@app.route('/_validate', methods=['POST'])
def wrong():
    char, choices, correct = random_choice_list()
    img = ('static/dog.jpg' if int(request.form['correct']) != 0
           else 'static/wrong.jpg')

    return jsonify(kanji_char=char, choices=choices, correct_value=correct,
                   happy_img=img)


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
