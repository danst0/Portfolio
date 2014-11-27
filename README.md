Portfolio
=========

Portfolio wealth management app for the command line.

Todos
=====

* Overview of stored information (transactions, prices) per stock (e.g. in stock graph)
* Import should work on server (e.g. upload of files,...)
* Taxes for profits (25% + 25%*5.5%)
* Indicator for buy and sell decision for tax reasons (Freistellungsauftrag 800€, kids)
* Semi-random Demo Portfolio with Demo User 
* Internet Explorer und Firefox
* Change font for more screen legibility
* Hide form in beginning, display loading, then no data
* New view/add to some, share of individual stocks
* Regression to mean for retirement forecasting

---

* Give update view a few informations more
* How to display multiple information at once (__str__)
* UI Design
  * Make nice
* Testing
  * Test completeness of import (esp. duplicates, number of transactions imported) --> Done
  * Test green-field installation --> Done
  * Make copy of database after initial (complete) import, merge and clearing (so after it is identical to my real portfolio)
* Develop reports that I am interested in
  * How to judge my performance, e.g. timing decision by finding local min. (for buy decision) and max. (for sell decision), alternative: what were the expected risks/profits? What is their realization
   * Absolute PF value (e.g. graph) --> started
    * Pure development must contain invest, divest (not dividend)
    * Drivers for development unclear. How to include in graph?
   * Decision oriented analysis
     * What effect did this buy (and esp. this buy-sell combination have)
  * Savings
  * ...
* Other functions
 * Function to reset tables money and prices and reinitialize based on transactions (loosing the prices imported)
* Programming
 * Modularization
 * More functions
 * More logic
 * Less chaos
 * make dates into python dates and only convert to string if required

Done
---
* How to integrate current scripts into django? --> done
* Write tests for aliases --> done
* App Design
* Switch to django for the data model -- > done
* Add graph function for stocks/portfolio/profitability
* Reporting
  * Performance
  * Rolling ROI for the last year. on a monthly rolling basis (graph)
 * redo stock split: keep current current prices and quants, just include as a marker
 * Make dialogues more resilient (ctrl-c and stupid input) 
* Dialogues
  * Enable way to abort dialogues
* Support a way to present to others
* Multi-User support
* Support multiple portfolios (eg. to have one to show)
* Quality check forecast retirement (esp. interest rate)
* Timing-Analyse, wie hat sich der Kurs vorher/nachher entwickelt
* ROI-Kuchen: ROI als Kuchendiagramm, wer hat wieviel dazu beigetragen

Install
===
Commands to get it running
---
python3 manage.py runserver
python3 manage.py syncdb
python3 manage.py startapp m2
python3 manage.py sql m2 - Show commands to build databases
python manage.py validate – Checks for any errors in the construction of your models.
