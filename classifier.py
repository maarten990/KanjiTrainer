import sqlite3
import numpy as np
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation, preprocessing, decomposition


def feature_transform_observations(history):
    correctness = [question[0] for question in history]
    durations   = [int(question[1]) for question in history]
    hints       = [False if question[2] == 'false' else True for question in history]
    hint_times  = [int(question[3]) for question in history]
    
    return (correctness.count(True),
            np.mean(durations),
            np.std(durations),
            hints.count(True),
            np.mean(hint_times),
            np.std(hint_times))


def feature_transform_parameters(params):
    pass


def classify(query, transform):
    db = sqlite3.connect('static/kanji.db')
    c = db.cursor()

    c.execute(query)

    histories = []
    scores    = []

    for hist, score in c.fetchall():
        histories.append(eval(hist))
        scores.append(score)

    training_data = preprocessing.scale([transform(hist) for hist in histories])
    training_data = decomposition.PCA().fit_transform(training_data)

    classifier = RandomForestClassifier()

    # perform 5-fold cross validation
    predictions = cross_validation.cross_val_score(classifier, training_data, scores, cv=5)
    print(predictions)

    classifier.fit(training_data, scores)
    print(classifier.score(training_data, scores))

    return classifier


def classify_parameters():
    pass

if __name__ == '__main__':
    obs_query = 'SELECT history, score FROM training_data'
    param_query = 'SELECT parameters, score FROM training_data'
    
    classify(obs_query, feature_transform_observations)