import os
from flask import Flask, jsonify, g, make_response, request, current_app
from functools import update_wrapper
from flask.json import JSONEncoder
from datetime import datetime, timedelta, date
import dataset
import decimal
import configparser
from statistics import mean

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

config = configparser.ConfigParser()
config.read(PROJECT_ROOT + '/config.ini')


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        print(obj)
        if isinstance(obj, datetime):
            return str(obj)
        elif isinstance (obj, decimal.Decimal):
            return float(obj)
        else:
            return super().default(obj)

def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def _roundTime(dt):
    return datetime(dt.year, dt.month, dt.day, dt.hour, 15 * (dt.minute // 15))

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

@app.before_request
def before_request():
    db = getattr(g, 'db', None)
    
    if db is None:
        db = g.db = dataset.connect('sqlite:////{}'.format(config['general']['database_path']))

@app.route('/', methods=['GET'])
@crossdomain(origin='*')
def index():
    to_date = _roundTime(datetime.now())
    to_date_param = request.args.get('to')
    if to_date_param:
       to_date = datetime.strptime(to_date_param, '%Y%m%d')
      
    from_date = to_date - timedelta(weeks = 1)
    from_date_param = request.args.get('from')
    if from_date_param:
       from_date = datetime.strptime(from_date_param, '%Y%m%d')
       
       if from_date > to_date:
           stash = from_date
           from_date = to_date
           to_date = stash
    
    query = """
        SELECT datetime, polarity, percent_positive, percent_negative, tweet_count
        FROM sentiment
        WHERE datetime >= '{}'
        AND datetime <= '{}'
    """.format(from_date, to_date)

    result = g.db.query(query)
    payload = []
    polarity = []
    for row in result:
        payload.append(row)
        polarity.append(row['polarity'])

    mean_polarity = mean([row['polarity'] for row in payload])
    total_counts = sum([row['tweet_count'] for row in payload])

    return jsonify({
        'data': payload,
        'count': total_counts,
        'avg': round(mean_polarity, 2),
        'start_datetime': from_date,
        'end_datetime': to_date
    })

@app.route('/average_polarity', methods=['GET'])
@crossdomain(origin='*')
def avg_polarity():
    to_date = datetime.now()
    to_date_param = request.args.get('to')
    if to_date_param:
       to_date = datetime.strptime(to_date_param, '%Y%m%d')
      
    from_date = to_date - timedelta(weeks = 1)
    from_date_param = request.args.get('from')
    if from_date_param:
       from_date = datetime.strptime(from_date_param, '%Y%m%d')
       
       if from_date > to_date:
           stash = from_date
           from_date = to_date
           to_date = stash
    
    query = """
        SELECT avg(polarity) AS avg_polarity
        FROM sentiment
        WHERE datetime >= '{}'
        AND datetime <= '{}'
    """.format(from_date, to_date)

    result = g.db.query(query)
    payload = []
    for row in result:
        payload.append(round(row['avg_polarity'], 2))

    return jsonify({'data': payload})
    
@app.route('/tweet_count', methods=['GET'])
@crossdomain(origin='*')
def tweet_count():
    to_date = datetime.now()
    to_date_param = request.args.get('to')
    if to_date_param:
       to_date = datetime.strptime(to_date_param, '%Y%m%d')
      
    from_date = to_date - timedelta(weeks = 1)
    from_date_param = request.args.get('from')
    if from_date_param:
       from_date = datetime.strptime(from_date_param, '%Y%m%d')
       
    if from_date > to_date:
       stash = from_date
       from_date = to_date
       to_date = stash
    
    query = """
        SELECT sum(tweet_count) AS tweet_count
        FROM sentiment
        WHERE datetime >= '{}'
        AND datetime <= '{}'
    """.format(from_date, to_date)

    result = g.db.query(query)
    payload = []
    for row in result:
        payload.append(row['tweet_count'])

    return jsonify({'data': payload})
