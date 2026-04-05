from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from dbstruct import db, user, movie, movielist, club

movies = Blueprint('movies', __name__)

@movies.route('/add_movie', methods=['POST'])
def addMovie():

    if 'userID' not in session:
        flash("must be logged in")
        return redirect(url_for('auth.login'))

    movieTitle = request.form.get('title')
    moviePoster = request.form.get('poster')
    movieTmdbId = request.form.get('tmdb_id')
    listIds = request.form.getlist('list_id')

    if not listIds:
        flash("select at least one list")
        return redirect(request.referrer or url_for('home'))

    existing_movie = movie.query.filter_by(
        userID=session['userID'], 
        tmdbID=movieTmdbId
    ).first()

    if existing_movie:
        new_movie = existing_movie
    else:
        new_movie = movie(
            title=movieTitle,
            posterURL=moviePoster,
            tmdbID=movieTmdbId,
            userID=session['userID']
        )
        db.session.add(new_movie)
        db.session.commit()

    current_user = user.query.get(session['userID'])
    added_to = []
    for list_id in listIds:
        listObj = movielist.query.get(list_id)
        if listObj and listObj.can_edit(current_user):
            if new_movie not in listObj.movies:
                listObj.movies.append(new_movie)
                added_to.append(listObj.name)

    if added_to:
        db.session.commit()
        flash(f"added {movieTitle} to {', '.join(added_to)}")
    else:
        flash(f"{movieTitle} is already in those lists")

    return redirect(request.referrer or url_for('home'))

@movies.route('/remove_movie/<int:movieId>', methods=['POST'])
def removeMovie(movieId):
    if 'userID' not in session:
        return redirect(url_for('auth.login'))
    
    listId = request.form.get('list_id')
    current_user = user.query.get(session['userID'])
    listObj = movielist.query.get(listId)
    
    if not listObj:
        flash("list not found")
        return redirect(request.referrer or url_for('home'))
    
    if not listObj.can_edit(current_user):
        flash("you don't have permission to edit this list")
        return redirect(request.referrer or url_for('home'))
    
    # find the movie for club lists
    movieRemove = movie.query.get(movieId)
    
    if movieRemove and movieRemove in listObj.movies:
        listObj.movies.remove(movieRemove)
        db.session.commit()
        flash(f"removed {movieRemove.title} from {listObj.name}")

        if not movieRemove.lists:
            db.session.delete(movieRemove)
            db.session.commit()
    else:
        flash("movie not found in list")
        
    return redirect(request.referrer or url_for('home'))

@movies.route('/my_lists')
def my_lists():

    if 'userID' not in session:
        return redirect(url_for('auth.login'))

    userId = session['userID']
    userLists = movielist.query.filter_by(userID=userId).all()

    return render_template('watchlist.html', lists=userLists)