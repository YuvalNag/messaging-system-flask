from flask_restful import Resource, reqparse
from models.user import UserModel
import re


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email',
                        type=str,
                        required=True,
                        help='This field is required')
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help='This field is required')

    def post(self):
        request_data = UserRegister.parser.parse_args()
        emailRegex ='^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        if(not re.search(emailRegex, request_data['email'])):
            return {'message': 'Invalid email'}, 400

        if UserModel.find_by_email(request_data['email']):
            return {'message': 'User already exist'}, 401

        user = UserModel(**request_data)
        user.save_to_db()

        return {'message': 'User created successfully'}, 201

