from django.db import models
from Securities.models import Security
import uuid
from decimal import *
# from django.core.exceptions import ValidationError

# Create your models here.
class Portfolio(models.Model):
	name = models.CharField(max_length=200)
	def __str__(self):
		return self.name



class Transaction(models.Model):
#	id = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)
	type = models.CharField(max_length=1)
	portfolio = models.ForeignKey(Portfolio)
	stock_id = models.ForeignKey(Security)
	date = models.DateField('date of transaction')
	nominal = models.DecimalField(max_digits=20, decimal_places=4)
	price = models.DecimalField(max_digits=20, decimal_places=4)
	cost = models.DecimalField(max_digits=20, decimal_places=4)
	total = models.DecimalField(max_digits=20, decimal_places=4)

	def __str__(self):
		return ';'.join((str(self.portfolio), self.type, str(self.stock_id), str(self.date), str(self.nominal), str(self.price), str(self.cost), str(self.total)))

	def get_invest_divest(self, portfolio, stock_id, from_date, to_date):
		in_divest = self.get_total(portfolio, 'b', from_date, to_date, stock_id)
		in_divest += self.get_total(portfolio, 's', from_date, to_date, stock_id)
		return in_divest
	def get_total_invest(self, portfolio, from_date, to_date):
		return self.get_total(portfolio, 'b', from_date, to_date)
	def get_total_divest(self, portfolio, from_date, to_date):
		return self.get_total(portfolio, 's', from_date, to_date)
	def get_total_dividend(self, portfolio, from_date, to_date):
		return self.get_total(portfolio, 'd', from_date, to_date)
	def get_total(self, portfolio, type, from_date, to_date, stock_id=None):
		if stock_id:
			return Transaction.objects.filter(portfolio__name=portfolio, type=type, date__range=[from_date, to_date], stock_id=stock_id)
		else:
			return Transaction.objects.filter(portfolio__name=portfolio, type=type, date__range=[from_date, to_date])



	def get_stocks_in_portfolio(self, portfolio, date):
		"""Get portfolio contents on that specific date, incl. all transactions from that date"""
		result = Transaction.objects.filter(portfolio__name=portfolio, type='b', date__lte=date)|Transaction.objects.filter(portfolio__name=portfolio, type='s', date__lte=date)
		stocks = {}
		for item in result:
			if item.id not in stocks.keys():
				stocks[item.id] = Decimal(0)
			stocks[item.id] = stocks[item.id] + item.nominal
		return stocks

	def get_total_for_portfolio(self, portfolio):
		"""NOT YET FINAL"""
		result = Transaction.objects.filter(portfolio__name=portfolio)
		aggregate = {}
		# self.data.c.execute('''SELECT name, SUM(nominal), SUM(cost), SUM(total) FROM transactions INNER JOIN stocks ON stocks.id = transactions.stock_id WHERE portfolio = ? GROUP BY stock_id''', (portfolio,)).fetchall()
# #		for item in result
		return result


#	def add(self, type, stock_id, date, nominal, price, cost, portfolio):
#		if stock_id != None:
#			if price < 0:
#				price = -1 * price
#			if cost < 0:
#				cost = -1 * cost
#			if type == 'b':
#				if nominal < 0:
#					nominal = -1 * nominal
#				total = -1 * price * nominal - cost
#			elif type == 's':
#				if nominal > 0:
#					nominal = -1 * nominal
#				total = -1 * price * nominal + cost
#			elif type == 'd':
#				if nominal != 0:
#					price = price * nominal
#					nominal = 0
#				cost = 0
#				total = price
#			result = self.data.c.execute('''SELECT id FROM transactions WHERE type = ? AND portfolio = ? AND stock_id = ? AND date = ? AND nominal = ? AND price = ? AND cost = ? AND total = ?''', (type, portfolio, stock_id, date, nominal, price, cost, total)).fetchall()
#			
#			if result == []:
#				self.data.c.execute('INSERT INTO transactions (id, type, portfolio, stock_id, date, nominal, price, cost, total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (uuid.uuid4(), type, portfolio, stock_id, date, nominal, price, cost, total))
#				self.money.update('settlement', date, total)
#				if type != 'd' and price != 0.0:
#					self.prices.update(self.secs.get_isin_id_from_stock_id(stock_id), date, price)
#				print('Cash addition ' + str(total))
#				return True
#			else:
#				print('Transaction already seems to exist: ' + str(result))
#				return False
#		else:
#			return False
# #		  self.data.commit()