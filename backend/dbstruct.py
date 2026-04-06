from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import backref

db = SQLAlchemy()

# association tables at the top, use table names not class 
movie_list = db.Table('movie_list',
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True),
    db.Column('list_id', db.Integer, db.ForeignKey('movielists.id'), primary_key=True)
)

club_members = db.Table('club_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('clubs.id'), primary_key=True)
)

# user
class user(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.String(64), unique=True, nullable=True)  # nullable for testing
    nickname = db.Column(db.String(16), nullable=False, unique=True)
    
    # relationships
    movies = db.relationship('movie', backref='author', lazy=True)
    clubs = db.relationship('club', secondary=club_members, backref='members', lazy=True)

    def __repr__(self):
        return f"User('{self.nickname}')"

    def to_dict(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'discord_id': self.discord_id
        }

# movies
class movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    posterURL = db.Column(db.String(200))
    tmdbID = db.Column(db.Integer)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Movie('{self.title}')"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'poster_url': self.posterURL,
            'tmdb_id': self.tmdbID,
            'user_id': self.userID
        }

# clubs
class club(db.Model):
    __tablename__ = 'clubs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # club owns multiple lists (if club is gone, lists are gone) 
    lists = db.relationship('movielist', backref='club', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"Club('{self.name}')"

    def is_member(self, user):
        return user in self.members

    def add_member(self, user):
        if user not in self.members:
            self.members.append(user)

    def remove_member(self, user):
        if user in self.members:
            self.members.remove(user)

    def to_dict(self, include_members=False, include_lists=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_members:
            data['members'] = [m.to_dict() for m in self.members]
        else:
            data['member_count'] = len(self.members)
        
        if include_lists:
            data['lists'] = [lst.to_dict() for lst in self.lists]
        
        return data

# lists
class movielist(db.Model):
    __tablename__ = 'movielists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=True)

    # relationship to movies
    movies = db.relationship('movie', secondary=movie_list, backref='lists', lazy=True)

    def __repr__(self):
        return f"List('{self.name}')"

    def is_club_list(self):
        return self.club_id is not None

    def is_personal_list(self):
        return self.userID is not None

    def can_edit(self, user):
        if self.is_personal_list():
            return self.userID == user.id
        elif self.is_club_list():
            return self.club.is_member(user)
        return False

    def to_dict(self, include_movies=False):
        data = {
            'id': self.id,
            'name': self.name,
            'user_id': self.userID,
            'club_id': self.club_id,
            'type': 'club' if self.is_club_list() else 'personal',
            'movie_count': len(self.movies)
        }
        
        if include_movies:
            data['movies'] = [m.to_dict() for m in self.movies]
        
        return data
