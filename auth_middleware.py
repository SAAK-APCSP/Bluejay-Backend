from functools import wraps
import jwt
from flask import request, abort, current_app
from model.users import User
from model.messages import Message # Import the Message class

def token_required(roles=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.cookies.get("jwt")
            if not token:
                return {
                    "message": "Authentication Token is missing!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401
            try:
                data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
                current_message = Message.query.filter_by(_uid=data["_uid"]).first()
            except Exception as e:
                return {
                    "message": "Something went wrong",
                    "data": None,
                    "error": str(e)
                }, 500

            return f(current_message, *args, **kwargs)  # Pass current_user to the decorated function

        return decorated

    return decorator

# You can then use the Message class as you would with the User class
