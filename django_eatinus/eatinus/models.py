from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.contrib import admin
from django.contrib.localflavor.us.models import USStateField
from django.contrib.localflavor.us.us_states import US_STATES
import settings

FOOD_CATEGORIES = (
  ('Snack Food', 'Snack Food'),
  ('Staple Food', 'Staple Food'),
  ('Beverage', 'Beverage'),
  ('Seasoning', 'Seasoning'),
  ('Bakery', 'Bakery'),
  ('Other', 'Other'),  
)  
  
RESTAURANT_CATEGORIES = (
  ('Chinese', 'Chinese'),
  ('Western', 'Western'),
  ('Japanese', 'Japanese'),
  ('Thai', 'Thai'),
  ('Other', 'Other'),
)  
  
RECIPE_CATEGORIES = (
  ('Dish', 'Dish'),
  ('Wheaten', 'Wheaten'),
  ('Soup', 'Soup'),
  ('Other', 'Other'),
)      
  
class Recipe(models.Model):
  user = models.ForeignKey(User)
  name = models.CharField(max_length=256)
  category = models.CharField(max_length=20, choices = RECIPE_CATEGORIES)  
  instruction = models.CharField(max_length=2046)
  note = models.CharField(max_length=256,blank=True)
  date = models.DateTimeField(auto_now_add=True)
  
  def __unicode__(self):
    return '%s, %s' % (self.name, self.user.username,)

class RecipeImage(models.Model):
  recipe = models.ForeignKey(Recipe, related_name='images')
  image = models.ImageField(upload_to='images/%Y')
  thumb = models.URLField()
  index = models.IntegerField(default=1)

class Ingredient(models.Model):
  name = models.CharField(max_length=64, unique=True)
  recipe = models.ManyToManyField(Recipe)

  def __unicode__(self):
    return self.name

class RecipeRatingStatistic(models.Model):
  recipe = models.ForeignKey(Recipe, related_name='statistic', unique=True)
  total = models.IntegerField(default=3)
  num = models.IntegerField(default=1)
  average = models.FloatField(default=3.0)    

class RecipeRating(models.Model):
  recipe = models.ForeignKey(Recipe)
  rater = models.ForeignKey(User)
  score = models.IntegerField()
  date = models.DateTimeField(auto_now_add=True)
  
class RecipeComment(models.Model):
  recipe = models.ForeignKey(Recipe)
  commenter = models.ForeignKey(User)
  content = models.CharField(max_length=2046)
  date = models.DateTimeField(auto_now_add=True)


class Food(models.Model): 
  user = models.ForeignKey(User)
  name = models.CharField(max_length=256)
  category = models.CharField(max_length=20, choices = FOOD_CATEGORIES)
  description = models.CharField(max_length=2046)
  location = models.CharField(max_length=256)
  date = models.DateTimeField(auto_now_add=True)
  
  def __unicode__(self):
    return '%s, %s' % (self.name, self.user.username,)

class FoodImage(models.Model):
  food = models.ForeignKey(Food, related_name='images')
  image = models.ImageField(upload_to='images/%Y')
  thumb = models.URLField()
  index = models.IntegerField(default=1)  
  
  
class FoodRatingStatistic(models.Model):
  food = models.ForeignKey(Food, related_name='statistic', unique=True)
  total = models.IntegerField(default=3)
  num = models.IntegerField(default=1)
  average = models.FloatField(default=3.0)    

class FoodRating(models.Model):
  food = models.ForeignKey(Food)
  rater = models.ForeignKey(User)
  score = models.IntegerField()
  date = models.DateTimeField(auto_now_add=True)
  
class FoodComment(models.Model):
  food = models.ForeignKey(Food)
  commenter = models.ForeignKey(User)
  content = models.CharField(max_length=2046)
  date = models.DateTimeField(auto_now_add=True)
  
  
class Address(models.Model):
  address1 = models.CharField(max_length=128)
  address2 = models.CharField(max_length=128, blank=True)

  city = models.CharField(max_length=64)
  state = USStateField(choices = US_STATES)
  zip = models.CharField(max_length=5, blank=True)
  country = models.CharField(max_length=24, default= 'United States') 
  
class Coordinate(models.Model):
  address = models.ForeignKey(Address)
  latitude = models.CharField(max_length=128)
  longitude = models.CharField(max_length=128, blank=True)
   
class Restaurant(models.Model):  
  name = models.CharField(max_length=256)
  category = models.CharField(max_length=20, choices = RESTAURANT_CATEGORIES)
  description = models.CharField(max_length=256)
  date = models.DateTimeField(auto_now_add=True)
  address = models.ForeignKey(Address)
  
  def __unicode__(self):
    return '%s' % (self.name)
    
class RestaurantImage(models.Model):
  restaurant = models.ForeignKey(Restaurant, related_name='images')
  image = models.ImageField(upload_to='images/%Y')
  thumb = models.URLField()
  index = models.IntegerField(default=1)  
  
class RestaurantRatingStatistic(models.Model):
  restaurant = models.ForeignKey(Restaurant, related_name='statistic', unique=True)
  total = models.IntegerField(default=3)
  num = models.IntegerField(default=1)
  average = models.FloatField(default=3.0)  

class RestaurantRating(models.Model):
  restaurant = models.ForeignKey(Restaurant)
  rater = models.ForeignKey(User)
  score = models.IntegerField()
  date = models.DateTimeField(auto_now_add=True)
  
class RestaurantComment(models.Model):
  restaurant = models.ForeignKey(Restaurant)
  commenter = models.ForeignKey(User)
  content = models.CharField(max_length=2046)
  date = models.DateTimeField(auto_now_add=True)
  
#Favorites feature
class RestaurantFavorite(models.Model):
  restaurant = models.ForeignKey(Restaurant)
  user = models.ForeignKey(User)
  
class FoodFavorite(models.Model):
  food = models.ForeignKey(Food)
  user = models.ForeignKey(User)
  
class RecipeFavorite(models.Model):
  recipe = models.ForeignKey(Recipe)
  user = models.ForeignKey(User)
  