from flask import Flask, render_template, request, session
from search import searchMovie
from dbstruct import db, user, movie, movielist
from auth import auth
from watchlist import movies
from lists import lists
from clubs import clubs

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(movies)
app.register_blueprint(lists)
app.register_blueprint(clubs)

@app.route('/')
def home():
    return render_template('index.html', username=session.get('username'))

@app.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        results = searchMovie(query)
    else:
        results = []
    
    user_lists = []
    club_lists = []
    if 'userID' in session:
        current_user = user.query.get(session['userID'])
        user_lists = movielist.query.filter_by(userID=session['userID']).all()
        # all club lists (public, will have to add private feature later)
        for c in current_user.clubs:
            club_lists.extend(c.lists)
    
    return render_template('search.html', query=query, results=results, user_lists=user_lists, club_lists=club_lists)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)