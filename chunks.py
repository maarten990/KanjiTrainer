import random
import compareKanji as ck
import os
import pickle
from sqlreader import fetch_all, fetch_one
from IPython import embed

class Parameters(object):
    def __init__(self, size=5, n_answers=4, max_strokes=3, min_strokes=1, kanji_similarity=0.5,
                 answer_similarity=0.5, grade=1, allow_duplicates=False,
                 reversed_bool=False, question_type="kanji"):
        self.size = int(size)
        self.n_answers = int(n_answers)
        self.max_strokes = int(max_strokes)
        self.min_strokes = int(min_strokes)
        self.kanji_similarity = float(kanji_similarity)
        self.answer_similarity = float(answer_similarity)
        self.grade = int(grade)
        self.allow_duplicates = bool(allow_duplicates)
        self.reversed_bool = bool(reversed_bool)
        self.question_type = str(question_type)    

    def params():
        return [p for p in dir(Parameters()) if '__' not in p and p != 'params']

    def __params(self):
        return [p for p in dir(self) if '__' not in p and p != 'params']

    def __repr__(self):
        param_str = ', '.join(['{}={}'.format(p, getattr(self, p))
                               for p in self.__params()])

        return 'Parameters({})'.format(param_str)


class ChunkGenerator(object):
    def __init__(self, kanji, radical_meanings):
        """
        Parameters:
        kanji -- a dictionary mapping a grade to a list of tuples of kanji and
                 their meanings
        radical_meanings -- a dictionary mapping radicals to their meaning
        """
        self.kanji = kanji
        self.radical_meanings = radical_meanings
        self.vocab_dict = pickle.load( open( "static/vocab_dict.p", "rb" ) )

    # TODO: make use of kanji_similarity
    # TODO: don't be limited to picking from one grade
    def generate(self, params):
        """
        Generate a list of questions.

        Parameters:
        size -- number of questions to generate
        n_answers -- the number of possible answers to present
        max_strokes -- the max number of strokes required to form the kanji
        min_strokes -- the min number of strokes required to form the kanji
        kanji_similarity -- the similarity of the kanji on a scale from 0 to 1
        answer_variation -- the similarity within the answer on a scale from 0
                            to 1
        grade -- the grade to pick kanji from
        allow_duplicates -- allow duplicate kanji within the chunk
        """
        size = params.size
        n_answers = params.n_answers
        max_strokes = params.max_strokes
        min_strokes = params.min_strokes
        kanji_similarity = params.kanji_similarity
        answer_similarity = params.answer_similarity
        grade = params.grade
        allow_duplicates = params.allow_duplicates
        reversed_bool = params.reversed_bool
        question_type = params.question_type #kanji, vocab 

        chunk = Chunk(params)

        # List of potential indices into the kanji list, indices can be removed
        # to disallow duplicates.
        kanji_indices = list(range(len(self.kanji[grade])))
        
        # Filter out all kanji with a stroke_count up to max_strokes.
        # Horrendous piece of code. Don't show your kids.
        new_kanji_indices = []
        for index in kanji_indices:
            _,_,stroke_count = self.kanji[grade][index]
            if int(stroke_count) <= max_strokes and int(stroke_count) >= min_strokes:
                new_kanji_indices.append(index)
        kanji_indices = new_kanji_indices

        # translate the answer_similarity measure to an easy/normal/hard scale
        # as used by compareKanji.py
        answer_difficulty = ('easy' if answer_similarity <= 0.33 else 'normal'
                             if answer_similarity <= 0.66 else 'hard')

        for _ in range(size):
            if question_type == "kanji":
                index = random.choice(kanji_indices)
                kanji, meaning, stroke_count = self.kanji[grade][index]
                options = self.__choice_list(kanji, answer_difficulty, grade,
                                         n_answers - 1, reversed_bool)
                hint = self.__hint(reversed_bool, kanji, grade)
                if not reversed_bool:
                    question = "What is the meaning of the following kanji?"
                    options += [meaning]
                    random.shuffle(options)
                    chunk.add_question(question, kanji, meaning, options, hint)
                else:
                    question = "Which kanji belongs to the following meaning(s)?"
                    options += [kanji]
                    random.shuffle(options)
                    chunk.add_question(question, meaning, kanji, options, hint)
            else: #question_type == vocab
                kanji = ""
                while not kanji in self.vocab_dict or self.vocab_dict[kanji] == []:
                    index = random.choice(kanji_indices)
                    kanji, meaning, stroke_count = self.kanji[grade][index]
                compound_choice = self.vocab_dict[kanji]
                choice = random.choice(compound_choice)
                item, _, item_meaning = choice
                selection = [x for x in compound_choice if x != choice] 
                random.shuffle(selection)            
                
                #easy: option compounds
                #normal: option compounds and 0.5 item compounds
                #hard: option compounds and all item compounds 
                if answer_difficulty == "easy":
                    selection = []
                elif answer_similarity == "normal":
                    selection = selection[::2]

                options = self.__choice_list(kanji, answer_difficulty, grade,
                                         n_answers - 1, reversed_bool)

                def check_compatibility(element):
                    for i in [0,2]:
                        if element[i] in [x[i] for x in selection]:
                            return False
                        if "(surname)" in element[2] or "~" in element[2]:
                            return False 
                    return True

                for option in options:
                    if option in self.vocab_dict:
                        if check_compatibility(self.vocab_dict[option]):
                            selection.extend(self.vocab_dict[option])

                #make we have enough anwsers to present
                while len(selection) < n_answers - 1:
                    kanji, _, _ = self.kanji[grade][random.choice(kanji_indices)]
                    if kanji in self.vocab_dict:
                        if check_compatibility(self.vocab_dict[kanji]):
                            selection.extend(self.vocab_dict[kanji])

                sampled_selection = random.sample(selection,n_answers - 1)

                print(sampled_selection)
                #remove dublicates: on kanji and meaning
                hint = self.__hint(reversed_bool, kanji, grade)  
                if not reversed_bool:
                    question = "What is the meaning of the following word?"
                    options = [x[2] for x in sampled_selection] + [item_meaning]
                    random.shuffle(options)
                    chunk.add_question(question, item, item_meaning, options, hint)
                else:
                    question = "Which word belongs to the following meaning(s)?"
                    options = [x[0] for x in sampled_selection] + [item]
                    random.shuffle(options)
                    chunk.add_question(question, item_meaning, item, options, hint)
            if not allow_duplicates:
                kanji_indices.remove(index)
        return chunk

    # TODO: this database query could be removed if we had a pickled dictionary
    # mapping kanji to meanings
    def __choice_list(self, kanji, difficulty, grade, n, reversed_bool):
        options = ck.giveChoicesKanji(kanji, difficulty, n)

        if reversed_bool:
            return options

        if n == 1:
            query = 'SELECT meanings FROM kanji WHERE grade=? AND literal=?'
            meanings = fetch_all(query, [repr(grade), options[0]])
        else:
            query = ('SELECT meanings FROM kanji WHERE grade=? AND literal IN ' +
                     str(tuple(options)))
            meanings = fetch_all(query, repr(grade))

        return [meaning[0] for meaning in meanings]

    def __hint(self, reversed_bool, item, grade):
        filePath = "static/KanjiPics/" + item + ".png"
        query = ('SELECT radicals FROM kanji WHERE grade=' + str(grade) + \
                     ' AND literal = ' + repr(item))
        kanji_radicals = fetch_one(query)
        if not reversed_bool:
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
        else:
            radical_text = "<ul>" 
            for radical in kanji_radicals[0].strip('\n').split(', '):
                if radical != item:
                    radical_text += "<li>" + self.radical_meanings[radical] + "</li>"
            radical_text += "</ul>"
            if radical_text != "<ul></ul>":
                hint = "Hint:<br> The kanji consist of the following radicals:" + \
                   "<br>" + radical_text
            else:
                hint = "Hint:<br> The kanji does not consist of any radicals"    
        return hint

class Chunk(object):
    """
    Represents a chunk of multiple questions.
    """
    def __init__(self, parameters):
        self.questions = []
        self.next_question_idx = 0
        self.history = []

        # save the parameters that were used to generate the chunk
        self.parameters = parameters

    def add_question(self, question, kanji, meaning, options, hint):
        self.questions.append((question, kanji, meaning, options, hint))

    def next_question(self):
        idx = self.next_question_idx
        self.next_question_idx += 1

        # randomize the full list of answers
        question, item, choices, options, _ = self.questions[idx]

        return question, item, options

    def repeat_previous_question(self):
        if self.next_question_idx > 0:
            idx = self.next_question_idx - 1
        else:
            idx = 0

        # randomize the full list of answers
        question, item, choices, options, _ = self.questions[idx]

        return question, item, options

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

