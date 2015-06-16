from random import choice
from chunks import Parameters

size              = [5]
n_answers         = range(2, 5)
max_strokes       = [0] #will be changed by min_strokes
min_strokes       = range(1, 9)
kanji_similarity  = [0] # currently unused
answer_similarity = [0.0, 0.5, 1.0]
grade             = range(1, 6)
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
    
    
    params = Parameters(**{p: choice(globals()[p]) for p in Parameters.params()})
    params.max_strokes = params.min_strokes + 3
    params.grade = choice(grade)

    return params
