import os
import requests
import operator
import re
import nltk
import json
from rq import Queue
from rq.job import Job
from worker import conn
from flask import Flask, render_template, request, jsonify
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup

app = Flask(__name__)
q = Queue(connection=conn)
# app.config.from_object(os.environ['APP_SETTING'])

# @app.route('/')
# def hello():
#     return "Hello World!"
# 
# @app.route('/<name>')
# def hello_name(name):
#     return 'Hello {}!'.format(name)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def get_counts():
    # get url
    data = json.loads(request.data.decode())
    url = data["url"]
    if 'http://' not in url[:7]:
        url = 'http://' + url
    # start job
    job = q.enqueue_call(
        func=count_and_save_words, args=(url,), result_ttl=5000
    )
    # return created job id
    return job.get_id()


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

#     job = Job.fetch(job_key, connection=conn)
# 
#     if job.is_finished:
#         result = Result.query.filter_by(id=job.result).first()
#         results = sorted(
#             result.result_no_stop_words.items(),
#             key=operator.itemgetter(1),
#             reverse=True
#         )[:10]
#         return jsonify(results)
#     else:
#         return "Nay!", 202
      return "Nay!", 202

def count_and_save_words(url):

    errors = []

    try:
        r = requests.get(url)
    except:
        errors.append(
            "Unable to get URL. Please make sure it's valid and try again."
        )
        return {"error": errors}

    # text processing
    raw = BeautifulSoup(r.text, 'html.parser').get_text()
    nltk.data.path.append('./nltk_data/')  # set the path
    tokens = nltk.word_tokenize(raw)
    text = nltk.Text(tokens)

    # remove punctuation, count raw words
    nonPunct = re.compile('.*[A-Za-z].*')
    raw_words = [w for w in text if nonPunct.match(w)]
    raw_word_count = Counter(raw_words)

    # stop words
    no_stop_words = [w for w in raw_words if w.lower() not in stops]
    no_stop_words_count = Counter(no_stop_words)

    # save the results
    results = sorted(
                no_stop_words_count.items(),
                key=operator.itemgetter(1),
                reverse=True
            )
#     try:
#         result = Result(
#             url=url,
#             result_all=raw_word_count,
#             result_no_stop_words=no_stop_words_count
#         )
#         return result.id
#     except:
#         errors.append("Unable to add item to database.")
#         return {"error": errors}

if __name__== '__main__':
#     os.environ['APP_SETTING'] = "config.DevelopmentConfig"
    app.run()