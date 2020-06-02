import os
from flask import Flask
from flask_restful import Api
from flask_jwt import JWT
from datetime import timedelta

from security import authenticate, identity
from resources.user import UserRegister
from resources.message import Message, MessageList


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=3600)
app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
app.config['PROPAGATE_EXCEPTIONS'] = True

app.secret_key = 'yuval'

api = Api(app)




jwt = JWT(app, authenticate, identity)

api.add_resource(Message, '/message/', '/message/<int:message_id>')
api.add_resource(MessageList, '/messages')
api.add_resource(UserRegister, '/register')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
