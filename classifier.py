import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation, preprocessing, decomposition
from sklearn.metrics import confusion_matrix
from chunks import Parameters

# workaround for eval'ing the question types
kanji = 'kanji'
vocab = 'vocab'

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
    vector = [getattr(params, p) for p in Parameters.params()]
    for i, elem in enumerate(vector):
        if type(elem) == bool:
            vector[i] = 1 if elem == True else 0

        elif type(elem) == str:
            vector[i] = 0 if elem == 'kanji' else 1

    return vector


def classify(query, transform, clf):
    """
    query: sql query to perform
    transform: transform database entry to feature vector
    clf: sklearn classifier class
    """
    db = sqlite3.connect('static/kanji.db')
    c = db.cursor()

    c.execute(query)

    histories = []
    scores    = []

    for hist, score in c.fetchall():
        histories.append(eval(hist))
        scores.append(score)

    data = preprocessing.scale([transform(hist) for hist in histories])
    data = decomposition.PCA().fit_transform(data)

    training_data, test_data, training_labels, test_labels = cross_validation.train_test_split(data, scores)

    classifier = clf()

    # perform 5-fold cross validation
    predictions = cross_validation.cross_val_score(classifier, data, scores, cv=5)
    print(predictions)

    classifier.fit(training_data, training_labels)
    print(classifier.score(test_data, test_labels))

    print(confusion_matrix(test_labels, classifier.predict(test_data)))

    return classifier


if __name__ == '__main__':
    obs_query = 'SELECT history, score FROM training_data'
    param_query = 'SELECT parameters, score FROM training_data'

    print('Observations:')
    classify(obs_query, feature_transform_observations, RandomForestClassifier)
    print('\n-----------')
    print('Parameters:')
    classify(param_query, feature_transform_parameters, RandomForestClassifier)