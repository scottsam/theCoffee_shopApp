import json
import os
from turtle import title

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from sqlalchemy import exc

from .auth.auth import AuthError, requires_auth
from .database.models import Drink, db_drop_and_create_all, setup_db

app = Flask(__name__)
setup_db(app)
CORS(app)

"""
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
"""
db_drop_and_create_all()

# ROUTES
"""
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks")
def drinks_short():
    # query all drinks available
    drinks = Drink.query.all()
    drinkShort = [drink.short() for drink in drinks]

    return jsonify({"success": True, "drinks": drinkShort})


"""
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def drinks_detail(f):
    # query all drinks available
    drinks = Drink.query.all()
    drinksLong = [drink.long() for drink in drinks]

    return jsonify({"success": True, "drinks": drinksLong})


"""
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drinks(f):
    body = request.get_json()

    if not body:
        abort(422)

    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)

    if new_title == None or new_recipe == None:
        abort(422)

    try:
        # convert the recipe to valid json object
        drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        drink.insert()
        print(drink)
    except:
        abort(400)

    return jsonify({"success": True, "drinks": [drink.long()]})


"""
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(f, drink_id):
    body = request.get_json()

    if not body:
        abort(422)

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        if "title" in body:
            drink.title = body.get("title")

        if "recipe" in body:
            drink.recipe = json.dumps(body.get("recipe"))

        drink.update()
        print(drink)

    except:
        abort(400)

    return jsonify({"success": True, "drinks": [drink.long()]})


"""
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(f, drink_id):

    try:

        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink == None:
            abort(404)
        drink.delete()
    except:
        abort(400)

    return jsonify({"success": True, "delete": drink_id})


# Error Handling
"""
Example error handling for unprocessable entity
"""


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422


"""
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

"""


@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": 404, "message": "Not Found"}), 404


@app.errorhandler(400)
def badrequest(error):

    return jsonify({"success": False, "error": 400, "message": "Bad request"}), 400


"""
@TODO implement error handler for 404
    error handler should conform to general task above

"""


@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": 404, "message": "Not Found"}), 404


"""
@TODO implement error handler for AuthError
    error handler should conform to general task above
"""


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({"success": False, "error": 401, "message": "Unauthorized"}), 401
