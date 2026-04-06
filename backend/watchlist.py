from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.dbstruct import db, user, movie, movielist

movies = Blueprint('movies', __name__)

# add movies to list
@movies.route('/add', methods=['POST'])
@jwt_required()
def add_movie():
    user_id = get_jwt_identity()
    current_user = user.query.get(user_id)
    
    data = request.get_json()
    movie_title = data.get('title')
    movie_poster = data.get('poster')
    movie_tmdb_id = data.get('tmdb_id')
    list_ids = data.get('list_ids', [])
    
    if not list_ids:
        return jsonify({'error': 'Select at least one list'}), 400
    
    # check if movie exists in list
    existing = movie.query.filter_by(userID=user_id, tmdbID=movie_tmdb_id).first()
    
    if existing:
        new_movie = existing
    else:
        new_movie = movie(
            title=movie_title,
            posterURL=movie_poster,
            tmdbID=movie_tmdb_id,
            userID=user_id
        )
        db.session.add(new_movie)
        db.session.commit()
    
    # add to selected list 
    added_to = []
    for list_id in list_ids:
        list_obj = movielist.query.get(list_id)
        if list_obj and list_obj.can_edit(current_user):
            if new_movie not in list_obj.movies:
                list_obj.movies.append(new_movie)
                added_to.append(list_obj.name)
    
    if added_to:
        db.session.commit()
        return jsonify({
            'message': f'Added {movie_title} to {", ".join(added_to)}'
        }), 200
    else:
        return jsonify({
            'message': f'{movie_title} is already in those lists'
        }), 200

# remove from list
@movies.route('/remove/<int:movie_id>', methods=['POST'])
@jwt_required()
def remove_movie(movie_id):
    user_id = get_jwt_identity()
    current_user = user.query.get(user_id)
    
    data = request.get_json()
    list_id = data.get('list_id')
    
    list_obj = movielist.query.get_or_404(list_id)
    
    if not list_obj.can_edit(current_user):
        return jsonify({'error': 'No permission to edit this list'}), 403
    
    movie_remove = movie.query.get_or_404(movie_id)
    
    if movie_remove in list_obj.movies:
        list_obj.movies.remove(movie_remove)
        db.session.commit()
        
        if not movie_remove.lists:
            db.session.delete(movie_remove)
            db.session.commit()
        
        return jsonify({
            'message': f'Removed {movie_remove.title} from {list_obj.name}'
        }), 200
    else:
        return jsonify({'error': 'Movie not found in list'}), 404

# fetch movies from user list
@movies.route('/my-movies', methods=['GET'])
@jwt_required()
def get_my_movies():
    user_id = get_jwt_identity()
    user_lists = movielist.query.filter_by(userID=user_id).all()
    
    return jsonify({
        'lists': [lst.to_dict(include_movies=True) for lst in user_lists]
    }), 200