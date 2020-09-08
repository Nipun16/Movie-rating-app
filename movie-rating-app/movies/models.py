# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

class Movie(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    place = models.CharField(max_length=10,null=True, blank=True)
    year = models.CharField(max_length=4,null=True, blank=True)
    star_cast = models.CharField(max_length=254,null=True, blank=True)
    rating = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    movies = models.ManyToManyField(Movie, through='User_Movie_Relationship')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class User_Movie_Relationship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    is_watched = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
