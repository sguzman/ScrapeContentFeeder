import bs4
import requests
import os
import brotli
import git

limit = 1290
redis_key = "ebooks"
repo_name = './ScrapeContent'
dir_name = repo_name + '/txt/'
repo = git.Repo(repo_name)


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):].replace('/', '')
    return text


def create_dir(dir_name_dir):
    if not os.path.exists(dir_name_dir):
        print('Creating dir %s' % dir_name_dir)
        os.mkdir(dir_name_dir)


def get(url):
    return requests.get(url).text


def get_links(i):
    url = f"http://23.95.221.108/page/{i}"
    html = get(url)

    soup = bs4.BeautifulSoup(html, 'html.parser')
    arts = soup.findAll('article')
    hrefs = [x.find('a').attrs['href'] for x in arts]

    return [remove_prefix(x, 'https://it-eb.com/') for x in hrefs]


def get_book(path):
    url = f"http://23.95.221.108/{path}"
    return get(url)


def write(file_name, content):
    fd = open(file_name, 'wb')
    fd.write(content)
    fd.flush()
    fd.close()


def main():
    create_dir(dir_name)

    for i in range(1, limit + 1):
        for path in get_links(i):
            file = f'./txt/{path}.txt.brotli'
            if os.path.exists(file):
                return
            else:
                print(file)

                html = get_book(path)
                bro = brotli.compress(html.encode(), brotli.MODE_TEXT)
                write(repo_name + '/' + file, bro)

                repo.index.add([file])
                repo.index.commit(f'Added {file}')


main()
