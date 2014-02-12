# All Django wants is that HttpResponse. Or an exception.
from FridgeRaider.models import Ingredient, Recipe
from django.shortcuts import render_to_response

simpleSearch = True
def home(request):
   return render_to_response('home.html', {
      'Home': True,
      })

def search(request):
   IngredStr = request.GET.get('IngredientsList')
   if IngredStr:
      didSearch = True
      pageSize = 12
      IngredStrList = [i.strip() for i in IngredStr.split(',')]
      IngredientsList = []
      for i in IngredStrList:
         IngredientsList += Ingredient.objects.filter(name__icontains=i)
      print IngredientsList
      matches = Recipe.objects.filter(ingredients__in=IngredientsList)
      if len(matches) > pageSize:
         matches = matches[:pageSize]
      for m in matches:
         m.imageUrl = m.getImageUrlBySize(230)
   else:
      IngredientsList = None
      matches         = None
      didSearch       = False
   return render_to_response('search.html',{
      'RecipeSearch': True,
      'matches': matches,
      'didSearch': didSearch,
      })

