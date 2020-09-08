# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
from datetime import date
from decimal import Decimal
from rest_framework import filters
from django.conf import settings

from click.core import Argument
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Movie, User, User_Movie_Relationship
from .serializers import MovieSerializer, UserSerializer, UserMovieSerializer
from .utils import fetchData, saveMovie, get_is_watched_flag, populate_movies, remove_movies

from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)

class MovieListView(generics.ListAPIView):
    search_fields = ['title']
    filter_backends = (filters.SearchFilter,)
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

@api_view(["POST"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def scrap_movies(request):
    try:
        logger.debug('Received request to scrap movies by user id : %s ' % request.user.id)
            
        url = getattr(settings, 'SCRAPPER_URL', None) 
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        movies = soup.select('td.titleColumn')
        links = [a.attrs.get('href') for a in soup.select('td.titleColumn a')]
        crew = [a.attrs.get('title') for a in soup.select('td.titleColumn a')]
        ratings = [b.attrs.get('data-value') for b in soup.select('td.posterColumn span[name=ir]')]
        votes = [b.attrs.get('data-value') for b in soup.select('td.ratingColumn strong')]

        imdb, movie = fetchData(movies, crew, ratings, votes, links)

        saveMovie(imdb, movie)

        return JsonResponse({'msg':'movies scrapped successfully'}, safe=False, status=status.HTTP_201_CREATED)
    
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as Argument:
        logger.error("Exception caught while scraping movies for user : %s" % Argument)
        return JsonResponse({'error': 'Something terrible went wrong'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def get_movie_by_id(request, movie_id):
    try:
        logger.debug('Received request to get movie by id: %s ' % movie_id)
            
        movie = Movie.objects.get(id=movie_id)
        serializer = MovieSerializer(movie)

        return JsonResponse({'movie': serializer.data}, safe=False, status=status.HTTP_200_OK)
    
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as Argument:
        logger.error("Exception caught while fetching to watch movies for user : %s" % Argument)
        return JsonResponse({'error': 'Something terrible went wrong'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def get_to_watch_movies(request):
    try:
        logger.debug('Received request to fetch to watch movies for user id: %s ' % request.user.id)
            
        movies = list(User_Movie_Relationship.objects.filter(user=request.user, is_watched=False).values().distinct())
       
        if len(movies) == 0:
            return JsonResponse({'msg': 'No to watch movies found for user'}, safe=False, status=status.HTTP_204_NO_CONTENT)
        else:
            return JsonResponse({'movies': movies}, safe=False, status=status.HTTP_200_OK)
    
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as Argument:
        logger.error("Exception caught while fetching to watch movies for user : %s" % Argument)
        return JsonResponse({'error': 'Something terrible went wrong'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def get_watched_movies(request):
    try:
        logger.debug('Received request to fetch movies for user id: %s ' % request.user.id)
            
        movies = list(User_Movie_Relationship.objects.filter(user=request.user, is_watched=True).values().distinct())
       
        if len(movies) == 0:
            return JsonResponse({'msg': 'No watched movies found for user'}, safe=False, status=status.HTTP_204_NO_CONTENT)
        else:
            return JsonResponse({'movies': movies}, safe=False, status=status.HTTP_200_OK)
    
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as Argument:
        logger.error("Exception caught while fetching watched movies for user : %s" % Argument)
        return JsonResponse({'error': 'Something terrible went wrong'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def add_movie(request):
    payload = json.loads(request.body)
    try:
        logger.debug('Received request to add movie to watch list for user id: %s ' % request.user.id)
        
        if not 'movies' in payload or len(payload['movies']) == 0:
            return JsonResponse({'error': 'No movies found to be added'}, safe=False, status=status.HTTP_417_EXPECTATION_FAILED)
        
        user = User.objects.get(id=request.user.id)
        
        is_watched = get_is_watched_flag(payload)

        logger.debug(is_watched)
        populate_movies(payload, user, is_watched)

        serializer = UserSerializer(user)
        return JsonResponse({'movie': serializer.data}, safe=False, status=status.HTTP_200_OK)
    
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as Argument:
        logger.error("Exception caught while fetching movies for user : %s" % Argument)

@api_view(["DELETE"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def delete_movie(request):
    payload = json.loads(request.body)
    try:
        logger.debug('Received request to remove movie from to watch list for user id: %s ' % request.user.id)
        
        if not 'movies' in payload or len(payload['movies']) == 0:
            return JsonResponse({'error': 'No movies found to be removed'}, safe=False, status=status.HTTP_417_EXPECTATION_FAILED)
        
        user = User.objects.get(id=request.user.id)

        remove_movies(payload, user)

        serializer = UserSerializer(user)
        return JsonResponse({'movie': serializer.data}, safe=False, status=status.HTTP_200_OK)
    
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as Argument:
        logger.error("Exception caught while removing movies for user : %s" % Argument)
