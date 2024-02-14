from flask import Blueprint, request, jsonify, current_app, Response
from flask_restful import Api, Resource
from datetime import datetime
from auth_middleware import token_required
from model.messages import Message  # Import the Message class

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
        
        def put(self, message):
            Message.update(message)
    class _Send(Resource):
        def post(self):
            body = request.get_json()
            # Fetch data from the form
            uid = body.get('uid')
            message = body.get('message')
            if uid is not None:
                new_message = Message(uid=uid, message=message)
            message = new_message.create()
            if message:
                return message.read()
            return {'message': f'Processed {uid}, either a format error or User ID {uid} is duplicate'}, 400

    class _Delete(Resource):
        @token_required
        def delete(self, current_user, Message): # Delete Method
            body = request.get_json()
            message_id = body.get('message_id')
            if not message_id:
                return {'message': 'Message ID is missing'}, 400

            message = Message.query.get(message_id)
            if not message:
                return {'message': 'Message not found'}, 404

            if message.uid != current_user.uid:
                return {'message': 'You are not authorized to delete this message'}, 403

            try:
                message.delete()
                return {'message': 'Message deleted successfully'}, 200
            except Exception as e:
                return {'message': f'Failed to delete message: {str(e)}'}, 500

api.add_resource(MessageAPI._CRUD, '/')
api.add_resource(MessageAPI._Send, '/send')
api.add_resource(MessageAPI._Delete, '/delete')
