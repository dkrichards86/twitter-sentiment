import os
import configparser
import json
import re
from datetime import datetime, timedelta
from statistics import mean, StatisticsError

import dataset
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

url_re = re.compile(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', flags=re.MULTILINE)
tag_re = re.compile(r'(@|#)\w*\b', flags=re.MULTILINE)

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

config = configparser.ConfigParser()
config.read(PROJECT_ROOT + '/config.ini')


class TweetProcessor():
    def __init__(self):
        self.db = dataset.connect('sqlite:////{}'.format(config['general']['database_path']))

        self.vader = nltk.sentiment.vader.SentimentIntensityAnalyzer()

    @staticmethod
    def _cleanse(text):
        text = text.encode('ascii','ignore').decode('utf-8').lower()
        text = url_re.sub('', text)
        text = tag_re.sub('', text)
    
        return text

    @staticmethod
    def _round(num):
        return round(num, 2)

    @staticmethod
    def _roundTime(dt):
        return datetime(dt.year, dt.month, dt.day, dt.hour, 15 * (dt.minute // 15))

    def generate_report(self, polarity, counts):
        try:
            polarity = self._round(mean(polarity) * 100 + 50)
        except StatisticsError:
            polarity = 50
        finally:
            percent_positive = self._round((counts['positive'] / counts['total']) * 100)
            percent_negative = self._round((counts['negative'] / counts['total']) * 100)
    
        sentiment_time = self._roundTime(datetime.now())

        self.db.begin()
        try:
            table = self.db['sentiment']
            table.insert(dict(
                datetime=sentiment_time,
                polarity=polarity,
                percent_positive=percent_positive,
                percent_negative=percent_negative,
                tweet_count=counts['total']
            ))
        except Exception:
            self.db.rollback()
            raise
        else:
            self.db.commit()

    def process(self):
        polarity = []
        counts = {
            'total': 0,
            'positive': 0,
            'negative': 0
        }
        

        file_set = [os.path.join(config['general']['tweet_dir'], file) for file in os.listdir(config['general']['tweet_dir']) if file.endswith(".json")]
        
        for path in file_set:
            with open(path) as f:
                for tweet in json.load(f):
                    ss = self.vader.polarity_scores(self._cleanse(tweet))
        
                    if ss['compound'] > 0.5:
                        counts['positive'] += 1
                    elif ss['compound'] < -0.5:
                        counts['negative'] += 1
                    
                    counts['total'] += 1
                    polarity.append(ss['compound'])

        try:
            self.generate_report(polarity, counts)
        except Exception as e:
            print(e)
        else:
            for path in file_set:
                os.remove(path)

if __name__ == "__main__":
    processor = TweetProcessor()
    processor.process()
