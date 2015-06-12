from random import choice
from chunks import Parameters

size              = [5]
n_answers         = range(2, 7)
max_strokes       = range(3, 11)
min_strokes       = range(2, 5)
kanji_similarity  = [0] # currently unused
answer_similarity = [0.0, 0.5, 1.0]
grade             = range(1, 6)
allow_duplicates  = [False]
reversed_ratio    = [0, 1]

def sample_parameters():
    params = Parameters(**{p: choice(globals()[p]) for p in Parameters.params()})

    # ensure that max_strokes >= min_strokes
    if params.max_strokes < params.min_strokes:
        params.max_strokes = params.min_strokes

    return params
