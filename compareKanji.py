#!/usr/bin/env python3
import sqlite3
import random
import numpy as np
from collections import defaultdict
from sqlreader import fetch_all, fetch_one, fetch_iterator

def getListDistance(list1, list2):
	numberSub = sum(1 for element in list2 if element not in list1)
	numberDeleteAdd = abs(len(list1)-len(list2))
	return numberSub + numberDeleteAdd

def getSimilarKanji(Kanjiliteral):
	similarKanji = []
	one = fetch_one('SELECT grade, radicals, stroke_count, meanings, on_reading,' +
                    'kun_reading FROM kanji WHERE literal=?', Kanjiliteral)
	literal_grade, literal_radicals, literal_stroke_count, literal_meanings, literal_on, literal_kun = one
	literal_radicals = literal_radicals.strip('\n').split(', ')
	for row in fetch_iterator('SELECT literal, radicals, stroke_count, meanings,' + 
                              'on_reading, kun_reading FROM kanji WHERE grade=?', literal_grade):
		radicalDistance = getListDistance(literal_radicals,row[1].strip('\n').split(', '))
		strokeCountDistance = abs(int(literal_stroke_count)-int(row[2]))*0.5
		meaningDistance = sum(1 for element in literal_meanings.strip('\n').split(', ') if 
				element not in row[3].strip('\n').split(', '))
		onDistance = sum(1 for element in literal_on.strip('\n').split(', ') if 
				element not in row[4].strip('\n').split(', '))
		kunDistance = sum(1 for element in literal_kun.strip('\n').split(', ') if 
				element not in row[5].strip('\n').split(', '))		
		similarKanji.append((row[0], radicalDistance, strokeCountDistance, 
                             meaningDistance, onDistance, kunDistance))

	return similarKanji

def random_pick(some_list, probabilities):
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    for item, item_probability in zip(some_list, probabilities):
        cumulative_probability += item_probability
        if x < cumulative_probability: break
    return item

def getKey(item):
    return item[1]

# TODO: make difficulty range from 0 to 1?
def giveChoicesKanji(literal, difficulty, numberChoices):
    difficultyStrength = 2.5
    similarKanji = getSimilarKanji(literal)
    summed = [(similarKanji[x][0],sum(similarKanji[x][1:])) for x in range(0,len(similarKanji))]
    sortedKanji = sorted(summed, key=getKey)
    #select kanji
    x = np.linspace(0,difficultyStrength,len(sortedKanji)-1)
    if difficulty == "easy":
            probabilities = np.exp(x)/sum(x)
    elif difficulty == "normal":
            probabilities = [1.0/len(sortedKanji)] * len(sortedKanji)
    else: #"hard"
            probabilities = np.exp(x[::-1])/sum(x)
    random_pick(sortedKanji[1:], probabilities)
    choices = []
    while len(choices) < numberChoices:
         choice = random_pick(sortedKanji[1:], probabilities)[0]
         if choice not in choices:
            choices.append(choice)
    return choices
