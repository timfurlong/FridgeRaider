# All Django wants is that HttpResponse. Or an exception.
from FridgeRaider.models import Ingredient, Recipe
from FridgeRaider.Yummly import Yummly
from django.shortcuts import render_to_response
from math import ceil


def home(request):
   return render_to_response('home.html', {
      'Home': True,
      })

def about(request):
   return render_to_response('about.html',{
      'About':True,
      })

def search(request):
   pageSize = 12
   q = request.GET.get('q')
   if q: # Search was made
      matches = getPossibleRecipes(q)
      if len(matches) > pageSize:
         matches = matches[:pageSize]
      for m in matches:
         m.imageUrl = m.getImageUrlBySize(230)
   else:
      matches         = None
   return render_to_response('search.html',{
      'RecipeSearch': True,
      'matches': matches,
      'q': q,
      })

def getPossibleRecipes( q ):
   '''Get all recipes that use only the ingredients listed in q. q is a comma seperated list of ingredients.'''
   qList = [i.strip() for i in q.split(',')]
   # Gather ingredients list
   IngredientsList = []
   for i in qList:
      IngredientsList += Ingredient.objects.filter(name__iexact=i)

   # Make inital set of possible recipes
   matches = Recipe.objects.filter(ingredients__in=IngredientsList).distinct()
   # Filter out recipes using ingredients not in IngredientsList
   for m in matches:
      m.keep = True # Initally mark to keep
      for i in m.ingredients.all():
         if i not in IngredientsList:
            m.keep = False # mark to delete this recipe
            break
   return [m for m in matches if m.keep] # Keep only matches marked keep


def searchSimple(request):
   pageSize = 12
   q        = request.GET.get('IngredientsList')
   page     = request.GET.get('page')
   if not page:
      page = '1'
   if q:
      start = (int(page)-1)*pageSize
      res = Yummly().search(q, maxResult=pageSize, start=start)
      maxPage = ceil( float(res['totalMatchCount']) / float(pageSize) )
      if start > res['totalMatchCount']:
         errorMsg    = 'Page #%s exceeds the total number of results' % page
         infoMsg     = None
         matches     = []
      else:
         matches = res['matches']
         infoMsg = 'Results %d - %d' % ( start+1, start+1+pageSize )
         for r in matches:
            r['imageUrlsBySize']['230'] = r['imageUrlsBySize']['90'].replace('s90-c','s230-c')
            r['yummlyUrl'] = "http://www.yummly.com/recipe/%s"%r['id']
            r['ingredientsStr'] = ', '.join( r['ingredients'] )
         else:
            errorMsg = 'No recipes found for %s. Please try again.' % q
   else:
      matches     = None
      errorMsg    = None
      infoMsg     = None
      maxPage     = None
   return render_to_response('searchSimple.html',{
      'RecipeSearch' : True,
      'matches' : matches,
      'q': q,
      'errorMsg': errorMsg,
      'infoMsg': infoMsg,
      'page': page,
      'maxPage': maxPage,
      })

