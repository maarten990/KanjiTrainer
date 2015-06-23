from parameter_sampling import *
from chunks import ChunkGenerator
from collections import defaultdict
from sqlreader import db_path, db_commit
import pickle
import sqlite3

kanji = defaultdict(lambda: [])
radicalMeanings = pickle.load(open("static/radicalMeanings.p", "rb"))

db = sqlite3.connect(db_path)
cursor = db.cursor()
for grade_ in range(1, 10):
    for row in cursor.execute('SELECT literal, meanings, stroke_count FROM kanji WHERE grade=?',
                              repr(grade_)):
        kanji[grade_].append((row[0], row[1], row[2]))
db.close()

chunkgen = ChunkGenerator(kanji, radicalMeanings)
db.close()

kanji = "kanji"
vocab = "vocab"

ranking = []
for i0 in grade:
    for i1 in answer_similarity:
        for i2 in n_answers:
            for i3 in question_type:
                for i4 in min_strokes:
                    for i5 in reversed_bool:
                        params = [5, i2, i4, i4+3, i1, i0, i5, i3]
                        params2 = Parameters(size=params[0], n_answers=params[1],
                                             min_strokes=params[2], max_strokes=params[3],
                                             answer_similarity=params[4], grade=params[5],
                                             reversed_bool=params[6], question_type=params[7])
                        try:
                            chunkgen.generate(params2)
                            ranking.append(params)
                        except Exception as exception:
                            if str(exception) != "Not enough kanji found for these parameters":
                                ranking.append(params)
                            print(exception)

pickle.dump(ranking, open("static/parameter_ranking.p", "wb"))
