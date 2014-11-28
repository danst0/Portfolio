from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_delete
from django.dispatch import receiver

from transactions.models import Transaction, Price
from money.models import Money

# Create your models here.


class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')
    user = models.ForeignKey(User, null=True, default=None)
    imported = models.BooleanField(default=False)

    def update(self):
        print('-'*10 + 'Start import' + '-'*10)
        print(self.docfile.name)
        # File based
        feedback_outbank = self.import_outbank(self.docfile.path)
        if not feedback_outbank:
            feedback_outbank = []
        feedback_cortalconsors = self.import_cortalconsors_quotes(self.docfile.path)
        if not feedback_cortalconsors:
            feedback_cortalconsors = []
        feedback_pdfs = self.update_pdfs(self.docfile.path)
        if not feedback_pdfs:
            feedback_pdfs = []


        ### Internet based
        #feedback_frankfurt = self.update_stocks_boerse_frankfurt()
        #if not feedback_frankfurt:
        feedback_frankfurt = []
        #feedback_yahoo = self.import_historic_quotes()
        #if not feedback_yahoo:
        feedback_yahoo = []


        prices = feedback_frankfurt + feedback_cortalconsors + feedback_yahoo + feedback_pdfs['prices']
        print(prices)
        transactions = feedback_pdfs['transactions']
        print(transactions)
        money = feedback_outbank
        print(money)
        # return render(request, 'import_all.html', {'block_title': 'Update Database',
        #                                            'prices': prices, 'transactions': transactions, 'money': money})



    def update_pdfs(self, path):
        # import pdb; pdb.set_trace()
        t = Transaction()
        result = t.import_sources(path)
        return result

    def import_outbank(self, path):
        # import pdb; pdb.set_trace()
        m = Money()
        result = m.import_outbank(path)
        return result

    def import_cortalconsors_quotes(self, path):
        p = Price()
        result = p.import_cortalconsors_quotes(path)
        return result

    def import_historic_quotes(self):
        # import pdb; pdb.set_trace()
        p = Price()
        result = p.import_historic_quotes()
        return result

    def update_stocks_boerse_frankfurt(self):
        # import pdb; pdb.set_trace()
        p = Price()
        result = p.import_boerse_frankfurt()
        return result


    def __str__(self):
        return str(self.docfile.name)

@receiver(post_delete, sender=Document)
def Document_post_delete_handler(sender, **kwargs):
    doc_instance = kwargs['instance']
    try:
        storage, path = doc_instance.docfile.storage, doc_instance.docfile.path
        storage.delete(path)
    except:
        pass