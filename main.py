import bs4
import requests
import os
import brotli
import redis
import github

limit = 1290
redis_key = "ebooks"
client = redis.StrictRedis()
cache = client.hgetall(redis_key)
github_user_env = 'GITHUB_USER'
github_user = os.environ[github_user_env]
github_pass_env = 'GITHUB_PASS'
github_pass = os.environ[github_pass_env]
g = github.Github(github_user, github_pass)


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):].replace('/', '')
    return text


def create_dir(dir_name):
    if not os.path.exists(dir_name):
        print('Creating dir %s' % dir_name)
        os.mkdir(dir_name)


def get_redis(url):
    if cache.get(url) is None:
        html = requests.get(url).text
        bro = brotli.compress(html.encode(), brotli.MODE_TEXT)
        client.hset(redis_key, url, bro)
        print(f'{url} -> {len(bro)}')
    else:
        html = cache[url]

    return html


def get_links(i):
    url = f"http://23.95.221.108/page/{i}"
    html = get_redis(url)

    soup = bs4.BeautifulSoup(html, 'html.parser')
    arts = soup.findAll('article')
    hrefs = [x.find('a').attrs['href'] for x in arts]

    return [remove_prefix(x, 'https://it-eb.com/') for x in hrefs]


def get_book(path):
    url = f"http://23.95.221.108/{path}"
    return get_redis(url)


def write(file_name, content):
    fd = open(file_name, 'wb')
    fd.write(content)
    fd.flush()
    fd.close()


def main():
    dir_name = "./ScrapeContent/txt/"
    create_dir(dir_name)

    for i in range(1, limit + 1):
        for path in get_links(i):
            file = f'{dir_name}{path}.txt.brotli'
            if not os.path.exists(file):
                print(file)
                html = get_book(path)
                bro = brotli.compress(html.encode(), brotli.MODE_TEXT)
                write(file, bro)


main()
