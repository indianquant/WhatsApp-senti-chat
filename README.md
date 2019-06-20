# whatsapp analyser

It works with chats between two people or group chats.
It will display the results in terminal as well as write it to a file (stats.txt).

## Dependecies

This script requires the [TextBlob](https://github.com/sloria/TextBlob) package to be installed.

## whatsapp_stats.py

The main script. This script does all the processing of the history file.

### Usage

`python whatsapp_stats.py <filename> [<stopwords_filename>]`

Where `<filename>` is the whatsapp chat history file e.g. WhatsApp Chat with XYZ.txt

You do not have to specify the stopwords file, it will then just use the default file stopwords.txt.

## stopwords.txt

Contains a list of words that you wish to exclude from the most common words count. Contains words like a, an, the, I etc.

## Issues

Please raise issues with any difficulties you find.

## Sources 

For the sentiment analysis I'm using [TextBlob](https://github.com/sloria/TextBlob).

For the stopwords list I extended the English Google stopwords list found at [https://code.google.com/p/stop-words/](https://code.google.com/p/stop-words/).

## TO-DO :

A script that processes the history file to build a database of the most used words in a chat, along with the sentement of each word.


