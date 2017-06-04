import logging
import math
from flask import Flask, render_template, request
from werkzeug.contrib.fixers import ProxyFix
from flask_caching import Cache
from cinemas import get_movies_info, sort_movies_list

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.cache = Cache(app, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': './cache'
})

CACHE_TIMEOUT = 43200


@app.cache.cached(timeout=CACHE_TIMEOUT, key_prefix='movies')
def get_movies():
    return sort_movies_list(get_movies_info())


def get_page(page):
    movies = get_movies()
    films_on_page = 5
    pages_count = math.ceil(len(movies) / films_on_page)
    begin = (page - 1) * films_on_page
    end = begin + films_on_page
    return movies[begin: end], pages_count


@app.route('/')
def films_list():
    return render_template('films_list.html')


@app.route('/<int:page>')
def get_films_table(page):
    movies, pages_count = get_page(page)
    return render_template('films_table.html', movies=movies, cur_page=page, pages_count=pages_count)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s# %(levelname)-8s [%(asctime)s] %(message)s',
        datefmt=u'%m/%d/%Y %I:%M:%S %p'
    )
    app.run()
