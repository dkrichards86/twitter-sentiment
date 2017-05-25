## Tweet Sentiment Processor
The processor conducts sentiment analysis on a batch of tweets and writes them to the database.

Sentiment is scored using [NLTK's](http://www.nltk.org/) Vader Sentiment Analysis tool.

Database path is configured in `config.ini`

### Usage
```python
python processor.python
```