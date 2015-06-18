import sqlite3
from sklearn.svm import SVC
from sklearn import cross_validation


def feature_transform(history):
	#TODO
	return (1, 2, 3)


def main():
	query = 'SELECT history, score FROM training_data'
	db = sqlite3.connect('static/kanji.db')
	c = db.cursor()

	c.execute(query)

	histories = []
	scores    = []

	for hist, score in c.fetchall():
		histories.append(eval(hist))
		scores.append(score)

	training_data = [feature_transform(hist) for hist in histories]

	classifier = SVC()

	# perform 5-fold cross validation
	predictions = cross_validation.cross_val_score(classifier, training_data, scores, cv=5)
	print(predictions)

	#classifier.fit(training_data, scores)


if __name__ == '__main__':
	main()