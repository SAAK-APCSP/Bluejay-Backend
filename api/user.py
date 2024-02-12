import json, jwt
from flask import Blueprint, request, jsonify, current_app, Response
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime
from auth_middleware import token_required

from model.users import User
from model.users import Messages

user_api = Blueprint('user_api', __name__,
                   url_prefix='/api/users')

message_api = Blueprint('message_api', __name__, 
                    url_prefix='/api/message')

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(user_api)
m_api = Api(message_api)

class MessageAPI:
    class _CRUD(Resource):
        def post(self):
            body = request.get_json()

            uid = body.get('uid')
            message_text = body.get('message')

            # Get sender's name from the uid
            sender = User.query.filter_by(uid=uid).first()
            if not sender:
                return {'message': 'Sender not found'}, 404

            message = Messages(uid=uid,
                               name=sender.name,
                               message=message_text,
                               date_sent=None,  # You can set the date_sent accordingly
                               likes=0,
                               comments=0)

            db.session.add(message)
            db.session.commit()

            # Success returns json of the message
            return jsonify(message.read())

        def put(self, message_id):
            '''Update a message'''
            message = Messages.query.get(message_id)
            if not message:
                return {'message': 'Message not found'}, 404

            body = request.get_json()
            message.message = body.get('message', message.message)
            message.uid = body.get('uid', message.uid)

            # Update other fields as needed (e.g., likes, comments)

            db.session.commit()
            return jsonify(message.read()), 200
            # Failure returns error

        def get(self):
            '''Get all messages'''
            messages = Messages.query.all()
            message_list = [message.read() for message in messages]
            return jsonify(message_list)

class UserAPI:        
    class _CRUD(Resource):  # User API operation for Create, Read.  THe Update, Delete methods need to be implemeented
        @token_required
        def post(self, current_user): # Create method
            ''' Read data for json body '''
            body = request.get_json()
            
            ''' Avoid garbage in, error checking '''
            # validate name
            name = body.get('name')
            if name is None or len(name) < 2:
                return {'message': f'Name is missing, or is less than 2 characters'}, 400
            # validate uid
            uid = body.get('uid')
            if uid is None or len(uid) < 2:
                return {'message': f'User ID is missing, or is less than 2 characters'}, 400
            # look for password and dob
            password = body.get('password')
            dob = body.get('dob')
            ''' #1: Key code block, setup USER OBJECT '''
            uo = User(name=name, 
                      uid=uid)
            
            ''' Additional garbage error checking '''
            # set password if provided
            if password is not None:
                uo.set_password(password)
            # convert to date type
            if dob is not None:
                try:
                    uo.dob = datetime.strptime(dob, '%Y-%m-%d').date()
                except:
                    return {'message': f'Date of birth format error {dob}, must be mm-dd-yyyy'}, 400
            
            ''' #2: Key Code block to add user to database '''
            # create user in database
            user = uo.create()
            # success returns json of user
            if user:
                return jsonify(user.read())
            # failure returns error
            return {'message': f'Processed {name}, either a format error or User ID {uid} is duplicate'}, 400
        @token_required
        def get(self, current_user): # Read Method
            users = User.query.all()    # read/extract all users from database
            json_ready = [user.read() for user in users]  # prepare output in json
            return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps

        
        def put(self, user_id):
            '''Update a user'''
            user = User.query.get(user_id)
            if not user:
                return {'message': 'User not found'}, 404
            body = request.get_json()
            user.name = body.get('name', user.name)
            user.uid = body.get('uid', user.uid)
            db.session.commit()
            return user.read(), 200

        def delete(self, user_id):
            '''Delete a user'''
            user = User.query.get(user_id)
            if not user:
                return {'message': 'User not found'}, 404
            db.session.delete(user)
            db.session.commit()
            return {'message': 'User deleted'}, 200
    
    class _Security(Resource):
        def post(self):
            try:
                body = request.get_json()
                if not body:
                    return {
                        "message": "Please provide user details",
                        "data": None,
                        "error": "Bad request"
                    }, 400
                ''' Get Data '''
                uid = body.get('uid')
                if uid is None:
                    return {'message': f'User ID is missing'}, 400
                password = body.get('password')
                
                ''' Find user '''
                user = User.query.filter_by(_uid=uid).first()
                if user is None or not user.is_password(password):
                    return {'message': f"Invalid user id or password"}, 400
                if user:
                    try:
                        token_payload = {
                            "_uid": user._uid,
                            "role": user.role 
                        }
                        token = jwt.encode(
                            token_payload,
                            current_app.config["SECRET_KEY"],
                            algorithm="HS256"
                        )
                        resp = Response("Authentication for %s successful" % (user._uid))
                        resp.set_cookie("jwt", token,
                                max_age=3600,
                                secure=True,
                                httponly=True,
                                path='/',
                                samesite='None'  # This is the key part for cross-site requests

                                # domain="frontend.com"
                                )
                        return resp
                    except Exception as e:
                        return {
                            "error": "Something went wrong",
                            "message": str(e)
                        }, 500
                return {
                    "message": "Error fetching auth token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 404
            except Exception as e:
                return {
                        "message": "Something went wrong!",
                        "error": str(e),
                        "data": None
                }, 500
    class Login(Resource):
        def post(self):
            data = request.get_json()

            uid = data.get('uid')
            password = data.get('password')

            if not uid or not password:
                response = {'message': 'Invalid creds'}
                return make_response(jsonify(response), 401)

            user = User.query.filter_by(_uid=uid).first()

            if user and user.is_password(password):
         
                response = {
                    'message': 'Logged in successfully',
                    'user': {
                        'name': user.name,  
                        'id': user.id
                    }
                }
                return make_response(jsonify(response), 200)

            response = {'message': 'Invalid id or pass'}
            return make_response(jsonify(response), 401)
    class _Create(Resource):
        def post(self):
            body = request.get_json()
            # Fetch data from the form
            name = body.get('name')
            uid = body.get('uid')
            password = body.get('password')
            role = body.get('role')
            if uid is not None:
                new_user = User(name=name, uid=uid, password=password, role=role)
            user = new_user.create()
            if user:
                return user.read()
            return {'message': f'Processed {name}, either a format error or User ID {uid} is duplicate'}, 400
    class _Delete(Resource):
        def post(self): # Delete Method
            body = request.get_json()
            uid = body.get('uid')
            password = body.get('password')
            user = User.query.filter_by(_uid=uid).first()
            if user is None or not user.is_password(password):
                return {'message': f'User {uid} not found'}, 404
            json = user.read()
            if user:
                try:
                    user.delete() 
                except Exception as e:
                    return {
                        "error": "Something went wrong!",
                        "message": str(e)
                    }, 500
            # 204 is the status code for delete with no json response
            return f"Deleted user: {json}", 204 # use 200 to test with Postman
            
    # building RESTapi endpoint
    api.add_resource(_CRUD, '/')
    api.add_resource(_Security, '/authenticate')
    api.add_resource(Login, '/login')
    api.add_resource(_Create, '/create')
    api.add_resource(_Delete, '/delete')