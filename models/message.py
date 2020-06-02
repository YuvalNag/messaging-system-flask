from db import db
from datetime import datetime
from models.user import UserModel

# receivers = db.Table('receivers',
#                      db.Column('message_id', db.Integer, db.ForeignKey(
#                          'messages.id'), primary_key=True),
#                      db.Column('receiver_id', db.Integer, db.ForeignKey(
#                          'users.id'), primary_key=True),
#                      db.Column('read', db.Boolean, default=False)
#                      )


class Receivers(db.Model):
    __tablename__ = 'receivers'
    message_id = db.Column('message_id', db.Integer,
                           db.ForeignKey('messages.id'), primary_key=True)
    receiver_id = db.Column('receiver_id', db.Integer,
                            db.ForeignKey('users.id'), primary_key=True)
    read = db.Column('read', db.Boolean, default=False)
    message = db.relationship("MessageModel", back_populates="receivers")
    receiver = db.relationship("UserModel", back_populates="received_messages")


class MessageModel(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(150))
    body = db.Column(db.Text)
    creation_date = db.Column(db.DateTime)

    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    receivers = db.relationship(
        "Receivers", back_populates="message", lazy='dynamic')
    # receivers = db.relationship(
    #     'UserModel', secondary=receivers, lazy='dynamic')

    def __init__(self, sender_id, subject, body, receivers_ids):
        self.sender_id = sender_id
        self.subject = subject
        self.body = body
        self.creation_date = datetime.now()
        print(receivers_ids)
        self.receivers_ids = receivers_ids

    def json(self):
        if self.sender:
            return {"sender": self.sender.email, "subject": self.subject, "body": self.body, "creation_date": self.creation_date.strftime("%Y-%m-%d %H:%M:%S")}
        else:
            return {"subject": self.subject, "body": self.body, "creation_date": self.creation_date.strftime("%Y-%m-%d %H:%M:%S")}

    @classmethod
    def find_message_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        for receiver_id in self.receivers_ids:
            receiver = UserModel.find_by_id(receiver_id)
            receiver_association = Receivers()
            receiver_association.receiver = receiver
            self.receivers.append(receiver_association)
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self, user, from_sent):
        if from_sent:
            self.sender_id = None
        else:
            self.receivers.filter_by(
                message_id=self.id, receiver_id=user.id).delete()

        have_receiver = self.receivers.filter_by(message_id=self.id).first()
        have_sender = self.sender_id != None
        if not have_receiver and not have_sender:
            db.session.delete(self)

        db.session.commit()
