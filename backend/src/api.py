import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
db = SQLAlchemy(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
# No permission required since this is a public route with access to all
def get_drinks():
    # query all drinks
    drinks = Drink.query.all()
    # if there are no drinks in DB then abort
    if len(drinks) == 0:
        abort(404)
    # create list for drinks
    drink_short = []
    # iterate through drinks list and append the .short formatted version (see models.py for implementation) to the above list
    for drink in drinks:
        drink_short.append(drink.short())
    
    # return return jsonified response that includes the drinks data in .short format
    return jsonify({
        'success': True,
        'status_code': 200,
        'drinks': drink_short
        })
    



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
# requires additional permissions, Currently only for baristas and managers.
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)
    drink_long = []
    # iterate through list of drinks and append them in .long form (see models.py for implementation) to the list above
    for drink in drinks:
        drink_long.append(drink.long())
    # return jsonified response that includes the drinks data in .long format
    return jsonify({
        'success': True,
        'status_code': 200,
        'drinks': drink_long
        })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
# requires additional permission. Currently only permitted for Managers
@requires_auth('post:drinks')
def create_drink():
    # retrieve json data included in the 'POST' request
    data = request.get_json() 

    # get title and recipe of drink
    new_title = data.get('title')
    new_recipe = data.get('recipe')
    # check that json request includes title and recipe
    if (new_title is None) or (new_recipe is None):
        abort (422)
    # assign title and recipe to a new drink
    new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
    try:
        # insert new drink into database
        new_drink.insert()
    except:
        # rollback if insert fails and abort with error
        db.session.rollback()
        abort(422, 'unprocessable or entry may already exist')
    # retrieve created drink data from DB    
    created_drink = Drink.query.filter_by(title=new_title).one_or_none()
    if created_drink is None:
        abort(404, 'error: new drink not created')
    # return json with created drink info in .long format
    return jsonify({
        'success': True,
        'status_code': 200,
        'drinks': created_drink.long()
    })

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
# requires additional permission. Currently only permitted for Managers
@requires_auth('patch:drinks')
def update_drinks(id):
    # retrieve drink data from DB filtered by the ID passed into the function from the http request
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)
    # retrieve json data included in the 'PATCH' request
    data = request.get_json()
    # check if user would like to update title or recipe
    if data.get('title'):
        updated_title = data.get('title')
        # assign new title to existing drink object
        drink.title = updated_title 
    
    if data.get('recipe'):
        updated_recipe = data.get('recipe')
        # assign new recipe to existing drink object
        drink.recipe = json.dumps(updated_recipe)
    try:
        # attempt to update DB
        drink.update()
    except:
        # rollback if update fails and abort with error
        db.session.rollback()
        abort(422)
    # retreive updated drink data from DB
    updated_drink = Drink.query.filter_by(id=id).one_or_none()
    if updated_drink is None:
        abort(422)
    # return json response with update drink data in .long format
    return jsonify({
        'success': True,
        'status_code': 200,
        'drinks': [updated_drink.long()]
    })

    





'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
# requires additional permission. Currently only permitted for Managers
@requires_auth('delete:drinks')
def delete_drink(id):
    # retrieve drink data from DB filtered by the ID passed into the function from the http request
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)
    # attempt to delete drink
    try:
        drink.delete()
    # if delete fails rollback and abort with error
    except:
        db.session.rollback()
        abort(422)
    # return json object with successfully deleted drink id
    return jsonify({
        'success': True,
        'status_code': 200,
        'delete': id
    })


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def bad_request(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response