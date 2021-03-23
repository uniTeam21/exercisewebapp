from datetime import datetime
from exercisewebapp import db, login_manager
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.schema import ColumnDefault


groupslink = db.Table('groupslink',
                  db.Column('user_id', db.Integer,db.ForeignKey('user.id')),
                  db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
                  )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref="owner",uselist=True)
    groups = db.relationship('Group', secondary=groupslink, backref=db.backref('groups', lazy='dynamic'))


    def __repr__(self):
        return f"User(' User: {self.username}', Email: '{self.email}', ID: '{self.id}',\nGroups: {self.groups}\n, Posts: {self.posts})\n"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    #votes = db.relationship("PostVote", uselist=False, back_populates="post")

    def __repr__(self):
        return f"Post( Post ID:{self.id}, Title:'{self.title}', Date posted:'{self.date_posted}', Reps:{self.reps}, Group ID:{self.group_id}, User ID:{self.user_id})\n"

# class PostVote(db.Model):
#     post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
#     post = db.relationship("Post", back_populates="votes")
#     upvote_number = db.Column(db.Integer, ColumnDefault(0), nullable=False)
#     downvote_number = db.Column(db.Integer,ColumnDefault(0), nullable=False)
#     total_votes = db.Column(db.Integer, ColumnDefault(0), nullable=False)
#     member_count = db.Column(db.Integer, ColumnDefault(0), nullable=False)
#     def __repr__(self):
#         return f"PostVote( Post ID:{self.post_id},Upvotes: {self.upvote_number}, downvotes:{self.downvote_number}, Total votes:{self.total_votes} )\n"



class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_title = db.Column(db.String(100), nullable=False)
    date_started = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    leader_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f"Group({self.id},'{self.exercise_title}', '{self.date_started}'\n"



db.create_all()
db.session.commit()