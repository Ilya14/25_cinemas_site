import requests
import random
import logging

from bs4 import BeautifulSoup


def fetch_afisha_page():
    logging.info('Obtaining the list of movies from afisha...')
    afisha_url = 'http://www.afisha.ru/msk/schedule_cinema/'
    return requests.get(afisha_url).text


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, 'lxml')

    movies_titles_tags = soup.find_all('div', {'class': 'm-disp-table'})

    movies_titles_tags = movies_titles_tags[:7]

    afisha_movies_info = {}
    for movie_title_tag in movies_titles_tags:
        movie_title = movie_title_tag.find('a').text
        movie_afisha_url = movie_title_tag.find('a').attrs['href']
        cinemas_count = len(movie_title_tag.parent.find_all('td', {'class': 'b-td-item'}))
        afisha_movies_info[movie_title] = {
            'movie_afisha_url': movie_afisha_url,
            'cinemas_count': cinemas_count
        }

    return afisha_movies_info


def fetch_kinopoisk_movie_page(movie_title, proxy_list):
    timeout = 3
    kinopoisk_page_url = 'https://www.kinopoisk.ru/index.php'
    params = {
        'kp_query': movie_title,
        'first': 'yes'
    }

    while True:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Agent:%s'.format(get_random_agent())
        }
        proxy_ip = get_random_proxy(proxy_list)
        proxy = {'http': proxy_ip}

        logging.info('Try proxy %s...', proxy_ip)

        try:
            request = requests.Session().get(
                kinopoisk_page_url,
                params=params,
                headers=headers,
                proxies=proxy,
                timeout=timeout
            )
        except(requests.exceptions.ConnectTimeout,
               requests.exceptions.ConnectionError,
               requests.exceptions.ProxyError,
               requests.exceptions.ReadTimeout):
            logging.exception('Connect error. Reconnect...')
        else:
            break

    return request.text


def get_text(elem):
    try:
        text = elem.text
    except AttributeError:
        text = None
    return text


def parse_kinopoisk_movie_page(raw_html):
    soup = BeautifulSoup(raw_html, 'lxml')

    kinopoisk_movie_info = {
        'rating':  get_text(soup.find('span', {'class': 'rating_ball'})),
        'rating_count': get_text(soup.find('span', {'class': 'ratingCount'})),
        'film_synopsys': get_text(soup.find('div', {'class': 'brand_words film-synopsys'})),
        'film_img': soup.find('div', {'class': 'film-img-box'}).find('img').attrs['src']
    }

    return kinopoisk_movie_info


def get_movies_info():
    afisha_page = fetch_afisha_page()
    afisha_movies_info = parse_afisha_list(afisha_page)

    proxies_list = get_proxies_list()

    movies_count = len(afisha_movies_info.keys())
    movies_info = []
    for num, movie in enumerate(afisha_movies_info.keys()):
        logging.info('[%d/%d] Get "%s" page...', num + 1, movies_count, movie)
        kinopoisk_page = fetch_kinopoisk_movie_page(movie, proxies_list)
        kinopoisk_movie_info = parse_kinopoisk_movie_page(kinopoisk_page)
        movies_info.append({
            'name': movie,
            'cinemas_count': afisha_movies_info[movie]['cinemas_count'],
            'movie_afisha_url': afisha_movies_info[movie]['movie_afisha_url'],
            'rating': kinopoisk_movie_info['rating'],
            'rating_count': kinopoisk_movie_info['rating_count'],
            'film_synopsys': kinopoisk_movie_info['film_synopsys'],
            'film_img': kinopoisk_movie_info['film_img'],
        })

    return movies_info


def sort_movies_list(movies):
    return sorted(
        movies,
        key=lambda item: item['rating'] if item['rating'] is not None else '0',
        reverse=True
    )


def get_random_agent():
    agent_list = [
        'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Opera/9.80 (Windows NT 6.2; WOW64) Presto/2.12.388 Version/12.17',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
    ]
    return random.choice(agent_list)


def get_proxies_list():
    proxy_url = 'http://www.freeproxy-list.ru/api/proxy'
    params = {'anonymity': 'true', 'token': 'demo'}
    request = requests.get(proxy_url, params=params).text
    proxies_list = request.split('\n')
    return proxies_list


def get_random_proxy(proxy_list):
    return random.choice(proxy_list)


if __name__ == '__main__':
    pass
