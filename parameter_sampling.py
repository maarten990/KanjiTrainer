from random import choice
from chunks import Parameters

size              = [10]
n_answers         = range(2, 7)
max_strokes       = range(3, 11)
min_strokes       = range(2, 5)
kanji_similarity  = [0] # currently unused
answer_similarity = [0.0, 0.5, 1.0]
grade             = range(1, 6)
allow_duplicates  = [False]
reversed_ratio    = [0, 1]

def sample_parameters():
    return Parameters(size              = choice(size),
                      n_answers         = choice(n_answers),
                      max_strokes       = choice(max_strokes),
                      min_strokes       = choice(min_strokes),
                      kanji_similarity  = choice(kanji_similarity),
                      answer_similarity = choice(answer_similarity),
                      grade             = choice(grade),
                      allow_duplicates  = choice(allow_duplicates),
                      reversed_ratio    = choice(reversed_ratio))