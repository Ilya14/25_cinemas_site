import logging
import math
from flask import Flask, render_template, json
from werkzeug.contrib.fixers import ProxyFix
from rq import Queue
from worker import conn
from cinemas import get_movies_info, sort_movies_list


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
queue = Queue(connection=conn)


def start_job():
    cinemas_limit = 30
    queue.enqueue(get_movies_info, args=(cinemas_limit,), result_ttl=43200, timeout=600, job_id='get_films')


def get_page(movies, page):
    films_on_page = 5
    pages_count = math.ceil(len(movies) / films_on_page)
    begin = (page - 1) * films_on_page
    end = begin + films_on_page
    return movies[begin: end], pages_count


@app.route('/')
def films_list():
    job = queue.fetch_job('get_films')
    if job is None:
        start_job()
    return render_template('films_list.html')


@app.route('/<int:page>')
def get_films_table(page):
    job = queue.fetch_job('get_films')
    if job is None:
        start_job()
        return 'Not ready', 202
    elif job.is_finished:
        movies_count = 10
        movies = sort_movies_list(job.result)[:movies_count]
        movies_page, pages_count = get_page(movies, page)
        return render_template('films_table.html',
                               movies=movies_page,
                               cur_page=page,
                               pages_count=pages_count)
    else:
        return 'Not ready', 202


@app.route('/api')
def api():
    job = queue.fetch_job('get_films')
    if job is None:
        start_job()
        return 'Not ready', 202
    elif job.is_finished:
        return json.dumps(job.result, indent=4, ensure_ascii=False)
    else:
        return 'Not ready', 202


@app.route('/help/api')
def api_help():
    return render_template('api_help.html')


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s# %(levelname)-8s [%(asctime)s] %(message)s',
        datefmt=u'%m/%d/%Y %I:%M:%S %p'
    )
    app.run()
