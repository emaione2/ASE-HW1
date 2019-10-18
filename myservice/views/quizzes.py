from flakon import JsonBlueprint
from flask import request, jsonify, abort
from myservice.classes.quiz import Quiz, Question, Answer, NonExistingAnswerError, LostQuizError, CompletedQuizError

quizzes = JsonBlueprint('quizzes', __name__)

_LOADED_QUIZZES = {}  # list of available quizzes
_QUIZNUMBER = 0  # index of the last created quizzes


@quizzes.route("/quizzes", methods=['POST', 'GET'])
def all_quizzes():
    result = None
    if 'POST' == request.method:
        result = create_quiz(request)
    elif 'GET' == request.method:
        result = get_all_quizzes(request)
    return result

@quizzes.route("/quizzes/loaded", methods=['GET'])
def loaded_quizzes():  # returns the number of quizzes currently loaded in the system
    return jsonify(loaded_quizzes=len(_LOADED_QUIZZES))
    # return {'loaded_quizzes': _QUIZNUMBER}


@quizzes.route("/quiz/<id>", methods=['GET', 'DELETE'])
def single_quiz(id):
    global _LOADED_QUIZZES
    result = ""

    exists_quiz(id=id)

    if 'GET' == request.method:  
        quiz = _LOADED_QUIZZES[id]
        result = jsonify(quiz.serialize())

    elif 'DELETE' == request.method:
        quiz = _LOADED_QUIZZES.pop(id)

        answered = quiz.currentQuestion
        tot = len(quiz.questions)

        result = jsonify(answered_questions=answered, total_questions=tot)

    return result


@quizzes.route("/quiz/<id>/question", methods=['GET'])
def play_quiz(id):
    global _LOADED_QUIZZES
    result = ""

    exists_quiz(id=id)
    quiz: Quiz = _LOADED_QUIZZES[id]

    if 'GET' == request.method:  
        try:
            result = quiz.getQuestion()
        except LostQuizError:
            result = jsonify(msg='you lost!')
        except CompletedQuizError:
            result = jsonify(msg='completed quiz')

    return result


@quizzes.route("/quiz/<id>/question/<answer>", methods=['PUT'])
def answer_question(id, answer):
    global _LOADED_QUIZZES

    exists_quiz(id=id)
    quiz: Quiz = _LOADED_QUIZZES[id]
    
    try:
        quiz.isOpen()
    except CompletedQuizError:
        return jsonify(msg='completed quiz')
    except LostQuizError:
        return jsonify(msg='you lost!')

    if 'PUT' == request.method:

        result = ''
        try:
            result = quiz.checkAnswer(givenAnswer=answer)
        except CompletedQuizError:
            result = 'you won 1 million clams!'
        except LostQuizError:
            result = 'you lost!'
        except NonExistingAnswerError:
            result = 'non-existing answer!'

        return jsonify({'msg': result})

############################################
# USEFUL FUNCTIONS BELOW (use them, don't change them)
############################################


def create_quiz(request):
    global _LOADED_QUIZZES, _QUIZNUMBER

    json_data = request.get_json()
    qs = json_data['questions']
    questions = []
    for q in qs:
        question = q['question']
        answers = []
        for a in q['answers']:
            answers.append(Answer(a['answer'], a['correct']))
        question = Question(question, answers)
        questions.append(question)

    _LOADED_QUIZZES[str(_QUIZNUMBER)] = Quiz(_QUIZNUMBER, questions)
    _QUIZNUMBER += 1

    return jsonify({'quiznumber': _QUIZNUMBER - 1})


def get_all_quizzes(request):
    global _LOADED_QUIZZES

    return jsonify(loadedquizzes=[e.serialize() for e in _LOADED_QUIZZES.values()])


def exists_quiz(id):
    if int(id) > _QUIZNUMBER:
        abort(404)  # error 404: Not Found, i.e. wrong URL, resource does not exist
    elif not(id in _LOADED_QUIZZES):
        abort(410)  # error 410: Gone, i.e. it existed but it's not there anymore
