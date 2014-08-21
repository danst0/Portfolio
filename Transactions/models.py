from django.db import models

# Create your models here.
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
		return (self.portfolio, self.type, self.stock_id, self.date, self.nominal, self.price, self.cost, self.total).join(';')

