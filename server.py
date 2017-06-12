import logging
import math
from flask import Flask, render_template, json
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.contrib.cache import SimpleCache
from cinemas import get_movies_info, sort_movies_list


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
cache = SimpleCache()
TIMEOUT = 43200


def get_movies(cinemas_limit=30, movies_count=10, threads_count=8):
    movies = cache.get('movies')
    if movies is None:
        movies_info = get_movies_info(cinemas_limit=cinemas_limit, threads_count=threads_count)
        movies = sort_movies_list(movies_info)[:movies_count]
        cache.set('movies', movies, timeout=TIMEOUT)
    return movies


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
    movies_page, pages_count = get_page(page)
    return render_template('films_table.html',
                           movies=movies_page,
                           cur_page=page,
                           pages_count=pages_count)


@app.route('/api')
def api():
    return json.dumps(get_movies(), indent=4, ensure_ascii=False)


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
