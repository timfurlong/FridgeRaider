from FridgeRaider.models import Ingredient, Recipe
from FridgeRaider.Yummly import Yummly
from django.shortcuts import render_to_response, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from math import ceil
import inflect

def home(request):
   return render_to_response('home.html', {
      'Home': True,
      })

def about(request):
   return render_to_response('about.html',{
      'About':True,
      })

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

def search(request):
   pageSize = 12

   # Get request
   q          = request.GET.get('q')
   extra      = request.GET.get('extra')
   minIngreds = request.GET.get('min')
   page       = request.GET.get('page')

   extra      = intConv(extra, 0)
   minIngreds = intConv(minIngreds, 0)

   context =  {'RecipeSearch': True,
                'q' : q,
                'extra' : extra,
                'min': minIngreds,} # initial template dictionary
   if q: # Search was made
      if 'existing' in request.GET:
         # Some ingredients have already been specified
         existing = request.GET.get('existing')
         if existing:
            q = existing + q
      qList = [i.strip() for i in q.split(',')]
      qList = [i for i in qList if i]
      qList = list( set(qList) ) # Remove repetition
      request.session['ingreds'] = qList
      context['qList'] = qList

      if len(qList) < 5:
         context['errorMsg'] = "Please provide at least 5 ingredients"
         return render(request, 'search.html', context)

      IngredientsList = getIngredientsList( qList )
      recipes = getPossibleRecipes(IngredientsList, extra, minIngreds)
      if recipes:
         paginator = Paginator(recipes, pageSize)
         try:
            matches = paginator.page(page)
         except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            matches = paginator.page(1)
         except EmptyPage:
            # If page is out of range, deliver last page of results.
            matches = paginator.page(paginator.num_pages)
         for m in matches:
            m.imageUrl = m.getImageUrlBySize(230)
            m.getIngredientOwnership( IngredientsList )
         context['matches'] = matches

         context['infoMsg'] = 'Results %d - %d' % ( matches.start_index(),
                                                         matches.end_index() )
         if matches.has_other_pages():
            context['infoMsg'] += ' (out of %d)' % paginator.count
   return render(request, 'search.html', context)

def getIngredientsList(q):
   if type(q) == list:
      qList = q
   else:
      qList = [i.strip() for i in q.split(',')]
      qList = [i for i in qList if i!='']
   IngredientsList = []
   for i in qList:
      IngredientsList += getSimilarIngredients(i)
   return IngredientsList

def getPossibleRecipes( IngredientsList, numExtraIngred=0,minIngreds=0 ):
   '''Get all recipes that use only the ingredients listed in q. q is a comma seperated list of ingredients.'''
   if IngredientsList:
      ingredIds = ["%d" % i.id for i in IngredientsList]
      ingredFmt = ("%s," * len(ingredIds))[:-1]
      subquery = """ SELECT * FROM "FridgeRaider_ingredient"
                     WHERE "FridgeRaider_ingredient"."id"
                     IN (%s)""" % ingredFmt
      query = """SELECT * FROM
                 (SELECT "FridgeRaider_recipe".id,
                     "FridgeRaider_recipe".title,
                     "FridgeRaider_recipe".num_ingredients,
                     count("matched_recipe_ingredients".ingredient_id) AS num_matched_ingredients
               FROM "FridgeRaider_recipe"
               LEFT JOIN
                  (SELECT "FridgeRaider_recipe_ingredients".id, recipe_id, ingredient_id
                  FROM "FridgeRaider_recipe_ingredients"
                  INNER JOIN (""" + subquery + """)
                     AS user_ingredients
                  ON user_ingredients.id = "FridgeRaider_recipe_ingredients".ingredient_id)
                  AS matched_recipe_ingredients
               ON "FridgeRaider_recipe".id = "matched_recipe_ingredients".recipe_id
               GROUP BY "FridgeRaider_recipe".id) AS match_table
            WHERE (num_matched_ingredients >= num_ingredients - %s)
               AND (num_matched_ingredients > (num_ingredients/2))
               AND (num_ingredients > %s);"""
      matches =  Recipe.objects.raw(query, ingredIds + [numExtraIngred, minIngreds] )
      return Recipe.objects.filter(pk__in = [m.id for m in matches])

def getSimilarIngredients( i ):
   '''Get all ingredient objects similar to ingredient with name i.
   For example if i=onion, return ingredient objects with titles [onion, onions, yellow onion, red onion, red onions, etc.]
   '''
   p = inflect.engine()
   IngredientsList = []
   IngredientsList += Ingredient.objects.filter(name__iendswith=i)
   IngredientsList += Ingredient.objects.filter(name__iendswith= p.plural(i) )
   return IngredientsList

# ============================================================================
# Small subroutines ==========================================================
# ============================================================================

def intConv(num, default):
   '''input a string to be converted to an integer.
   If the conversion is not valid, return default.'''
   try:
      return int(num)
   except ValueError:
      return default
   except TypeError:
      return default