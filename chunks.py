import random
import compareKanji as ck


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
    def generate(self, size, n_answers, kanji_similarity, answer_similarity,
                 grade, allow_duplicates=False):
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

        chunk = Chunk()

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

            options = self.__choice_list(kanji, answer_difficulty, grade,
                                         n_answers - 1)
            hint = self.__hint(kanji)

            chunk.add_question(kanji, meaning, options, hint)

        return chunk

    # TODO: this database query could be removed if we had a pickled dictionary
    # mapping kanji to meanings
    def __choice_list(self, kanji, difficulty, grade, n):
        options = ck.giveChoicesKanji(kanji, difficulty, n, self.database)
        query = ('SELECT meanings FROM kanji WHERE grade=? AND literal IN ' +
                 str(tuple(options)))
        meanings = self.database.fetch_all(query, repr(grade))

        return [meaning[0] for meaning in meanings]

    # TODO: implement
    def __hint(self, kanji):
        pass


class Chunk(object):
    """
    Represents a chunk of multiple questions.
    """
    def __init__(self):
        self.questions = []
        self.next_question_idx = 0
        self.history = []

    def add_question(self, kanji, meaning, options, hint):
        self.questions.append((kanji, meaning, options, hint))

    def next_question(self):
        idx = self.next_question_idx
        self.next_question_idx += 1

        # randomize the full list of answers
        kanji, meaning, options, _ = self.questions[idx]
        choice_list = options + [meaning]
        random.shuffle(choice_list)

        return kanji, choice_list

    def done(self):
        return self.next_question_idx >= len(self.questions)

    def validate_previous_question(self, answer):
        if self.next_question_idx == 0:
            return None
        _, correct, _, _ = self.questions[self.next_question_idx - 1]

        # the answer is either the full string from the button, or one of the words
        # in the comma-separated list
        meaning_list = [meaning.strip() for meaning in correct.split(',')]
        if answer == correct or answer.strip() in meaning_list:
            right_answer = True
        else:
            right_answer = False

        self.history.append(right_answer)

        return right_answer

