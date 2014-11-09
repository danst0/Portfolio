import urllib.request
import json


class GoogleFinanceAPI:
    def __init__(self):
        self.prefix = "http://finance.google.com/finance/info?client=ig&q="

    def get(self, symbol, exchange):
        url = self.prefix + "%s:%s" % (exchange, symbol)
        u = urllib.request.urlopen(url)
        encoding = u.headers.get_content_charset()
        print(json.loads(u.read()[4:].decode()))
        obj = json.loads(u.read().decode())
        print(obj)
        # content = str(u.read())
        #         print(content)
        #         obj = json.loads(content[3:])
        return obj[0]


if __name__ == "__main__":
    c = GoogleFinanceAPI()

    quote = c.get("MSFT", "NASDAQ")
    print(quote)