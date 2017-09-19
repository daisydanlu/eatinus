import re
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.localflavor.us.forms import USStateField
from django.contrib.localflavor.us.us_states import US_STATES
from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

FOOD_CATEGORIES = (
  ('', '--- Select Category ---'),                   
  ('Snack Food', 'Snack Food'),
  ('Staple Food', 'Staple Food'),
  ('Beverage', 'Beverage'),
  ('Seasoning', 'Seasoning'),
  ('Bakery', 'Bakery'),
  ('Other', 'Other'),  
)  
  
RESTAURANT_CATEGORIES = (
  ('', '--- Select Category ---'),                             
  ('Chinese', 'Chinese'),
  ('Western', 'Western'),
  ('Japanese', 'Japanese'),
  ('Thai', 'Thai'),
  ('Other', 'Other'),
)  
  
RECIPE_CATEGORIES = (
  ('', '--- Select Category ---'),                         
  ('Dish', 'Dish'),
  ('Wheaten', 'Wheaten'),
  ('Soup', 'Soup'),
  ('Other', 'Other'),
)    

class RegistrationForm(forms.Form):
  username = forms.CharField(label='Username', max_length=30)
  email = forms.EmailField(label='Email')
  password1 = forms.CharField(
    label='Password',
    widget=forms.PasswordInput()
  )
  password2 = forms.CharField(
    label='Password (Again)',
    widget=forms.PasswordInput()
  )
  def __init__(self, *args, **kwargs):
    self.helper = FormHelper()
    self.helper.form_class = 'col-lg-5'
    self.helper.form_method = 'post'
    self.helper.form_action = '.'
    self.helper.add_input(Submit('submit', 'Register'))
    super(RegistrationForm, self).__init__(*args, **kwargs)

  def clean_username(self):
    username = self.cleaned_data['username']
    if not re.search(r'^\w+$', username):
      raise forms.ValidationError('Username can only contain alphanumeric characters and the underscore.')
    try:
      User.objects.get(username=username)
    except:
      return username
    raise forms.ValidationError('Username is already taken.')

  def clean_password2(self):
    if 'password1' in self.cleaned_data:
      password1 = self.cleaned_data['password1']
      password2 = self.cleaned_data['password2']
      if password1 == password2:
        return password2
    raise forms.ValidationError('Passwords do not match.')


class RecipeSaveForm(forms.Form):  
  name = forms.CharField(
    label='Name',
    widget=forms.TextInput(attrs={'size': 36})
  )
  category = forms.ChoiceField(
    label='Category', choices = RECIPE_CATEGORIES,
  )    
  image = forms.ImageField(
    label='Select a file',
    help_text='10M maximum',
  )
  ingredients = forms.CharField(
    label='Ingredients',
    help_text='Example: chicken, onion',
    widget=forms.TextInput(attrs={'size': 48})
  )
  instruction = forms.CharField(
    label='Instruction',
    widget=forms.Textarea(attrs={'cols': 80}),
  )
  note = forms.CharField(
    label='Cooker\'s note (Optional)',
    required=False,
    widget=forms.Textarea(attrs={'rows': 3, 'cols': 80}),
  )
  
  def __init__(self, *args, **kwargs):
    self.helper = FormHelper()
    self.helper.form_class = 'col-lg-8'
    self.helper.form_method = 'post'
    self.helper.form_action = '/recipe/save/'
    self.helper.add_input(Submit('submit', 'Submit'))
    super(RecipeSaveForm, self).__init__(*args, **kwargs)

    
class RecipeEditForm(forms.Form):
  
  name = forms.CharField(
    label='Name',
    widget=forms.TextInput(attrs={'size': 36})
  )
  category = forms.ChoiceField(
    label='Category', choices = RECIPE_CATEGORIES,
  )    
  ingredients = forms.CharField(
    label='Ingredients',
    help_text='Example: chicken, onion',
    widget=forms.TextInput(attrs={'size': 48})
  )
  instruction = forms.CharField(
    label='Instruction',
    widget=forms.Textarea(attrs={'cols': 80}),
  )
  note = forms.CharField(
    label='Cooker\'s note (Optional)',
    required=False,
    widget=forms.Textarea(attrs={'rows': 3, 'cols': 80}),
  )
  
  def __init__(self, *args, **kwargs):
    self.helper = FormHelper()
    super(RecipeEditForm, self).__init__(*args, **kwargs)
    

class RecipeCommentForm(forms.Form):
  content = forms.CharField(
    label='Comment',
    widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}),
  )

class FoodSaveForm(forms.Form):
  
  name = forms.CharField(
    label='Name',
    widget=forms.TextInput(attrs={'size': 36})
  )
  image = forms.ImageField(
    label='Select a file',
    help_text='10M maximum',
  )
  category = forms.ChoiceField(
    label='Category', choices = FOOD_CATEGORIES,
  )  
  description = forms.CharField(
    label='Description',
    widget=forms.Textarea(attrs={'cols': 80}),
  )
  location = forms.CharField(
    label='Where to buy',
    widget=forms.TextInput(attrs={'cols': 80}),
  )
  
  def __init__(self, *args, **kwargs):
    self.helper = FormHelper()
    self.helper.form_class = 'col-lg-8'
    self.helper.form_method = 'post'
    self.helper.form_action = '/food/save/'
    self.helper.add_input(Submit('submit', 'Submit'))
    super(FoodSaveForm, self).__init__(*args, **kwargs)
    
    
class FoodEditForm(forms.Form):
  
  name = forms.CharField(
    label='Name',
    widget=forms.TextInput(attrs={'size': 36})
  )
  category = forms.ChoiceField(
    label='Category', choices = FOOD_CATEGORIES,
  )
  description = forms.CharField(
    label='Description',
    widget=forms.Textarea(attrs={'cols': 80}),
  )
  location = forms.CharField(
    label='Where to buy',
    widget=forms.Textarea(attrs={'size': 80}),
  )
  
  def __init__(self, *args, **kwargs):
    self.helper = FormHelper()
    super(FoodEditForm, self).__init__(*args, **kwargs)
    

class FoodCommentForm(forms.Form):
  content = forms.CharField(
    label='Comment',
    widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}),
  )
  


class RestaurantSaveForm(forms.Form):

  name = forms.CharField(
    label='Name',
    widget=forms.TextInput(attrs={'size': 36})
  )
  image = forms.ImageField(
    label='Add an image',
    help_text='10M maximum',
    required=False,
  )
  category = forms.ChoiceField(
    label='Category', choices = RESTAURANT_CATEGORIES,
  )  
  description = forms.CharField(
    label='Description',
    widget=forms.Textarea(attrs={'rows': 3, 'cols': 80}),
  )
  address1 = forms.CharField(
    label='Address1',
    widget=forms.TextInput(attrs={'size': 36}),
  )
  address2 = forms.CharField(
    label='Address2 (Optional)',
    widget=forms.TextInput(attrs={'size': 36}),
    required=False,
  )
  city = forms.CharField(
    label='City',
    widget=forms.TextInput(attrs={'size': 36}),
  )
  state = forms.ChoiceField(
    label='State',
    choices = US_STATES,
  )
  zip = forms.CharField(
    label='Zip Code (Optional)',
    widget=forms.TextInput(attrs={'size': 36}),
    required=False,
  )     
  def __init__(self, *args, **kwargs):
    self.helper = FormHelper()
    self.helper.form_class = 'col-lg-8'
    self.helper.form_method = 'post'
    self.helper.form_action = '/restaurant/save/'
    self.helper.add_input(Submit('submit', 'Submit'))
    super(RestaurantSaveForm, self).__init__(*args, **kwargs)
    
    
class RestaurantEditForm(forms.Form):
 
  name = forms.CharField(
    label='Name',
    widget=forms.TextInput(attrs={'size': 36})
  )
  category = forms.ChoiceField(
    label='Category', choices = RESTAURANT_CATEGORIES,
  )  
  description = forms.CharField(
    label='Description',
    widget=forms.Textarea(attrs={'rows': 3, 'cols': 80}),
  )
  address1 = forms.CharField(
    label='Address1',
    widget=forms.TextInput(attrs={'size': 36}),
  )
  address2 = forms.CharField(
    label='Address2 (Optional)',
    widget=forms.TextInput(attrs={'size': 36}),
    required=False,
  )
  city = forms.CharField(
    label='City',
    widget=forms.TextInput(attrs={'size': 36}),
  )
  state = forms.ChoiceField(
    label='State',
    choices = US_STATES,
  )
  zip = forms.CharField(
    label='Zip Code (Optional)',
    widget=forms.TextInput(attrs={'size': 36}),
    required=False,
  ) 
  
  def __init__(self, *args, **kwargs):
    self.helper = FormHelper()
    super(RestaurantEditForm, self).__init__(*args, **kwargs)
    

class RestaurantCommentForm(forms.Form):
  content = forms.CharField(
    label='Comment',
    widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}),
  )
  
class RestaurantSearchForm(forms.Form):
  keyword = forms.CharField(
    label='Keyword',
    required=False,    
  )       
  category = forms.ChoiceField(
    label='Category', choices = RESTAURANT_CATEGORIES,
    required=False,    
  )  
  city = forms.CharField(
    label='City',
    required=False,    
  )   
  def __init__(self, *args, **kwargs):
    self.helper = FormHelper()
    self.helper.form_method = 'get'
    self.helper.form_action = '/restaurant/search/'    
    self.helper.add_input(Submit('search', 'Search'))
    super(RestaurantSearchForm, self).__init__(*args, **kwargs)

class FoodSearchForm(forms.Form):
  keyword = forms.CharField(
    label='Keyword',
    required=False,     
  )       
  category = forms.ChoiceField(
    label='Category', choices = FOOD_CATEGORIES,
    required=False,     
  )  
  def __init__(self, *args, **kwargs):
    self.helper = FormHelper()
    self.helper.form_method = 'get'
    self.helper.form_action = '/food/search/'    
    self.helper.add_input(Submit('search', 'Search'))
    super(FoodSearchForm, self).__init__(*args, **kwargs)
    
class RecipeSearchForm(forms.Form):
  keyword = forms.CharField(
    label='Keyword',
    required=False,     
  )       
  category = forms.ChoiceField(
    label='Category', choices = RECIPE_CATEGORIES,
    required=False,     
  )  
  ingredient = forms.CharField(
    label='Ingredient',
    required=False,     
  )   
  def __init__(self, *args, **kwargs):
    self.helper = FormHelper()
    self.helper = FormHelper()
    self.helper.form_method = 'get'
    self.helper.form_action = '/recipe/search/'    
    self.helper.add_input(Submit('search', 'Search'))    
    super(RecipeSearchForm, self).__init__(*args, **kwargs)    