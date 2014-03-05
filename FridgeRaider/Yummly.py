import requests # Basically a more Pythonic and modern adaptation of urllib2
import sys
import json
from FridgeRaider.models import Ingredient, Recipe
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

sys.path.append( '.' )

class Yummly:

	APP_ID  = '75f39ebf'
	APP_KEY = '8678ce0138b3cc250618be63722467d6'

	def getAllowedIngredients(self):
		res = requests.get("http://api.yummly.com/v1/api/metadata/ingredient",
								params={'_app_id':self.APP_ID,
												'_app_key': self.APP_KEY})

		JsonTxt = res.text[27:len(res.text)-2]
		ingredients = json.loads(JsonTxt)
		for entry in ingredients:
			self.addIngredient( entry['description'] )
		return ingredients

	def addIngredient(self, name):
		try:
				i = Ingredient(name=name)
				i.save()
		except IntegrityError:
			pass
		return i

	def addRecipes(self, recipes):
		numSaved = 0
		for r in recipes:
			if not r['ingredients']:
				continue
			recipe = Recipe(title=r['recipeName'],
											yummlyId = r['id'],
											rating = r['rating'],
											sourceDisplayName = r['sourceDisplayName'],
											totalTimeInSeconds = r['totalTimeInSeconds'],
											# imageUrl90 = r['imageUrlsBySize']['90'],
											num_ingredients = len(r['ingredients']))
			if 'imageUrlsBySize' in r:
				recipe.imageUrl90 = r['imageUrlsBySize']['90'],

			try:
				recipe.save()
				sys.stdout.write('.')
				numSaved += 1
			except IntegrityError:
				# 'yummlyId = "%s" already exists in the database' % r['id']
				sys.stdout.write('x')
				continue
			for ingredientName in r['ingredients']:
				try:
					ingredientObj = Ingredient.objects.get(name=ingredientName)
					recipe.ingredients.add(ingredientObj)
				except ObjectDoesNotExist:
					# print 'Adding "%s" to the ingredients table' % ingredientName
					ingredientObj = self.addIngredient( ingredientName )
					recipe.ingredients.add( ingredientObj )
		return numSaved
	def getRecipes(self, IngredientsList, numPerRequest = 10, start=0):
		res = self.search(IngredientsList, numPerRequest, start)
		matchCount = res['totalMatchCount']
		numSaved = self.addRecipes( res['matches'] )
		start += numPerRequest
		page = 1
		while start < matchCount:
			print '\nRESULTS FOR REQUEST #%d (start=%d out of total matches=%d)\n' % (page, start,matchCount)
			res = self.search(IngredientsList, numPerRequest, start)
			if res:
				numSaved += self.addRecipes( res['matches'] )
				print '\nTotal # Saved: %d' % numSaved
			start += numPerRequest
			page += 1

	def search(self, IngredientsList, maxResult = 12, start=0, attemptNum=1, requirePictures=False):
		requirePictures = str( requirePictures ).lower()

		res = requests.get( "http://api.yummly.com/v1/api/recipes",
								params={ 'q': IngredientsList,
													'requirePictures': requirePictures,
													'maxResult': maxResult,
													'start': start},
								headers={'X-Yummly-App-ID':self.APP_ID,
												 'X-Yummly-App-Key': self.APP_KEY})

		try:
			res = res.json()
		except (NameError,ValueError):
			if attemptNum > 3:
				return None
			res = self.search(IngredientsList, maxResult,start, attemptNum+1)
		return res

if __name__ == '__main__':
	y       = Yummly()
	y.getRecipes('', numPerRequest=1500,start=0)
	# res = y.search('',maxResult=10)

	# ingredients = y.getAllowedIngredients()