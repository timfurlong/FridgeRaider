"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from FridgeRaider.views import getPossibleRecipes
from FridgeRaider.models import Recipe, Ingredient

class TestRecipeLookup(TestCase):
   def setUp(self):
      i1 = Ingredient.objects.create(name='plantains')
      i2 = Ingredient.objects.create(name='oil')
      r  = Recipe.objects.create(title="Fried Plantains",
                                 rating=0, totalTimeInSeconds=0, yummlyId=0)
      r.ingredients.add(i1, i2)

      i1 = Ingredient.objects.create(name="onion")
      i2 = Ingredient.objects.create(name="olive oil")
      r  = Recipe.objects.create(title="Caramelized Onions",
                                 rating=0, totalTimeInSeconds=0,yummlyId=1)
      r.ingredients.add(i1, i2)

   def test_two_given_ingredients(self):
      """
      Tests that providing a recipe list of "plantains, oil" should return at
      least the recipe Fried Plantains"
      """
      r = Recipe.objects.get(title="Fried Plantains")
      matches = getPossibleRecipes("plantains, oil")
      self.assertIn(r, matches)

   def test_three_given_ingredients(self):
      '''
      Tests that providing a recipe list of "plantains, oil, onion" still returns at least
      the recipe Fried Plantains
      '''
      r = Recipe.objects.get(title="Fried Plantains")
      self.assertIn(r, getPossibleRecipes("plantains, oil, onion") )

      # order should not matter
      self.assertIn(r, getPossibleRecipes("oil,plantains, onion") )

   def test_four_given_ingredients(self):
      '''
      Providing "onion, oil, plantains, olive oil" should return recipes Fried Plantains and Caramelized Onions
      '''
      matches = getPossibleRecipes("onion, oil, plantains, olive oil")

      r = Recipe.objects.get(title="Fried Plantains")
      self.assertIn(r, matches)

      r = Recipe.objects.get(title="Caramelized Onions")
      self.assertIn(r, matches)

   def test_case_insensitivity(self):
      '''
      tests to make sure ingredients searches are case insensitive.
      '''
      r = Recipe.objects.get(title="Fried Plantains")
      matches = getPossibleRecipes("PlAntAins, oIl")
      self.assertIn(r, matches)

