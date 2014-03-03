"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from FridgeRaider.views import getPossibleRecipes, getIngredientsList
from FridgeRaider.models import Recipe, Ingredient

class TestRecipeLookup(TestCase):
   def setUp(self):
      testRecipes = {
         'Caramelized Onions': ['onion', 'olive oil'],
         'Fried Plantains': ['plantains', 'oil'],
      }
      for k,v in testRecipes.items():
         r = Recipe.objects.create(title=k,
                                   rating=0, totalTimeInSeconds=0, yummlyId=k,
                                   num_ingredients=len(v))
         for i in v:
            r.ingredients.add( Ingredient.objects.create(name=i) )

   def test_two_given_ingredients(self):
      """
      Tests that providing a recipe list of "plantains, oil" should return at
      least the recipe Fried Plantains"
      """
      r = Recipe.objects.get(title="Fried Plantains")
      ingreds = getIngredientsList("plantains, oil")
      matches = getPossibleRecipes( ingreds )
      self.assertIn(r, matches)

   def test_three_given_ingredients(self):
      '''
      Tests that providing a recipe list of "plantains, oil, onion" still returns at least
      the recipe Fried Plantains
      '''
      r = Recipe.objects.get(title="Fried Plantains")
      ingreds = getIngredientsList( "plantains, oil, onion" )
      self.assertIn(r, getPossibleRecipes(ingreds) )

      # order should not matter
      ingreds = getIngredientsList( "oil,plantains, onion" )
      self.assertIn(r, getPossibleRecipes(ingreds) )

   def test_four_given_ingredients(self):
      '''
      Providing "onion, oil, plantains, olive oil" should return recipes Fried Plantains and Caramelized Onions
      '''
      ingreds = getIngredientsList( "onion, oil, plantains, olive oil" )
      matches = getPossibleRecipes( ingreds )

      r = Recipe.objects.get(title="Fried Plantains")
      self.assertIn(r, matches)

      r = Recipe.objects.get(title="Caramelized Onions")
      self.assertIn(r, matches)

   def test_case_insensitivity(self):
      '''
      tests to make sure ingredients searches are case insensitive.
      '''
      r = Recipe.objects.get(title="Fried Plantains")
      ingreds = getIngredientsList( "PlAntAins, oIl" )
      matches = getPossibleRecipes(ingreds)
      self.assertIn(r, matches)

   def test_plurality_insensitivity(self):
      '''
      plurality of the query string should be ignored.
      '''
      r = Recipe.objects.get(title="Fried Plantains")
      ingreds = getIngredientsList( "plantain, oil" )
      matches = getPossibleRecipes(ingreds) # rather than plantains
      self.assertIn(r, matches)

   def test_same_ingredient_ending(self):
      '''
      Ingredients of the same ending should be considered matches.
      '''
      r = Recipe.objects.get(title="Caramelized Onions")
      ingreds = getIngredientsList( 'oil, onion' )
      matches = getPossibleRecipes(ingreds) # rather than olive oil
      self.assertIn(r, matches)