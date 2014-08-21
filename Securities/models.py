
from django.db import models

# Create your models here.
class Security(models.Model):
	name = models.CharField(max_length=200)
	aliases = models.CharField(max_length=400)
	isin_id = models.CharField(max_length=10)
	yahoo_id = models.CharField(max_length=10)
	type = models.CharField(max_length=10)

	search_fields = ['name', 'aliases']

	def set_aliases(self, x):
    		if x and not isinstance(x, str): 
    			self.aliases = ':::'.join(x)
    		else:
    			self.aliases = ''
	def get_aliases(self):
		if self.aliases == '':
			return []
		else:
        		return self.aliases.split(':::')
	def __str__(self):
		return self.name#, self.aliases, self.isin_id, self.yahoo_id, self.type))



class Price(models.Model):
	stock_id = models.ForeignKey(Security)
	date = models.DateField('date of price')
	price = models.DecimalField(max_digits=20, decimal_places=4)	   
	def __str__(self):
		return self.stock_id, self.date, self.price
