

from flask import request
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required, current_identity
from models.message import MessageModel
from db import db


class Message(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('subject',
                        type=str,
                        required=True,
                        help='This field is required')
    parser.add_argument('body',
                        type=str,
                        required=True,
                        help='This field is required')
    parser.add_argument('receivers_ids',
                        type=list,
                        location='json',
                        required=True,
                        help='This field is required')

    @jwt_required()
    def get(self, message_id):
        user = current_identity
        receiver_association = user.received_messages.filter_by(
            message_id=message_id).first()
        if receiver_association:
            receiver_association.read = True
            db.session.commit()
            return receiver_association.message.json()

        message = user.sent_messages.filter_by(id=message_id).first()
        if message:
            return message.json()
        return {"message": "Message not found"}, 404

    @jwt_required()
    def post(self):
        user = current_identity
        request_data = Message.parser.parse_args()
        message = MessageModel(user.id, **request_data)
        try:
            message.save_to_db()
        except:
            return {"message": "Internal error occurred."}, 500
        return message.json(), 201

    @jwt_required()
    def delete(self, message_id):
        user = current_identity
        message = MessageModel.find_message_by_id(message_id)
        from_sent = request.args.get('sent')
        if message:
            message.delete_from_db(user, from_sent)

        return {'message': 'Message deleted'}


class MessageList(Resource):
    @jwt_required()
    def get(self):
        user = current_identity
        unread = request.args.get('unread')
        sent_messages = []
        if unread:
            received_messages = [receiver_association.message.json()
                                 for receiver_association in user.received_messages.filter_by(receiver_id=user.id)]
        else:
            sent_messages = [message.json() for message in user.sent_messages]
            received_messages = [receiver_association.message.json()
                                 for receiver_association in user.received_messages.filter_by(receiver_id=user.id,read=0)]

        return {'sent': sent_messages,
                "received": received_messages}
