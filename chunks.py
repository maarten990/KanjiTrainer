import random
import compareKanji as ck
import os

class Parameters(object):
    def __init__(self, size=5, n_answers=4, kanji_similarity=0.5,
                 answer_similarity=0.5, grade=1, allow_duplicates=False):
        self.size = int(size)
        self.n_answers = int(n_answers)
        self.kanji_similarity = float(kanji_similarity)
        self.answer_similarity = float(answer_similarity)
        self.grade = int(grade)
        self.allow_duplicates = bool(allow_duplicates)


class ChunkGenerator(object):
    def __init__(self, kanji, radical_meanings, database):
        """
        Parameters:
        kanji -- a dictionary mapping a grade to a list of tuples of kanji and
                 their meanings
        radical_meanings -- a dictionary mapping radicals to their meaning
        database -- an SQLReader instance
        """
        self.kanji = kanji
        self.radical_meanings = radical_meanings
        self.database = database

    # TODO: make use of kanji_similarity
    # TODO: don't be limited to picking from one grade
    def generate(self, params):
        """
        Generate a list of questions.

        Parameters:
        size -- number of questions to generate
        n_answers -- the number of possible answers to present
        kanji_similarity -- the similarity of the kanji on a scale from 0 to 1
        answer_variation -- the similarity within the answer on a scale from 0
                            to 1
        grade -- the grade to pick kanji from
        allow_duplicates -- allow duplicate kanji within the chunk
        """
        size = params.size
        n_answers = params.n_answers
        kanji_similarity = params.kanji_similarity
        answer_similarity = params.answer_similarity
        grade = params.grade
        allow_duplicates = params.allow_duplicates

        chunk = Chunk(n_answers, kanji_similarity, answer_similarity, grade)

        # List of potential indices into the kanji list, indices can be removed
        # to disallow duplicates.
        kanji_indices = list(range(len(self.kanji[grade])))

        # translate the answer_similarity measure to an easy/normal/hard scale
        # as used by compareKanji.py
        answer_difficulty = ('easy' if answer_similarity <= 0.33 else 'normal'
                             if answer_similarity <= 0.66 else 'hard')

        for _ in range(size):
            index = random.choice(kanji_indices)
            kanji, meaning = self.kanji[grade][index]

            if not allow_duplicates:
                kanji_indices.remove(index)

            if random.random() > 0.5:
                QuestionType = "meaning"
            else:
                QuestionType = "kanji"
           
            options = self.__choice_list(kanji, answer_difficulty, grade,
                                         n_answers - 1, QuestionType)
            hint = self.__hint(QuestionType, kanji, grade)

            if QuestionType == "kanji":
                question = "What is the meaning of the following kanji?"
                chunk.add_question(question, kanji, meaning, options, hint)
            else:
                question = "Which kanji belongs to the following meaning(s)?"
                chunk.add_question(question, meaning, kanji, options, hint)
        return chunk

    # TODO: this database query could be removed if we had a pickled dictionary
    # mapping kanji to meanings
    def __choice_list(self, kanji, difficulty, grade, n, QuestionType):
        options = ck.giveChoicesKanji(kanji, difficulty, n, self.database)

        # QuestionType == meaning
        if QuestionType != 'kanji':
            return options

        if n == 1:
            query = 'SELECT meanings FROM kanji WHERE grade=? AND literal=?'
            meanings = self.database.fetch_all(query, [repr(grade), options[0]])
        else:
            query = ('SELECT meanings FROM kanji WHERE grade=? AND literal IN ' +
                     str(tuple(options)))
            meanings = self.database.fetch_all(query, repr(grade))

        return [meaning[0] for meaning in meanings]

    def __hint(self, QuestionType, item, grade):
        filePath = "static/KanjiPics/" + item + ".png"
        query = ('SELECT radicals FROM kanji WHERE grade=' + str(grade) + \
                     ' AND literal = ' + repr(item))
        kanji_radicals = self.database.fetch_one(query)
        if QuestionType == "kanji":
            radical_text = "<ul>" 
            for radical in kanji_radicals[0].strip('\n').split(', '):
                if radical ==item:
                    radical_text += "<li>" + radical + \
                                    ": ? (This kanji is also a radical itself)""</li>"
                else:
                    radical_text += "<li>" + radical + ": " + \
                                    self.radical_meanings[radical] + "</li>"
            radical_text += "</ul>"
            hint = "Hint:<br> The kanji " + item + \
                   " consist of the following radicals:<br>" + radical_text
            if os.path.isfile(filePath):
               hint += '<img src="' + filePath + '" height="25%" width="25%">'
        # TODO: check how many radicals were found
        else: # QuestionType = "meaning":
            radical_text = "<ul>" 
            for radical in kanji_radicals[0].strip('\n').split(', '):
                if radical != item:
                    radical_text += "<li>" + self.radical_meanings[radical] + "</li>"
            radical_text += "</ul>"
            if radical_text != "<ul></ul>":
                hint = "Hint:<br> The kanji consist of the following radicals:" + \
                   "<br>" + radical_text
            else:
                hint = "Sorry, there is no hint for this kanji"    
        return hint

class Chunk(object):
    """
    Represents a chunk of multiple questions.
    """
    def __init__(self, n_answers, kanji_similarity, answer_similarity, grade):
        self.questions = []
        self.next_question_idx = 0
        self.history = []

        # save the parameters that were used to generate the chunk
        self.n_answers = n_answers

        self.kanji_similarity = kanji_similarity
        self.answer_similarity = answer_similarity
        self.grade = grade

    def add_question(self, question, kanji, meaning, options, hint):
        self.questions.append((question, kanji, meaning, options, hint))

    def next_question(self):
        idx = self.next_question_idx
        self.next_question_idx += 1

        # randomize the full list of answers
        question, item, choices, options, _ = self.questions[idx]
        choice_list = options + [choices]
        random.shuffle(choice_list)

        return question, item, choice_list

    def done(self):
        return self.next_question_idx >= len(self.questions)

    def get_hint(self):
        _, _, _, _, hint = self.questions[self.next_question_idx - 1]
        return hint

    def validate_previous_question(self, answer, time_taken, hint_requested):
        if self.next_question_idx == 0:
            return None
        _, _, correct, _, _ = self.questions[self.next_question_idx - 1]

        # the answer is either the full string from the button, or one of the words
        # in the comma-separated list
        meaning_list = [meaning.strip() for meaning in correct.split(',')]
        if answer == correct or answer.strip() in meaning_list:
            right_answer = True
        else:
            right_answer = False

        self.history.append((right_answer, time_taken, hint_requested))

        return right_answer

