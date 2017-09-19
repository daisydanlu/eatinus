import os.path
from django.conf.urls.defaults import *
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings

from eatinus.views import *

admin.autodiscover()

site_static = os.path.join(os.path.dirname(__file__), 'static')

urlpatterns = patterns('',
  # Browsing
  (r'^$', main_page),
  (r'^user/(\w+)/$', user_page),
  
  (r'^recipe/latest/$', latest_recipes_page),
  
  (r'^recipe/(\d+)/$', recipe_page),
  (r'^recipes/$', recipe_site_page),
  
  (r'^food/(\d+)/$', food_page),
  (r'^food/$', food_site_page),

  (r'^restaurant/(\d+)/$', restaurant_page),
  (r'^restaurants/$', restaurant_site_page),
    
  # Session management
  (r'^login/$', 'django.contrib.auth.views.login'),
  (r'^logout/$', logout_page),
  (r'^register/$', register_page),
  (r'^register/success/$', TemplateView.as_view(template_name="registration/register_success.html")),
                       
  # Data update
  (r'^recipe/save/$', recipe_save_page),
  (r'^recipe/(\d+)/comment/$', recipe_comment_page),
  (r'^recipe/(\d+)/edit/$', recipe_edit_page),
  (r'^recipe/(\d+)/delete/$', recipe_delete_page),
  
  (r'^food/save/$', food_save_page),
  (r'^food/(\d+)/comment/$', food_comment_page),
  (r'^food/(\d+)/edit/$', food_edit_page),
  (r'^food/(\d+)/delete/$', food_delete_page),  
  
  (r'^restaurant/save/$', restaurant_save_page),
  (r'^restaurant/(\d+)/comment/$', restaurant_comment_page),
  #(r'^restaurant/(\d+)/edit/$', restaurant_edit_page),

  # AJAX
  (r'^recipe/(\d+)/rate/$', recipe_rate),
  (r'^food/(\d+)/rate/$', food_rate),
  (r'^restaurant/(\d+)/rate/$', restaurant_rate),
  
  # Search
  (r'^restaurant/search/$', restaurant_search_page),
  (r'^food/search/$', food_search_page),
  (r'^recipe/search/$', recipe_search_page),   
  
  # Fail
  (r'^failure/$', failure), 
  
  # Admin interface
  (r'^admin/', include(admin.site.urls)),

)

#if settings.DEBUG:
#  urlpatterns += patterns('',
#    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
#    {'document_root': settings.STATIC_ROOT}),
#                       
#    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
#    {'document_root': settings.MEDIA_ROOT}),
#  )
