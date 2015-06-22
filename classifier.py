import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import cross_validation, preprocessing, decomposition
from sklearn.metrics import confusion_matrix
from sklearn.grid_search import GridSearchCV
from chunks import Parameters
import pickle

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
            np.std(hint_times),
            np.mean(durations) - np.mean(hint_times))


def feature_transform_parameters(params):
    vector = [getattr(params, p) for p in Parameters.params()]
    for i, elem in enumerate(vector):
        if type(elem) == bool:
            vector[i] = 1 if elem == True else 0

        elif type(elem) == str:
            vector[i] = 0 if elem == 'kanji' else 1

    return vector


def get_data():
    query = 'SELECT history, score FROM training_data'

    db = sqlite3.connect('static/kanji.db')
    c = db.cursor()

    c.execute(query)

    histories = []
    scores    = []

    for hist, score in c.fetchall():
        histories.append(eval(hist))
        scores.append(score)

    data = [feature_transform_observations(hist) for hist in histories]

    return data, scores


def classify(transform, clf, parameters):
    """
    transform: transform database entry to feature vector
    clf: sklearn classifier class
    parameters: dict of parameters to be passed to GridSearch
    """
    data, scores = get_data()
    data = preprocessing.scale(data)
    data = decomposition.PCA().fit_transform(data)

    classifier = clf()
    grid = GridSearchCV(classifier, parameters, verbose=1, n_jobs=-1)
    grid.fit(data, scores)
    print('--------')
    print('Best score: {}'.format(grid.best_score_))
    print('Best params: {}'.format(grid.best_params_))

    return grid


def test_parameters():
    parameters = {'n_estimators': [1, 5, 10, 5],
                  'criterion': ['gini', 'entropy'],
                  'max_features': ['auto', 'sqrt', 'log2'],
                  'max_depth': [1, 5, 10, 15, None],
                  'min_samples_split': [1, 2, 3, 5, 10],
                  'min_samples_leaf': [1, 2, 3, 5],
                  'bootstrap': [True, False]}

    classify(feature_transform_observations, RandomForestClassifier,
             parameters)

    parameters = [{'kernel': ['rbf'], 'gamma': [0.0, 0.1, 0.3, 0.5, 1], 'shrinking': [True, False]},
                  {'kernel': ['linear'], 'shrinking': [True, False]},
                  {'kernel': ['poly'], 'degree': [2, 3, 4], 'gamma': [0.0, 0.1, 0.3, 0.5, 1], 'shrinking': [True, False]},
                  {'kernel': ['sigmoid'], 'gamma': [0.0, 0.1, 0.3, 0.5, 1], 'shrinking': [True, False]}
                  ]

    classify(feature_transform_observations, SVC,
             parameters)

    parameters = {'class_weight': [None, 'auto']}

    classify(feature_transform_observations, LogisticRegression,
             parameters)


def save_svm():
    svm = SVC(kernel='rbf', shrinking=True, gamma=1)
    data, labels = get_data()
    svm.fit(data, labels)

    with open('static/trained_svm.pickle', 'wb') as f:
        pickle.dump(svm, f)


def save_random_forest():
    forest = RandomForestClassifier(max_features='sqrt', n_estimators=5,
                                    criterion='entropy', bootstrap=False)

    data, labels = get_data()
    forest.fit(data, labels)

    with open('static/trained_forest.pickle', 'wb') as f:
        pickle.dump(forest, f)


if __name__ == '__main__':
    save_random_forest()