from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from django.contrib import messages
from django.conf import settings
from django.utils import simplejson

from boto.s3.connection import S3Connection
from boto.s3.key import Key

import time
import os.path 
import math
from PIL import Image, ImageOps
from django.core.files import File
import StringIO

from eatinus.forms import *
from eatinus.models import *

ITEM_PER_PAGE = 10
UPLOAD_IMAGE_MAX_RES = 960 * 540 
IMAGE_THUMB_SIZE = (200, 150)

DEFAULT_RATING_SCORE = 3


def store_images_to_s3(imagestr, iamge_path, thumbstr, thumb_path):
  conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
  bucket = conn.get_bucket(settings.AWS_MEDIA_BUCKET_NAME) 
  k1 = Key(bucket)
  k1.key = iamge_path
  k1.set_contents_from_string(imagestr)
  k1.set_acl('public-read')
  k2 = Key(bucket)
  k2.key = thumb_path
  k2.set_contents_from_string(thumbstr)  
  k2.set_acl('public-read')
  
def register_page(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      user = User.objects.create_user(
        username=form.cleaned_data['username'],
        password=form.cleaned_data['password1'],
        email=form.cleaned_data['email']
      )
      return HttpResponseRedirect('/register/success/')
  else:
    form = RegistrationForm()

  variables = RequestContext(request, {
    'form': form
  })
  return render_to_response('registration/register.html', variables)
  
def main_page(request):
  popular_foods = Food.objects.order_by(
    '-date'
  )[:4]
  popular_recipes = Recipe.objects.order_by(
    '-date'
  )[:4]
  popular_restaurants = Restaurant.objects.order_by(
    '-date'
  )[:4]
  variables = RequestContext(request, {
    'foods': popular_foods,
    'recipes': popular_recipes,
    'restaurants': popular_restaurants
  }) 
  return render_to_response('main_page.html', variables)
  
  
def recipe_site_page(request):
  recipes = Recipe.objects.order_by(
    '-date'
  )[:20]
  form = RecipeSearchForm()
  variables = RequestContext(request, {
    'recipes': recipes,
    'form': form,    
  }) 
  return render_to_response('recipe_site_page.html', variables)  

def food_site_page(request):
  foods = Food.objects.order_by(
    '-date'
  )[:20]
  form = FoodSearchForm()
  variables = RequestContext(request, {
    'foods': foods,
    'form': form,    
  }) 
  return render_to_response('food_site_page.html', variables) 

def restaurant_site_page(request):
  restaurants = Restaurant.objects.order_by(
    '-date'
  )[:20]
  
  form = RestaurantSearchForm()
  
  variables = RequestContext(request, {
    'restaurants': restaurants,
    'form': form,
  }) 
  return render_to_response('restaurant_site_page.html', variables)   
  
def recipe_page(request, recipe_id):
  recipe = get_object_or_404(
    Recipe,
    pk=recipe_id
  )
  
  keyword = recipe.ingredient_set.all()[0].name
  similar_recipes = Recipe.objects.filter(ingredient__name__icontains=keyword)
  similar_recipes = similar_recipes.exclude(id=recipe.id)
  
  comments = RecipeComment.objects.filter(recipe=recipe).order_by('-date')
  form = RecipeCommentForm()
  statistic, created = RecipeRatingStatistic.objects.get_or_create(recipe=recipe)
  
  user_rating = None
  if request.user.is_authenticated():
    user_ratings = RecipeRating.objects.filter(recipe=recipe, rater=request.user)[:1]
    if bool(user_ratings):
      user_rating = user_ratings[0]
  
  variables = RequestContext(request, {
    'recipe': recipe,
    'similar_recipes': similar_recipes,
    'user_rating': user_rating,
    'is_author': recipe.user.username==request.user.username,
    'comments': comments,
    'form': form,
  })
  return render_to_response('recipe_page.html', variables)
  
def food_page(request, food_id):
  food = get_object_or_404(
    Food,
    pk=food_id
  )
  
  keyword = food.name.split()[0]
  similar_foods = Food.objects.filter(name__icontains=keyword)
  similar_foods = similar_foods.exclude(id=food.id)
  
  comments = FoodComment.objects.filter(food=food).order_by('-date')
  form = FoodCommentForm()
  statistic, created = FoodRatingStatistic.objects.get_or_create(food=food)
  
  user_rating = None
  if request.user.is_authenticated():
    user_ratings = FoodRating.objects.filter(food=food, rater=request.user)[:1]
    if bool(user_ratings):
      user_rating = user_ratings[0]    
  
  variables = RequestContext(request, {
    'food': food,
    'similar_foods': similar_foods,
    'user_rating': user_rating,
    'is_author': food.user.username==request.user.username,
    'comments': comments,
    'form': form,
  })
  return render_to_response('food_page.html', variables)
  
def restaurant_page(request, restaurant_id):
  restaurant = get_object_or_404(
    Restaurant,
    pk=restaurant_id
  )
  
  city = restaurant.address.city
  similar_restaurants = Restaurant.objects.filter(address__city__iexact=city)
  similar_restaurants = similar_restaurants.exclude(id=restaurant.id)
  similar_restaurants = similar_restaurants.order_by('statistic__total')
  
  comments = RestaurantComment.objects.filter(restaurant=restaurant).order_by('-date')
  form = RestaurantCommentForm()
  statistic, created = RestaurantRatingStatistic.objects.get_or_create(restaurant=restaurant)

  user_rating = None
  if request.user.is_authenticated():
    user_ratings = RestaurantRating.objects.filter(restaurant=restaurant, rater=request.user)[:1]
    if bool(user_ratings):
      user_rating = user_ratings[0]    
  
  variables = RequestContext(request, {
    'restaurant': restaurant,
    'similar_restaurants': similar_restaurants,
    'user_rating': user_rating,
    'comments': comments,
    'form': form,
  })
  return render_to_response('restaurant_page.html', variables)
  
      
def user_page(request, username):
  user = get_object_or_404(User, username=username)
  
  foods = user.food_set.order_by('-date')
  recipes = user.recipe_set.order_by('-date')
  food_num = len(foods)
  recipe_num = len(recipes)
  recent_shared_foods = foods[:5] 
  recent_shared_recipes = recipes[:5] 

  variables = RequestContext(request, {
    'recent_shared_recipes': recent_shared_recipes,
    'recent_shared_foods': recent_shared_foods,
        
    'username': username,
    'recipe_num': recipe_num,
    'food_num': food_num,
  })
  return render_to_response('user_page.html', variables)

#def _create_thumb(image, image_name):
#  thumb = ImageOps.fit(image, IMAGE_THUMB_SIZE, Image.ANTIALIAS, 0, (0.5, 0.5))
#  thumb_name = 'thumb_' + image_name
#  thumb_dir = os.path.join(settings.MEDIA_ROOT, 'thumbs')
#  thumb_path = os.path.join(thumb_dir, thumb_name)
#  thumb.save(thumb_path, 'JPEG', quality=75)
#  return thumb_name

def get_thumb(image):
  thumb = ImageOps.fit(image, IMAGE_THUMB_SIZE, Image.ANTIALIAS, 0, (0.5, 0.5))
  return thumb
  
def process_image_wrapper(request):
  f = request.FILES['image']   
  imagefile = StringIO.StringIO(f.read())
  upload_image = Image.open(imagefile)
  if upload_image.mode not in ('L', 'RGB'):
    upload_image = upload_image.convert('RGB')
  res = upload_image.size[0] * upload_image.size[1]
  if (res > UPLOAD_IMAGE_MAX_RES):
    resize_ratio = math.sqrt((float)(UPLOAD_IMAGE_MAX_RES) / res)
    size = ((int)(upload_image.size[0] * resize_ratio), (int)(upload_image.size[1] * resize_ratio))
    upload_image = upload_image.resize(size, Image.ANTIALIAS)  
  
  thumb = get_thumb(upload_image)
  timestamp = time.strftime('%Y-%m-%d', time.localtime(time.time()))
  today_path = os.path.join('images', timestamp)  

  upload_image_name = os.path.splitext(f.name)[0] + str(int(time.time()))
  upload_image_path = os.path.join(today_path, upload_image_name + '.jpg')  
  thumb_name = 'thumb_' + upload_image_name
  thumb_path = os.path.join(today_path, thumb_name + '.jpg') 
  
  buf= StringIO.StringIO()
  upload_image.save(buf, format='JPEG', quality=75)
  imagestr = buf.getvalue()
  
  thumbbuf= StringIO.StringIO()
  thumb.save(thumbbuf, format='JPEG', quality=75)
  thumbstr = thumbbuf.getvalue()  
  
  imagefile.close()
  buf.close()
  thumbbuf.close()
  
  store_images_to_s3(imagestr, upload_image_path, thumbstr, thumb_path) 
  return (upload_image_path, thumb_path)  
    
def _food_save(request, form):
  upload_image_path, thumb_path = process_image_wrapper(request)
  # Create recipe.
  food = Food(
    user=request.user,
    name=form.cleaned_data['name'],
    category=form.cleaned_data['category'],
    description=form.cleaned_data['description'],
    location=form.cleaned_data['location'],
  )
  food.save()
  food_image = FoodImage(
    food=food
  )  
      
  food_image.image = upload_image_path
  food_image.thumb = thumb_path
  food_image.save()
  return food
  
    
def _recipe_save(request, form):
  upload_image_path, thumb_path = process_image_wrapper(request) 
  
  # Create recipe.
  recipe = Recipe(
    user=request.user,
    name=form.cleaned_data['name'],
    category=form.cleaned_data['category'],    
    instruction=form.cleaned_data['instruction'],
    note=form.cleaned_data['note']
  )
  recipe.save()  
  # Create new ingredient list.
  ingredient_names = form.cleaned_data['ingredients'].split(',')
  for ingredient_name in ingredient_names:
    ingredient_name = ingredient_name.strip().lower()
    ingredient, dummy = Ingredient.objects.get_or_create(name=ingredient_name)
    recipe.ingredient_set.add(ingredient)
    
  recipe_image = RecipeImage(
    recipe=recipe
  )  
      
  recipe_image.image = upload_image_path
  recipe_image.thumb = thumb_path
  recipe_image.save()
  return recipe
  
  
def _restaurant_save(request, form):
  upload_image_path, thumb_path = process_image_wrapper(request)    
#  f = request.FILES['image']
#  timestamp = time.strftime('%Y-%m-%d', time.localtime(time.time()))
#  images_root = os.path.join(settings.MEDIA_ROOT, 'images')
#  today_dir = os.path.join(images_root, timestamp)  
#  if not os.path.isdir(today_dir):
#    os.mkdir(today_dir)
#  imagefile = StringIO.StringIO(f.read())
#  upload_image = Image.open(imagefile)
#  if upload_image.mode not in ('L', 'RGB'):
#    upload_image = upload_image.convert('RGB')
#  res = upload_image.size[0] * upload_image.size[1]
#  if (res > UPLOAD_IMAGE_MAX_RES):
#    resize_ratio = math.sqrt((float)(UPLOAD_IMAGE_MAX_RES) / res)
#    size = ((int)(upload_image.size[0] * resize_ratio), (int)(upload_image.size[1] * resize_ratio))
#    upload_image = upload_image.resize(size, Image.ANTIALIAS)
#  upload_image_name = str(int(time.time())) + f.name
#  upload_image_path = os.path.join(today_dir, upload_image_name)   
#  upload_image.save(upload_image_path, 'JPEG', quality=75)    
  
  # Create restaurant.
  address = Address(
    address1 = form.cleaned_data['address1'],
    address2 = form.cleaned_data['address2'],
    city = form.cleaned_data['city'],
    state = form.cleaned_data['state'],
    zip = form.cleaned_data['zip'],                
  )
  address.save()
  restaurant = Restaurant(
    name = form.cleaned_data['name'],
    description = form.cleaned_data['description'],
    category = form.cleaned_data['category'],
    address = address
  )
  restaurant.save()  
  
  restaurant_image = RestaurantImage (
    restaurant=restaurant
  )  
      
  restaurant_image.image = upload_image_path
  restaurant_image.thumb = thumb_path
  restaurant_image.save()
  return restaurant

    
    
@login_required
def food_save_page(request):
  if request.method == 'POST':
    form = FoodSaveForm(request.POST, request.FILES)
    if form.is_valid():
      food = _food_save(request, form)
      return HttpResponseRedirect('/food/%s/' % food.id)
    else:
      return HttpResponseRedirect('/failure/')

  else:
    form = FoodSaveForm()
    variables = RequestContext(request, {
      'form': form
    })
    return render_to_response('food_save_page.html', variables)


@login_required
def recipe_save_page(request):
  if request.method == 'POST':
    form = RecipeSaveForm(request.POST, request.FILES)
    if form.is_valid():
      recipe = _recipe_save(request, form)
      return HttpResponseRedirect('/recipe/%s/' % recipe.id)
    else:
      return HttpResponseRedirect('/failure/')

  else:
    form = RecipeSaveForm()
    variables = RequestContext(request, {
      'form': form
    })
    return render_to_response('recipe_save_page.html', variables)

@login_required
def restaurant_save_page(request):
  if request.method == 'POST':
    form = RestaurantSaveForm(request.POST, request.FILES)
    if form.is_valid():
      restaurant = _restaurant_save(request, form)
      return HttpResponseRedirect('/restaurant/%s/' % restaurant.id)
    else:
      return HttpResponseRedirect('/failure/')

  else:
    form = RestaurantSaveForm()
    variables = RequestContext(request, {
      'form': form
    })
    return render_to_response('restaurant_save_page.html', variables)

def _food_edit(food, request, form):

  food.user=request.user
  food.name=form.cleaned_data['name']
  food.category=form.cleaned_data['category']
  food.description=form.cleaned_data['description']
  food.location=form.cleaned_data['location']
  food.save()

def _recipe_edit(recipe, request, form):

  recipe.user=request.user
  recipe.name=form.cleaned_data['name']
  recipe.instruction=form.cleaned_data['instruction']
  recipe.note=form.cleaned_data['note']
  recipe.save()

  # Delete old ingredients of recipe.
  recipe.ingredient_set.clear()
  

  ingredient_names = form.cleaned_data['ingredients'].split(',')
  for ingredient_name in ingredient_names:
    ingredient_name = ingredient_name.strip().lower()
    ingredient, dummy = Ingredient.objects.get_or_create(name=ingredient_name)
    recipe.ingredient_set.add(ingredient)
 
@login_required
def food_edit_page(request, food_id):
  food = get_object_or_404(
    Food,
    pk=food_id
  )    
  if request.method == 'POST':
    form = FoodEditForm(request.POST)
    if form.is_valid():
      _food_edit(food, request, form)
      return HttpResponseRedirect('/food/{0}/'.format(food_id))
    else:
      return HttpResponseRedirect('/failure/')
  else:    
    form = FoodEditForm({
      'name': food.name,
      'category': food.category,
      'description': food.description,
      'location': food.location,
    })
  
    variables = RequestContext(request, {
      'form': form,
    })
    return render_to_response('food_edit_page.html', variables)
   
    
@login_required
def recipe_edit_page(request, recipe_id):
  recipe = get_object_or_404(
    Recipe,
    pk=recipe_id
  )    
  if request.method == 'POST':
    form = RecipeEditForm(request.POST)
    if form.is_valid():
      _recipe_edit(recipe, request, form)
      return HttpResponseRedirect('/recipe/{0}/'.format(recipe_id))
    else:
      return HttpResponseRedirect('/failure/')
  else:
    ingredients = Ingredient.objects.filter(recipe=recipe)
    text = ''
    for ingredient in ingredients:
      text += ingredient.name
      text += ', '
    text = text[:len(text)-2]
    
    form = RecipeEditForm({
      'name': recipe.name,
      'instruction': recipe.instruction,
      'note': recipe.note,
      'ingredients': text
    })
  
    variables = RequestContext(request, {
      'form': form,
    })
    return render_to_response('recipe_edit_page.html', variables)

@login_required
def food_delete_page(request, food_id):
  food = get_object_or_404(
    Food,
    pk=food_id
  )    
  food.delete()
  return HttpResponseRedirect('/user/{0}/'.format(request.user.username))
  
@login_required
def recipe_delete_page(request, recipe_id):
  recipe = get_object_or_404(
    Recipe,
    pk=recipe_id
  )    
  recipe.ingredient_set.clear()
  recipe.delete()
  return HttpResponseRedirect('/user/{0}/'.format(request.user.username))

@login_required
def food_rate(request, food_id):
  if request.method == 'POST':
    if 'rating' in request.POST:
      food = get_object_or_404(
        Food,
        pk=food_id
      )    
      result = FoodRating.objects.filter(food=food, rater=request.user)
      if not bool(result):
        food_rating = FoodRating(
          food = food,
          rater = request.user,
          score = int(request.POST['rating']),
        )
        food_rating.save()
      else:
        return HttpResponse('error.')
      statistic, created = FoodRatingStatistic.objects.get_or_create(food=food)
      statistic.total += int(request.POST['rating'])
      statistic.num += 1
      rating = float(statistic.total)/statistic.num
      statistic.average = rating
      statistic.save()
      json_dump = {
        'rating': rating,
      }
      data = simplejson.dumps(json_dump)
      return HttpResponse(data, mimetype='application/json')
  

@login_required
def restaurant_rate(request, restaurant_id):
  if request.method == 'POST':
    if 'rating' in request.POST:
      restaurant = get_object_or_404(
        Restaurant,
        pk=restaurant_id
      )    
      result = RestaurantRating.objects.filter(restaurant=restaurant, rater=request.user)
      if not bool(result):
        restaurant_rating = RestaurantRating(
          restaurant = restaurant,
          rater = request.user,
          score = int(request.POST['rating']),
        )
        restaurant_rating.save()
      else:
        return HttpResponse('error.')
      statistic, created = RestaurantRatingStatistic.objects.get_or_create(restaurant=restaurant)
      statistic.total += int(request.POST['rating'])
      statistic.num += 1
      rating = float(statistic.total)/statistic.num
      statistic.average = rating      
      statistic.save()
      json_dump = {
        'rating': rating,
      }
      data = simplejson.dumps(json_dump)
      return HttpResponse(data, mimetype='application/json')
  
      
@login_required
def recipe_rate(request, recipe_id):
  if request.method == 'POST':
    if 'rating' in request.POST:
      recipe = get_object_or_404(
        Recipe,
        pk=recipe_id
      )    
      result = RecipeRating.objects.filter(recipe=recipe, rater=request.user)
      if not bool(result):
        recipe_rating = RecipeRating(
          recipe = recipe,
          rater = request.user,
          score = int(request.POST['rating']),
        )
        recipe_rating.save()
      else:
        return HttpResponse('error.')
      statistic, created = RecipeRatingStatistic.objects.get_or_create(recipe=recipe)
      statistic.total += int(request.POST['rating'])
      statistic.num += 1
      rating = float(statistic.total)/statistic.num
      statistic.average = rating      
      statistic.save()
      json_dump = {
        'rating': rating,
      }
      data = simplejson.dumps(json_dump)
      return HttpResponse(data, mimetype='application/json')
        

@login_required
def food_comment_page(request, food_id):
  food = get_object_or_404(
    Food,
    pk=food_id
  )    
  if request.method == 'POST':
    form = FoodCommentForm(request.POST)
    if form.is_valid():
      food_comment = FoodComment(
        food = food,
        commenter = request.user,
        content = form.cleaned_data['content'],   
      )
      food_comment.save()
      return HttpResponseRedirect('/food/%s/' % food_id)
  return HttpResponseRedirect('/failure/')
    
@login_required
def recipe_comment_page(request, recipe_id):
  recipe = get_object_or_404(
    Recipe,
    pk=recipe_id
  )    
  if request.method == 'POST':
    form = RecipeCommentForm(request.POST)
    if form.is_valid():
      recipe_comment = RecipeComment(
        recipe = recipe,
        commenter = request.user,
        content = form.cleaned_data['content'],   
      )
      recipe_comment.save()
      return HttpResponseRedirect('/recipe/%s/' % recipe_id)
  return HttpResponseRedirect('/failure/')

@login_required
def restaurant_comment_page(request, restaurant_id):
  restaurant = get_object_or_404(
    Restaurant,
    pk=restaurant_id
  )    
  if request.method == 'POST':
    form = RestaurantCommentForm(request.POST)
    if form.is_valid():
      restaurant_comment = RestaurantComment(
        restaurant = restaurant,
        commenter = request.user,
        content = form.cleaned_data['content'],   
      )
      restaurant_comment.save()
      return HttpResponseRedirect('/restaurant/%s/' % restaurant_id)
  return HttpResponseRedirect('/failure/')

def food_search_page(request):
  foods = []
  keyword = ''
  category = ''
  if request.GET.has_key('keyword'):
    keyword = request.GET['keyword'].strip()
    if keyword:
      keywords = keyword.split()
      q = Q()
      for keyword in keywords:
        q = q & Q(name__icontains=keyword)

      foods = Food.objects.filter(q)

  if request.GET.has_key('category'):
    category = request.GET['category'].strip()
    if category:
      q = Q()
      q = q & Q(category__iexact=category)

      if foods:
          foods = foods.filter(q)
      else:
          foods = Food.objects.filter(q)

  foods = foods.order_by('-date')
  form = FoodSearchForm({'keyword' : keyword,
                         'category' : category,
  })      
  variables = RequestContext(request, {
    'foods': foods,
    'form': form,
  })
  return render_to_response('food_site_page.html', variables)
  
  
def restaurant_search_page(request):
  restaurants = []
  keyword = ''
  category = ''
  city = ''
  if request.GET.has_key('keyword'):
    keyword = request.GET['keyword'].strip()
    if keyword:
      keywords = keyword.split()
      q = Q()
      for keyword in keywords:
        q = q & Q(name__icontains=keyword)

      restaurants = Restaurant.objects.filter(q)

  if request.GET.has_key('category'):
    category = request.GET['category'].strip()
    if category:
      q = Q(category__iexact=category)

      if restaurants:
          restaurants = restaurants.filter(q)
      else:
          restaurants = Restaurant.objects.filter(q)

  if request.GET.has_key('city'):
    city = request.GET['city'].strip()
    if city:
      q = Q()
      q = q & Q(address__city__iexact=city)

      if restaurants:
          restaurants = restaurants.filter(q)
      else:
          restaurants = Restaurant.objects.filter(q)
          
  restaurants = restaurants.order_by('-date')          
  form = RestaurantSearchForm({'keyword' : keyword,
                               'category' : category,
                               'city' : city,                          
  })      
  variables = RequestContext(request, {
    'restaurants': restaurants,
    'form': form,
  })
  return render_to_response('restaurant_site_page.html', variables)
  
def recipe_search_page(request):
  recipes = []
  keyword = ''
  category = ''
  ingredient = ''
  if request.GET.has_key('keyword'):
    keyword = request.GET['keyword'].strip()
    if keyword:
      keywords = keyword.split()
      q = Q()
      for keyword in keywords:
        q = q & Q(name__icontains=keyword)

      recipes = Recipe.objects.filter(q)
          
  if request.GET.has_key('category'):
    category = request.GET['category'].strip()
    if category:
      qu = Q(category__iexact=category)
      if recipes:
          recipes = recipes.filter(qu)
      else:
          recipes = Recipe.objects.filter(qu)

  if request.GET.has_key('ingredient'):
    ingredient = request.GET['ingredient'].strip()
    if ingredient:
      ingredients = ingredient.split()
      q = Q()
      for ingredient in ingredients:
        q = q & Q(ingredient__name__icontains=ingredient)

      if recipes:
          recipes = recipes.filter(q)
      else:
          recipes = Recipe.objects.filter(q)
          
  recipes = recipes.order_by('-date')                 
  form = RecipeSearchForm({'keyword' : keyword,
                           'category' : category,
                           'ingredient' : ingredient,                           
  })      
  variables = RequestContext(request, {
    'recipes': recipes,
    'form': form,
  })
  return render_to_response('recipe_site_page.html', variables)
  
    
def search_page(request):
  form = SearchForm()
  recipes = []
  show_results = False

  if request.GET.has_key('query'):
    show_results = True
    query = request.GET['query'].strip()
    if query:
      keywords = query.split()
      q = Q()
      for keyword in keywords:
        q = q & Q(name__icontains=keyword)

      form = SearchForm({'query' : query})
      recipes = Recipe.objects.filter(q)[:10]

  variables = RequestContext(request, {
    'form': form,
    'recipes': recipes,
    'show_results': show_results,
    'show_user': True
  })
  return render_to_response('restaurant_site_page.html', variables)
  
  
def latest_recipes_page(request):
  today = datetime.today()
  yesterday = today - timedelta(1)

  latest_recipes = Recipe.objects.filter(
    date__gt=yesterday
  )
  latest_recipes = Recipe.order_by(
     '-date'
  )[:10]

  variables = RequestContext(request, {
    'latest_recipes': latest_recipes
  }) 
  return render_to_response('latest_recipes_page.html', variables)

@login_required
def logout_page(request):
  logout(request)
  return HttpResponseRedirect('/')


@login_required
def failure(request):
  variables = RequestContext(request, {

  }) 
  return render_to_response('failure.html', variables)
