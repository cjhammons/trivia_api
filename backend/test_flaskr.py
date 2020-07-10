import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'path
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

    '''
    /categories endpoint tests
    '''
    def test_categories_success(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    '''
    GET /questions endpoint tests
    '''
    def test_questions_success_page_arg(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['currentCategory'])
        self.assertTrue(data['totalQuestions'])

    def test_questions_success_no_page_arg(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['currentCategory'])
        self.assertTrue(data['totalQuestions'])

   
    '''
    DELETE /questions endpoint tests
    '''
    def test_delete_question_success(self):
        id = 5
        res = self.client().delete('/questions/' + str(id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse(Question.query.get(id))

    def test_delete_question_bad_id(self):
        id = -1
        res = self.client().delete('/questions' + str(id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)  

  

    '''
    POST /questions endpoint tests
    '''
    def test_post_question_success(self):
        test_question = 'What is the answer to the ultimate question?'
        test_answer = 'forty two'
        test_category = 1
        test_difficulty = 1
        res = self.client().post('/questions', json={
            'question': test_question,
            'answer': test_answer,
            'category': test_category,
            'difficulty': test_difficulty
        })
        
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created_id'], True)

        new_question = Question.query.get(data['created_id'])
        self.assertEqual(new_question.question, test_question)
        self.assertEqual(new_question.answer, test_answer)
        self.assertEqual(new_question.category, test_category)
        self.assertEqual(new_question.difficulty, test_difficulty)
    
    def test_post_question_failure_no_question(self):
        test_question = 'What is the answer to the ultimate question?'
        test_answer = 'forty two'
        test_category = 1
        test_difficulty = 1
        res = self.client().post('/questions', json={
            'answer': test_answer,
            'category': test_category,
            'difficulty': test_difficulty
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_post_question_failure_no_answer(self):
        test_question = 'What is the answer to the ultimate question?'
        test_answer = 'forty two'
        test_category = 1
        test_difficulty = 1
        res = self.client().post('/questions', json={
            'question': test_question,
            'category': test_category,
            'difficulty': test_difficulty
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_post_question_failure_no_category(self):
        test_question = 'What is the answer to the ultimate question?'
        test_answer = 'forty two'
        test_category = 1
        test_difficulty = 1
        res = self.client().post('/questions', json={
            'question': test_question,
            'answer': test_answer,
            'difficulty': test_difficulty
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_post_question_failure_no_difficulty(self):
        test_question = 'What is the answer to the ultimate question?'
        test_answer = 'forty two'
        test_category = 1
        test_difficulty = 1
        res = self.client().post('/questions', json={
            'question': test_question,
            'answer': test_answer,
            'category': test_category,
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_post_search_success(self):
        res = self.client().post('questions/search', json={
            'searchTerm': 'title'
        })

        self.assertEqual(res.status_code, 200)
        
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['totalQuestions'])
    
    def test_post_search_bad_term(self):
        res = self.client().post('questions/search', json={
            'searchTerm': 'oogabooga69420lmaoooooooooooooooooo'
        })

        self.assertEqual(res.status_code, 200)
        
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['totalQuestions'], 0)

    def test_post_search_no_term(self):
        res = self.client().post('questions/search', json={})
        self.assertEqual(res.status_code, 422)

 

    '''
    GET /categories/{id}/questions 
    '''

    def test_get_question_by_category_success(self):
        test_category = 1
        res = self.client().get('categories/' + str(test_category)+ '/questions')

        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(test_category, data['currentCategory'])

    def test_get_question_by_category_fail_404(self):
        test_category = 42069
        res = self.client().get('categories/' + str(test_category)+ '/questions')

        self.assertEqual(res.status_code, 404)

        data = json.loads(res.data)
        self.assertFalse(data['success'])
    
    '''
    POST /quizzes
    '''

    def test_post_quizzes_success_all_categories(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category':{
                'type': None,
                'id': 0
            }
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)

        
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])


    def test_post_quizzes_success_specific_category(self):
        test_category= {
            'type': 'Science',
            'id': 6
        }
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': test_category}
        )

        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], test_category['id'])

    def test_post_quizzes_success_no_more_questions(self):
        test_category= {
            'type': 'Science',
            'id': 6
        }
        test_previous_questions = [10 , 11]
        res = self.client().post('/quizzes', json={
            'previous_questions': test_previous_questions,
            'quiz_category': test_category
        })

        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], True)
        self.assertFalse(data['question'])

    def test_post_quizzes_failure_invalid_category(self):
        test_category= {
            'type': 'Underwater Basket Weaving',
            'id': -1
        }
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': test_category
        })

        self.assertEqual(res.status_code, 404)

        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        
        




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()