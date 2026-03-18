import os
import requests
from dotenv import load_dotenv

load_dotenv()

apiKey = os.getenv('TMDB_API_KEY')

baseURL = "https://api.themoviedb.org/3"

imageBaseURL = "https://image.tmdb.org/t/p"
posterSize = "w200" #other options: w92, w154, w200, w342, w500, original

def getPosterURL(posterPath):
    if posterPath:
        return f"{imageBaseURL}/{posterSize}{posterPath}"
    return None

def searchMovie(query):
    
    url = f"{baseURL}/search/movie"
    
    params = {
        "api_key": apiKey,
        "query": query,
        "language": "en-US",
        "page": 1
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        movies = data.get("results", [])
        for movie in movies:
            movie['posterURL'] = getPosterURL(movie.get('poster_path'))
        return movies
    else:
        print(f"Error: {response.status_code}")
        return []

def getMovie(movie_id):
    
    url = f"{baseURL}/movie/{movie_id}"
    
    params = {
        "api_key": apiKey,
        "language": "en-US"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        movie = response.json()
        movie['posterURL'] = getPosterURL(movie.get('poster_path'))
        return movie
    else:
        return None