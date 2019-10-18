import unittest
import json
from flask import request, jsonify
from myservice.app import app as tested_app
from myservice.classes import quiz


class TestApp(unittest.TestCase):

    def test1(self):  # allpolls
        allAns = []
        allQuests = []

        ans11 = quiz.Answer("la 1", False)
        allAns.append(ans11)
        ans12 = quiz.Answer("la 2", False)
        allAns.append(ans12)
        ans13 = quiz.Answer("la trEEEEEEE`", True)
        allAns.append(ans13)
        allQuests.append(quiz.Question("Qual'EEEE` la o-PTZ-ione, baNMBIno?! ...", allAns))

        ans21 = quiz.Answer("piace", True)
        allAns.append(ans21)
        ans22 = quiz.Answer("brutto", False)
        allAns.append(ans22)
        allQuests.append(quiz.Question("non e` bello cio` che e` bello ... e` bello cio` che", allAns))

        genius = quiz.Quiz('Mike', allQuests)

        resp = genius.checkAnswer("la trEEEEEEE`")
        self.assertEqual(resp, 1)

