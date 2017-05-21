import os
import sys
import configparser
import json
from datetime import datetime
import tweepy

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

config = configparser.ConfigParser()
config.read(PROJECT_ROOT + '/config.ini')


class TweetCollector(tweepy.StreamListener):
    def __init__(self):
        super().__init__()
        self.tweets = []
        
    def on_error(self, status_code):
        if status_code == 420:
            print("Exception, rate limit hit - Twitter status code:", status_code)
            return False
        else:
            print("Twitter status code:", status_code)

    def on_status(self, status):
        self.tweets.append(status.text)

        if len(self.tweets) == int(config['general']['chunk_size']):
            self.write_tweets()

    def write_tweets(self):
        filename = datetime.now().strftime('%Y%m%d%H%M%S')
        
        with open('{}/{}.json'.format(config['general']['tweet_dir'], filename), 'w') as f:
            json.dump(self.tweets, f)
            print("Wrote {}:".format(config['general']['chunk_size']))
            self.tweets = []


if __name__ == "__main__":
    auth = tweepy.OAuthHandler(config['keys']['consumer_key'], config['keys']['consumer_secret'])
    auth.set_access_token(config['keys']['access_key'], config['keys']['access_secret'])
    api = tweepy.API(auth)

    keywords = config['general']['keywords'].split(',')

    while True:
        try:
            collector = TweetCollector()
            stream = tweepy.Stream(auth = api.auth, listener=collector)
            stream.filter(languages=["en"], track=keywords)
        except KeyboardInterrupt:
            raise
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print("Restarting")
