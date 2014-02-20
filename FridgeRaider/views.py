# All Django wants is that HttpResponse. Or an exception.
from FridgeRaider.models import Ingredient, Recipe
from FridgeRaider.Yummly import Yummly
from django.shortcuts import render_to_response
from math import ceil
import inflect

from time import time

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

   IngredientsList = []
   # Benchmark 1: 0.068 sec
   for i in qList:
      IngredientsList += getSimilarIngredients(i)

   # Make inital set of possible recipes
   tic = time()
   matches = Recipe.objects.filter(ingredients__in=IngredientsList).distinct()
   print 'Inital recipe set: %2.3f sec' % (time()-tic)

   # Filtration step #1: Remove all recipes with more ingredients than provided
   tic = time()
   # numBefore = len(matches)
   m = Recipe.objects.get(title="Fried Plantains")
   matches = matches.exclude(num_ingredients__gt = len(qList))
   # print "Filtration step 2: %d matches => %d matches" % (numBefore, len(matches))

   # Filter out recipes using ingredients not in IngredientsList
   tic = time()
   for m in matches:
      m.keep = True # Initally mark to keep
      for i in m.ingredients.all():
         if i not in IngredientsList:
            m.keep = False # mark to delete this recipe
            break
   print "Filtration step 2: %2.3f sec" % (time()-tic)
   return [m for m in matches if m.keep] # Keep only matches marked keep

def getSimilarIngredients( i ):
   '''Get all ingredient objects similar to ingredient with name i.
   For example if i=onion, return ingredient objects with titles [onion, onions, yellow onion, red onion, red onions, etc.]
   '''
   p = inflect.engine()
   IngredientsList = []
   IngredientsList += Ingredient.objects.filter(name__iendswith=i)
   IngredientsList += Ingredient.objects.filter(name__iendswith= p.plural(i) )
   return IngredientsList

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

