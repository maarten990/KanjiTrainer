#!/usr/bin/env python3
import os
import pickle
import sqlite3
db = sqlite3.connect('static/kanji.db')
cursor = db.cursor()
cursor.execute('SELECT literal, grade FROM kanji')
kanji = cursor.fetchall()
db.close()
vocab = []
for file in os.listdir("KIC"):
    if file.endswith(".txt"):
        with open("KIC/" + file, 'r') as f:
            line_count = 0
            for line in f:
                line_count += 1
                if line[0] != "#" and line_count > 4:
                    vocab_kanji = line[:line.find(" ")]
                    vocab_reading = line[line.find("[")+1:line.find("]")]
                    vocab_meaning = line[line.find("/")+1:line.find("/\n")]
                    vocab.append((vocab_kanji,vocab_reading,vocab_meaning))

def highest_grade(word):
    highest_grade = 0
    for literal in word:
        if literal in [x[0] for x in kanji] and literal != word:
            grade = kanji[[x[0] for x in kanji].index(literal)][1]
            if grade == 'None' or highest_grade == 'None' or int(grade) > int(highest_grade):
                highest_grade = grade
    return highest_grade

vocab_dict = {}
for k in kanji: 
    vocab_all_k = [x for x in vocab if k[0] in x[0]]
    vocab_dict[k[0]] = [x for x in vocab_all_k if highest_grade(x[0]) == k[1]]

pickle.dump( vocab_dict, open( "vocab_dict.p", "wb" ) )
