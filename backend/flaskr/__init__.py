import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    all_questions = [question.format() for question in questions]
    current_questions = all_questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={'/': {'origins': '*'}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):

        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():

        categories_query = Category.query.all()
        categories = {}
        for category in categories_query:
            categories[category.id] = category.type

        if (len(categories) == 0):
            abort(404)
    
        return jsonify({
            'success': True,
            'categories': categories
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        questions_query = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions_query)

        categories_query = {}
        categories = Category.query.order_by(Category.type).all()
        for category in categories:
            categories_query[category.id] = category.type
        
        if len(current_questions) == 0:
            abort(404)
        
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions_query),
            'categories': categories_query,
            'current_category': None
        })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            if question: 
                question.delete()
                return jsonify({
                    'success': True,
                    'deleted': question_id
                })
            else:
                abort(404)
        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()

            questions_query = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions_query)
            
            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(questions_query)
            })
        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search', methods=['POST'])
    def search():
        body = request.get_json()
        search = body.get('searchTerm')
        questions = Question.query.filter(Question.question.ilike(f'%{search}%')).all()
        
        if questions:
            current_questions = paginate_questions(request, questions)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(questions)
            })
        else:
            abort(404)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def questions_by_category(category_id):
        category = Category.query.filter_by(id=category_id).one_or_none()

        if category:
            current_questions = paginate_questions(request, Question.query.filter_by(category=str(category_id)).all())
            questions_len = len(Question.query.filter_by(category=str(category_id)).all())
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': questions_len,
                'current_category': category.type
            })
        else:
            abort(404)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        try:
            body = request.get_json()
            if 'quiz_category' not in body and 'previous_questions' not in body:
                abort(422)
            
            category = body.get('quiz_category')
            category_id = category['id']
            previous_questions = body.get('previous_questions')
            current_question_not_in_previous = Question.id.notin_((previous_questions))
            
            if category_id == 0:
                available_questions = Question.query.filter(current_question_not_in_previous).all()
            else:
                available_questions = Question.query.filter_by(category=category_id).filter(current_question_not_in_previous).all()

            random_question_pick = random.randrange(0, len(available_questions))

            if len(available_questions) > 0:
                new_question  = available_questions[random_question_pick].format()
                return jsonify({
                    'success': True,
                    'question': new_question
                })
            else:
                abort(404)
        except:
            abort(422)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Page not found'
        })
    
    @app.errorhandler(422)
    def unprocessable_recource(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable recource'
        }), 422
    return app

