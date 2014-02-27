from django.db import models

class Ingredient(models.Model):
   name = models.CharField(max_length=200, unique=True, db_index=True)
   def __unicode__(self):
      return self.name

class Recipe(models.Model):
   title              = models.CharField(max_length=200, db_index=True)
   ingredients        = models.ManyToManyField(Ingredient, db_index=True)
   yummlyId           = models.CharField(max_length=2000, unique=True)
   rating             = models.IntegerField()
   sourceDisplayName  = models.CharField(max_length=200)
   totalTimeInSeconds = models.FloatField()
   imageUrl90         = models.CharField(max_length=2000) # De facto max URL length
   num_ingredients    = models.IntegerField()

   def __unicode__(self):
      return self.title

   def getImageUrlBySize(self, size):
      return self.imageUrl90.replace('s90-c','s%s-c' % size)

   def getYummlyUrl(self):
      return "http://www.yummly.com/recipe/external/%s"%self.yummlyId

   def getIngredientsStr(self):
      return ", ".join([i.name for i in self.ingredients.all()])

   def getIngredientOwnership(self, ownedIngredients):
      has, needs = [], []
      for ingred in self.ingredients.all():
         if ingred in ownedIngredients:
            has.append( ingred )
         else:
            needs.append( ingred )
      self.has, self.needs = has, needs

   def hasIngredientStr(self):
      return ", ".join([i.name for i in self.has])

   def needsIngredientStr(self):
      return ", ".join([i.name for i in self.needs])