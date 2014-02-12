from django.db import models

class Ingredient(models.Model):
   name = models.CharField(max_length=200, unique=True)
   def __unicode__(self):
      return self.name

class Recipe(models.Model):
   title              = models.CharField(max_length=200)
   ingredients        = models.ManyToManyField(Ingredient)
   yummlyId           = models.CharField(max_length=2000, unique=True)
   rating             = models.IntegerField()
   sourceDisplayName  = models.CharField(max_length=200)
   totalTimeInSeconds = models.FloatField()
   imageUrl90         = models.CharField(max_length=2000) # De facto max URL length

   def __unicode__(self):
      return self.title

   def getImageUrlBySize(self, size):
      return self.imageUrl90.replace('s90-c','s%s-c' % size)

   def getYummlyUrl(self):
      return "http://www.yummly.com/recipe/%s"%self.yummlyId

   def getIngredientsStr(self):
      return ", ".join([i.name for i in self.ingredients.all()])
