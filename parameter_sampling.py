from random import choice
from chunks import Parameters

grade             = range(1,6)
size              = [5]
n_answers         = range(2, 5)
max_strokes       = [0] #will be changed by min_strokes
min_strokes       = range(1, 9)
kanji_similarity  = [0] # currently unused
answer_similarity = [0.0, 0.5, 1.0]
allow_duplicates  = [False]
reversed_bool     = [False, True]
question_type     = ["kanji","vocab"]

kanji = "kanji"
vocab = "vocab"

ranking = []
for i0 in grade:
    for i1 in answer_similarity:
        for i2 in n_answers:
            for i3 in question_type:
                for i4 in min_strokes:
                    for i5 in reversed_bool:
                        ranking.append([5, i2, i4, i4+3, i1, i0, i5, i3])

def getRankingID(param):
    r = ranking.index([param.size,param.n_answers, param.min_strokes,
                       param.max_strokes, param.answer_similarity,
                       param.grade, param.reversed_bool, param.question_type])
    return r

def getParametes(ID):
    return Parameters(size=ranking[ID][0], n_answers=ranking[ID][1],
                      min_strokes=ranking[ID][2], max_strokes=ranking[ID][3],
                      answer_similarity=ranking[ID][4], grade=ranking[ID][5],
                      reversed_bool=ranking[ID][6], question_type=ranking[ID][7])

def sample_parameters(level):
    if level == 1:
        grade = [1]
    if level == 2:
        grade = range(1,3)
    if level == 3:
        grade = range(1,6)

    params = Parameters(**{p: choice(globals()[p] if p != 'grade' else grade)
                           for p in Parameters.params()})
    params.max_strokes = params.min_strokes + 3
    params.grade = choice(grade)

    return params


def safe_policy(level):
    if level == 1:
        return Parameters(size=5, n_answers=3, min_strokes=1, max_strokes=4,
                          answer_similarity=0.0, grade=1,
                          reversed_bool=False, question_type="kanji")

    if level == 2:
        return Parameters(size=5, n_answers=3, min_strokes=3, max_strokes=6,
                          answer_similarity=0.5, grade=3,
                          reversed_bool=False, question_type="kanji")

    if level == 3:
        return Parameters(size=5, n_answers=4, min_strokes=5, max_strokes=8,
                          answer_similarity=1.0, grade=5,
                          reversed_bool=False, question_type="vocab")

def update_parameters(params, score):
    """
    Return new parameters based on the previous ones and the predicted Likert
    score.
    """
    if score == 1:
        update = choice([11,10,9])
    elif score == 2:
        update = choice([6,5,4])
    elif score == 3:
        update = choice([1,0,-1])
    elif score == 4:
        update = choice([-4,-5,-6])
    else:
        update = choice([-9,-10,-11])
    currentRanking = getRankingID(params)
    newRanking = max(0,min(len(ranking),currentRanking + update))
    print('Updating parameters with score {}'.format(score))
    print('Now at rank:',newRanking)
    return getParametes(newRanking)
