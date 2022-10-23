import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_NAME, DB_USER, DB_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = F"postgresql://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}"
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], data['categories'])

    def test_post_question(self):
        question = {
            'question': 'Who won the 2021/2022 english premier league?',
            'answer': 'Mancity',
            'difficulty': 3,
            'category': 6
        }
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
    
    def test_search(self):
        search_term = {
            'searchTerm': 'World'
        }
        res = self.client().post('/search', json=search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], len(data['questions']))
    
    def test_questions_by_category(self):
        res = self.client().get('/categories/6/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], data['questions'])
        self.assertTrue(data['total_questions'], data['current_category'])

    def test_delete_question(self):
        res = self.client().delete('/questions/3')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], '3')

    def test_quiz(self):
        quiz_round = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Sports',
                'id': 6
                }
        }
        res = self.client().post('/quizzes', json=quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], data['question'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()