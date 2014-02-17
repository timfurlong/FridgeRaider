# All Django wants is that HttpResponse. Or an exception.
from FridgeRaider.models import Ingredient, Recipe
from FridgeRaider.Yummly import Yummly
from django.shortcuts import render_to_response
from math import ceil

simpleSearch = True
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
   IngredStr = request.GET.get('IngredientsList')
   if IngredStr:
      didSearch = True
      IngredStrList = [i.strip() for i in IngredStr.split(',')]
      IngredientsList = []
      for i in IngredStrList:
         IngredientsList += Ingredient.objects.filter(name__icontains=i)
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
      print page, start, maxPage, res['totalMatchCount']
      if start > res['totalMatchCount']:
         errorMsg = 'Page #%s exceeds the total number of results' % page
         infoMsg = None
         matches = []
      else:
         matches = res['matches']
         infoMsg = '%d results' % ( res['totalMatchCount'] )
         for r in matches:
            r['imageUrlsBySize']['230'] = r['imageUrlsBySize']['90'].replace('s90-c','s230-c')
            r['yummlyUrl'] = "http://www.yummly.com/recipe/%s"%r['id']
            r['ingredientsStr'] = ', '.join( r['ingredients'] )
         else:
            errorMsg = 'No recipes found for %s. Please try again.' % q
   else:
      matches = None
      errorMsg = None
      infoMsg = None
      maxPage = None
   return render_to_response('searchSimple.html',{
      'RecipeSearch' : True,
      'matches' : matches,
      'q': q,
      'errorMsg': errorMsg,
      'infoMsg': infoMsg,
      'page': page,
      'maxPage': maxPage,
      })