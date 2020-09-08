from rest_framework import serializers

from movies.models import User, Movie, User_Movie_Relationship

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'title', 'url', 'place', 'year', 'rating','star_cast')

class UserSerializer(serializers.ModelSerializer):
    movies = MovieSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'movies')

class UserMovieSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    movie = MovieSerializer(many=False, read_only=True)
    class Meta:
        model = User_Movie_Relationship
        fields = ('user', 'movie', 'is_watched')
