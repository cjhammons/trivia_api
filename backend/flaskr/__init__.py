import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

from flask_migrate import Migrate
import sys

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]

    if len(categories) == 0:
      abort(404)
    
    return jsonify({
      'categories': formatted_categories,
      'totalCategories': len(formatted_categories),
      'success': True
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10

    questions = Question.query.all()
    formatted_questions = [question.format() for question in questions]

    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]

    if len(questions) == 0 or len(categories) == 0:
      abort(404)

    return jsonify({
      'success':True,
      'questions': formatted_questions[start:end],
      'totalQuestions': len(formatted_questions),
      'categories': formatted_categories,
      'currentCategory': 2
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    
    question = Question.query.get(question_id)
    if question == None:
      abort(404)
    try:
      question.delete()
    except:
      abort(400)

    return jsonify({
      'success': True
      })
    


  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():
    body = request.get_json()

    question = body.get('question', None)
    answer = body.get('answer', None)
    category = body.get('category', None)
    difficulty = body.get('difficulty', None)
  
    if (question==None) or (answer==None) or (category==None) or (difficulty==None):
      abort(422)

    question = Question(
      question=question,
      answer=answer,
      category=category,
      difficulty=difficulty
    )  
    question.insert()

    return jsonify({
      'success': True,
      'created_id': question.id
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    searchTerm = body.get('searchTerm', None)
    
    if searchTerm:
      try:
        questions = Question.query.filter(Question.question.ilike('%'+searchTerm+'%')).all()
        formatted_questions = [question.format() for question in questions]
        return jsonify({
          'success': True,
          'questions': formatted_questions,
          'totalQuestions': len(questions),
          })
      except:
        print(sys.exc_info())
        abort(400)
    else:
      abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_question_by_category(category_id):
    category = Category.query.get(category_id)
    if not category:
      abort(404)
    
    try:
      questions = Question.query.filter_by(category=category_id)
      formatted_questions = [question.format() for question in questions]

      return jsonify({
        'success':True,
        'questions': formatted_questions,
        'totalQuestions': len(formatted_questions),
        'currentCategory': category_id
      })
    except:
      print(sys.exc_info())
      abort(400)
    

 


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    category = body.get('quiz_category', 0)['id']
    previous_questions = body.get('previous_questions', [])

    questions= []
    if category == 0:
      qs = Question.query.all()
    else:
      if not Category.query.get(category):
          abort(404)
      qs = Question.query.filter_by(category=category)

    questions = [question.format() for question in qs]
    
    if len(questions) == 0:
      abort(404)

    index = 0
    while index < len(questions):
      question = questions[index]
      if int(question['id']) in previous_questions:
        del questions[index]
        index -= 1
      index += 1
      

    if len(questions) == 0:
      selected_question = None
    else:
      selected_question = random.choice(questions)

    return jsonify({
      'success': True,
      'question': selected_question
    })



  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Not Found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
        return jsonify({
          'success': False,
          'error': 422,
          'message': 'Could not process'
        }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad request'

    }), 400

  @app.errorhandler(405)
  def not_allowed(error):
      return jsonify({
      'success': False,
      'error': 405,
      'message': 'Method not allowed'

    }), 405  
  
  return app

