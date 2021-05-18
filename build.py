from datetime import datetime
from feedgen.feed import FeedGenerator
from functools import cache
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import markdown
from os import mkdir, listdir
from os.path import abspath, dirname, join, realpath
from re import match, search
from shutil import copy, rmtree
from urllib.parse import urljoin


URL = "http://iankinsey.com/"
FEED_NAME = "rss.xml"
SITEMAP_NAME = "sitemap.xml"
SLUG_REGEX = r"\d+-\d+-\d+-[a-zA-Z\-]+"
SLUG_DATE_REGEX = r"\d+-\d+-\d+"
PROJECT_ROOT = abspath(dirname(realpath(__file__)))
INDEX_TEMPLATE = "index.jinja"
ARTICLE_TEMPLATE = "article.jinja"
SITEMAP_TEMPLATE = "sitemap.jinja"
STATIC_DIR = join(PROJECT_ROOT, 'static')
TEMPLATES_DIR = join(PROJECT_ROOT, 'templates')
ARTICLES_DIR = join(PROJECT_ROOT, 'articles')
DIST_DIR = join(PROJECT_ROOT, 'dist')
ARTICLE_DIST_DIR = join(DIST_DIR, 'articles')
PAGES = [
    'about',
    'projects'
]
ARTICLES = [
    i for i in listdir(ARTICLES_DIR)
    if match(SLUG_REGEX, i)
]
ARTICLES.sort(reverse=True)
ENV = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True
)
ENV.globals['current_year'] = datetime.now().year


def render_pages():
    for page in PAGES:
        template = ENV.get_template(f"{page}.jinja")
        contents = template.render()

        open(join(DIST_DIR, f"{page}.html"), 'w').write(contents)


def render_index():
    articles = [get_article(a)['html'] for a in ARTICLES]
    template = ENV.get_template(INDEX_TEMPLATE)
    contents = template.render(articles=articles)

    open(join(DIST_DIR, "index.html"), 'w').write(contents)


def render_articles():
    for article in ARTICLES:
        render_article(article)


def render_article(name):
    contents = get_article_contents(name)

    open(join(ARTICLE_DIST_DIR, f'{name}.html'), 'w').write(contents)


def get_article_contents(name):
    article = get_article(name)
    template = ENV.get_template(ARTICLE_TEMPLATE)
    return template.render(title=article['title'], article=article['html'])


@cache
def get_article(article):
    md = open(join(ARTICLES_DIR, article)).read()
    short_url = f"/articles/{article}.html"
    url = urljoin(URL, short_url)
    title = md.split("\n")[0].replace("#", "").strip()
    datestr = search(SLUG_DATE_REGEX, article)[0]
    date = datetime.strptime(datestr, '%Y-%m-%d')
    published = f"####{date.strftime('%B %d, %Y')}"
    md_content = md.replace(title, f"[{title}]({short_url})\n{published}", 1)

    return {
        "html": markdown(md_content),
        "title": title,
        "name": article,
        "url": url,
        "short_url": url,
        "date": f"{date}T00:00:00+00:00",
        "parsed_date": date
    }


def render_rss():
    feed_url = urljoin(URL, FEED_NAME)
    fg = FeedGenerator()
    fg.title("Ian Kinsey")
    fg.subtitle("Thoughts in software development")
    fg.author({"name": "Ian Kinsey", "email": "ikrss@nym.hush.com"})
    fg.link(href=URL, rel="alternate")
    fg.link(href=feed_url, rel="self")
    fg.language("en")

    for name in ARTICLES:
        article = get_article(name)
        entry = fg.add_entry()
        entry.title(article['title'])
        entry.published(article['date'])
        entry.link(href=article['url'])

    fg.rss_file(join(DIST_DIR, FEED_NAME))


def render_sitemap():
    template = ENV.get_template(SITEMAP_TEMPLATE)
    articles = [get_article(a) for a in ARTICLES]
    urls = [urljoin(URL, f"{p}.html") for p in PAGES] + [URL]
    contents = template.render(urls=urls, articles=articles)

    open(join(DIST_DIR, SITEMAP_NAME), 'w').write(contents)


def copy_static_assets():
    for file_name in listdir(STATIC_DIR):
        copy(join(STATIC_DIR, file_name), DIST_DIR)


def setup():
    try:
        rmtree(DIST_DIR)
    except FileNotFoundError:
        pass

    mkdir(DIST_DIR)
    mkdir(ARTICLE_DIST_DIR)


def build():
    setup()
    render_pages()
    render_articles()
    render_index()
    render_rss()
    render_sitemap()
    copy_static_assets()


if __name__ == "__main__":
    build()
