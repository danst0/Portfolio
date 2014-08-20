Portfolio
=========

Portfolio wealth management app for the command line.

Todos
=====
* Testing
 * Test completeness of import (esp. duplicates, number of transactions imported) --> Done
 * Test green-field installation --> Done
 * Make copy of database after initial (complete) import, merge and clearing (so after it is identical to my real portfolio)
* Develop reports that I am interested in
  * Performance
   * Rolling ROI for the last year. on a monthly rolling basis (graph)
   * How to judge my performance, e.g. timing decision by finding local min. (for buy decision) and max. (for sell decision), alternative: what were the expected risks/profits? What is their realization
   * Absolute PF value (e.g. graph) --> started
    * Pure development must contain invest, divest (not dividend)
    * Drivers for development unclear. How to include in graph?
  * Savings
  * ...
* Dialogues
 * Enable way to abort dialogues
 * redo stock split: keep current current prices and quants, just include as a marker
 * Make dialogues more resilient (ctrl-c and stupid input) 
* Other functions
 * Function to reset tables money and prices and reinitialize based on transactions (loosing the prices imported)
* Programming
 * Modularization
 * More functions
 * More logic
 * Less chaos
 * make dates into python dates and only convert to string if required
