import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()
print('DB has been reset.')


# ROUTES

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    sel = Drink.query.all()
    drinks = [drink.short() for drink in sel]
    return jsonify({
        'success': True,
        'drinks': drinks
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
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    sel = Drink.query.all()
    drinks = [drink.long() for drink in sel]
    return jsonify({
        'success': True,
        'drinks': drinks
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
@requires_auth('post:drinks')
def create_drink(payload):  # Why do we need payload?
    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)
    if (new_title is None) or (new_recipe is None):
        abort(400)
    new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
    # print('_---_---_---_---_---_---_')
    # print(json.dumps(new_recipe))
    # print(new_drink)
    # print('_---_---_---_---_---_---_')
    new_drink.insert()

    sel = Drink.query.filter_by(title=new_title).all()
    drink = [d.long() for d in sel]

    return jsonify({
        'success': True,
        'drinks': drink
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


@app.route('/drinks/<int:drink_id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink_recipe(payload, drink_id):
    body = request.get_json()
    sel = Drink.query.get(drink_id)

    if sel is None:
        abort(404)
    sel.title = body.get('title', sel.title)
    recipe = json.dumps(body.get('recipe'))

    if 'recipe' not in body:
        # if recipe is False:
        sel.recipe = sel.recipe
    else:
        sel.recipe = recipe
    try:
        sel.update()
    except:
        abort(422)
    select = Drink.query.get(drink_id)
    return jsonify({
        'success': True,
        'drinks': sel.long()
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


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    sel = Drink.query.get(drink_id)
    if sel is None:
        abort(404)
    try:
        sel.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except:
        abort(422)


# Error Handling
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

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(AuthError)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['code'],
    }), error.status_code


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
