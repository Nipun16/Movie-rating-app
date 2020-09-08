import re
import logging
from .models import Movie

logger = logging.getLogger(__name__)

def fetchData(movies, crew, ratings, votes, links):
    imdb = []

    for index in range(0, len(movies)):
        movie_string = movies[index].get_text()
        movie = (' '.join(movie_string.split()).replace('.', ''))
        movie_title = movie[len(str(index))+1:-7]
        year = re.search('\((.*?)\)', movie_string).group(1)
        place = movie[:len(str(index))-(len(movie))]
        data = {"movie_title": movie_title,
                "year": year,
                "place": place,
                "star_cast": crew[index],
                "rating": ratings[index],
                "vote": votes[index],
                "link": links[index]
                }
        imdb.append(data)
        
    return imdb, movie

def saveMovie(imdb, movie):
    for item in imdb:
        movie = Movie.objects.filter(title=item['movie_title']).first()

        if not movie:
            movie = Movie()

        movie.title = item['movie_title']
        movie.url = item['link']
        movie.place = item['place']
        movie.year = item['year']
        movie.star_cast = item['star_cast']
        movie.rating = item['rating']
        movie.save()

def populate_movies(payload, user, is_watched):
    for movie in payload['movies']:
        movie = Movie.objects.get(id=movie['id'])
        user.movies.add(movie, through_defaults={'is_watched' : is_watched})   

def get_is_watched_flag(payload):
    is_watched = False
    
    if payload['is_watched']:
        is_watched = payload['is_watched']

    return is_watched

def remove_movies(payload, user):
    for movie in payload['movies']:
        movie = Movie.objects.get(id=movie['id'])
        user.movies.remove(movie)
