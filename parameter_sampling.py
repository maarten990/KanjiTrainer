from random import choice
from chunks import Parameters

size              = [5]
n_answers         = range(2, 5)
max_strokes       = [0] #will be changed by min_strokes
min_strokes       = range(1, 9)
kanji_similarity  = [0] # currently unused
answer_similarity = [0.0, 0.5, 1.0]
allow_duplicates  = [False]
reversed_bool     = [True, False]
question_type     = ["kanji","vocab"]


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
        return Parameters(size=5, n_answers=3, min_strokes=1, max_strokes=6,
                          answer_similarity=0.5, grade=3,
                          reversed_bool=False, question_type="kanji")

    if level == 3:
        return Parameters(size=5, n_answers=4, min_strokes=1, max_strokes=8,
                          answer_similarity=1.0, grade=6,
                          reversed_bool=False, question_type="vocab")