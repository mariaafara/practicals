Given as input:
a text and a glossary files

*  We compute the frequency of each glossary entry in the input text.
*  We enter all glossary entries found in text in a database (DB), along with their frequencies.
*  We get the machine translation into Spanish of the n most frequent glossary entries found in the
input text, using the API (https://libretranslate.com/docs/). 
*  We add the translations to the DB.

Steps done:
* Read the glossary file line-by-line by iterating over the file object of the glossary file in a for
loop, lowercase and strip the line then add the glossary in a dictionary as a key with a zero
frequency as its value.
* In a similar fashion, read the input text file line-by-line, preprocess the line by lowercasing and
removing stopwords and any non-alphabetical words (punctuations, etc), then increase the
frequency of every found glossary in the preprocessed line (if found).
* Then add all found glossaries in the input text along with their frequency in a ‘frequencies’
table in the database, where all glossaries can be found in the ‘glossary’ column, and all their
corresponding frequencies in the ‘frequency’ column.
* Query the ‘frequencies’ table in the DB to select the top 10 frequent glossaries. Then using
the ‘libretranslate’ API, get their spanish translation. Finally, insert the 1