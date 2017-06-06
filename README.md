# Tweet Sentiment Platform

The twitter sentiment platform has three main components, the collector, the processor,
and the API.

### Collector
The collector utilizes Twitter's stream to collect firehose tweets filtered by keyword.

We use the great [Tweepy](http://www.tweepy.org/) library as the platform's foundation.

### Processor
The processor conducts sentiment analysis on a batch of tweets and writes them to the database.

Sentiment is scored using [Vader Sentiment Analysis](http://comp.social.gatech.edu/papers/icwsm14.vader.hutto.pdf) implemented in [NLTK](http://www.nltk.org/).

### API
The sentiment API serves tweet polarity to the frontend.  

The API is built on [Flask](http://flask.pocoo.org/) and connects to a SQLite3 database.

### Bot
The sentiment Bot publishes stats to Twitter on a cron.  

[Tweepy](http://www.tweepy.org/) is used to handle publishing.

## Usage
This platform is built on [Python3](https://www.python.org/download/releases/3.0/). This assumes
you have a Python3 environment enabled.

First, run `pip install -r requirements.txt` to install the dependencies. You will also
need some [corpora from NLTK](http://www.nltk.org/data.html), so run `nlkt.download()`.

Once you have the dependencies, copy `config.ini.example` to `config.ini` and update as
appropriate.

Next, create a SQLite3 database using the schema provided in `databases/`.

After that, follow the READMEs in `collector/`, `processor/`, and `api/` to run
the components.
