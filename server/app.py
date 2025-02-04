#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.json

        username = data .get('username')
        password = data .get('password')
        image_url = data .get('image_url')
        bio = data .get('bio')

        user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )

        
        user.password_hash = password

        try:

            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            return user.to_dict(), 201

        except IntegrityError:

            return {'error': '422 Unprocessable Entity'}, 422



class CheckSession(Resource):
      def get(self):
        
        user_id = session['user_id']
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        
        return {}, 401

class Login(Resource):
    def post(self):

        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        user = User.query.filter(User.username == username).first()

        if user:
            if user.authenticate(password):

                session['user_id'] = user.id
                return user.to_dict(), 200

        return {'error': '401 Unauthorized'}, 401


class Logout(Resource):
    def delete(self):
        if not session.get('user_id'):
            return {'message': 'No active session'}, 401
        
        session['user_id'] = None
        return {}, 200  # Successfully logged out


class RecipeIndex(Resource):
    def get(self):
        if not session.get('user_id'):
            return {'message': 'Unauthorized'}, 401
        
        user = User.query.filter(User.id == session['user_id']).first()
        if user:
            return [recipe.to_dict() for recipe in user.recipes], 200
        else:
            return {'message': 'User not found'}, 404

    def post(self):
        if not session.get('user_id'):
            return {'message': 'Unauthorized'}, 401
        
        data = request.get_json()
        title = data['title']
        instructions = data['instructions']
        minutes_to_complete = data['minutes_to_complete']

        try:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=session['user_id'],
            )

            db.session.add(recipe)
            db.session.commit()

            return recipe.to_dict(), 201

        except IntegrityError:
            return {'error': '422 Unprocessable Entity'}, 422


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)