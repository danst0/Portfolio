from django.db import models

# Create your models here.


class Security(models.Model):
	name = models.CharField(max_length=200)
	aliases = models.DateTimeField('date published')
	isin_id = models.CharField(max_length=10)
	yahoo_id = models.CharField(max_length=10)
	type = models.CharField(max_length=10)

	def __str__(self):
		return (self.name, self.aliases, self.isin_id, self.yahoo_id, self.type)

class Portfolio(models.Model):
	name = models.CharField(max_length=200)
	def __str__(self):
		return self.name

class Transaction(models.Model):
	type = models.CharField(max_length=1)
	portfolio = models.ForeignKey(Portfolio)
	stock_id = models.ForeignKey(Security)
	date = models.DateField('date of transaction')
	nominal = models.DecimalField(max_digits=20, decimal_places=4)
	price = models.DecimalField(max_digits=20, decimal_places=4)
	cost = models.DecimalField(max_digits=20, decimal_places=4)
	total = models.DecimalField(max_digits=20, decimal_places=4)

	def __str__(self):
		return self.portfolio, self.type, self.stock_id, self.date, self.nominal, self.price, self.cost, self.total



class Price(models.Model):
	stock_id = models.ForeignKey(Security)
	date = models.DateField('date of price')
	price = models.DecimalField(max_digits=20, decimal_places=4)	   
	def __str__(self):
		return self.stock_id, self.date, self.price

class Money(models.Model):
	date = models.DateField('date of income/total')
	type = models.CharField(max_length=10)
	value = models.DecimalField(max_digits=20, decimal_places=4)			 

	def __str__(self):
		return self.type, self.date, self.value