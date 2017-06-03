from bot import TweetBot


if __name__ == "__main__":
    collector = TweetBot(stat_type='weekly')
    collector.run()
