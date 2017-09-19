from django.contrib import admin
from eatinus.models import *

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    list_filter = ('user',)
    ordering = ('name',)
    search_fields = ('name',)

class RecipeCommentAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'commenter', 'date')
    list_filter = ('commenter',)
    ordering = ('date',)
    search_fields = ('recipe',)

class RecipeRatingAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'rater')
    list_filter = ('rater',)
    ordering = ('recipe',)
    search_fields = ('recipe',)

class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    list_filter = ('user',)
    ordering = ('name',)
    search_fields = ('name',)

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
           
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeComment, RecipeCommentAdmin)
admin.site.register(RecipeRating, RecipeRatingAdmin)
admin.site.register(RecipeRatingStatistic)
admin.site.register(Ingredient)

admin.site.register(Food, FoodAdmin)

admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(RestaurantRatingStatistic)
