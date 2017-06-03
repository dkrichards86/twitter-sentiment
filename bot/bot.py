import os
import sys
import configparser
import json
from datetime import datetime, timedelta
import tweepy
import dataset

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

config = configparser.ConfigParser()
config.read(PROJECT_ROOT + '/config.ini')


class TweetBot():
    def __init__(self, stat_type='daily'):
        auth = tweepy.OAuthHandler(config['keys']['consumer_key'], config['keys']['consumer_secret'])
        auth.set_access_token(config['keys']['access_key'], config['keys']['access_secret'])
        self.api = tweepy.API(auth)
        
        self.db = dataset.connect('sqlite:////{}'.format(config['general']['database_path']))
        
        self.stat_type = stat_type
    
    @staticmethod
    def _floor_time(dt):
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    def fetch_results(self, query):
        result = self.db.query(query)
        
        payload = []
        for row in result:
            payload.append(row)

        return {
            'avg': payload[0]['avg_polarity'],
            'count': payload[0]['sum_count']
        }

    def generate_query(self, delta):
        now = datetime.now()
        to_date = self._floor_time(now)
        from_date = self._floor_time(now - delta)
    
        query = """
            SELECT avg(polarity) AS avg_polarity, sum(tweet_count) AS sum_count
            FROM sentiment
            WHERE datetime >= '{}'
            AND datetime <= '{}'
        """.format(from_date, to_date)
        
        return query

    def get_timedelta(self):
        delta = timedelta(days = 1)
        
        if self.stat_type == 'weekly':
            delta = timedelta(weeks = 1)
            
        return delta
    
    def write_stats(self, stats):
        avg = round(stats['avg'], 2)
        count = "{:,}".format(stats['count'])
        
        status = "Presidential Polarity Daily Brief- {}% average sentiment from {} tweets.".format(avg, count)
        
        if self.stat_type == 'weekly':
            status = "Presidential Polarity week in review- {} tweets collected, {}% average sentiment".format(count, avg)
        
        self.api.update_status(status)

    def run(self):
        delta = self.get_timedelta()
        query = self.generate_query(delta)
        results = self.fetch_results(query)
        self.write_stats(results)