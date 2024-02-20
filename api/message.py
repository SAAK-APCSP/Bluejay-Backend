from flask import Blueprint, request, jsonify, current_app, Response
from flask_restful import Api, Resource
from datetime import datetime
import jwt
from auth_middleware import token_required
from model.messages import Message  # Import the Message class
from __init__ import app, db

message_api = Blueprint('message_api', __name__, url_prefix='/api/messages')

api = Api(message_api)

class MessageAPI:
    class _CRUD(Resource):
        @token_required
        def post(self, current_user, Message): # Create Method
            body = request.get_json()

            # Validate message content
            message_content = body.get('message')
            if not message_content:
                return {'message': 'Message content is missing'}, 400

            # Create Message object
            message = Message(uid=current_user.uid, message=message_content)

            # Add message to database
            try:
                created_message = message.create()
                return jsonify(created_message.read()), 201
            except Exception as e:
                return {'message': f'Failed to create message: {str(e)}'}, 500

        @token_required()
        def get(self, _): # Read Method
            messages = Message.query.all()
            json_ready = [message.read() for message in messages]
            return jsonify(json_ready)

        def put(self, old_message, new_message, likes):
            Message.update(old_message, new_message, likes)
