from app import app
from flask import render_template
import re
import requests
import json
import datetime
from collections import defaultdict
import main.config


def get_hot_article_ids():
    response = json.loads(requests.get(main.config.HOT_ARTICLES_URL, headers=main.config.HEADERS).content)
    ids_list = [article['data']['id'] for article in response['data']['children']]
    return ids_list


def get_articles_comments(ids_list):

    def get_comment_texts(comments_info):
        comment_texts = []
        for comment in comments_info['data']['children']:
            comment_data = comment['data']
            comment_text = comment_data.get('body')
            if comment_text:
                comment_texts.append(comment_text)
            replies = comment_data.get('replies')
            if replies:
                comment_texts.extend(get_comment_texts(replies))
        return comment_texts

    comments = []
    for article_id in ids_list[:10]:
        response = json.loads(
            requests.get(main.config.ARTICLE_COMMENTS_URL.format(article_id), headers=main.config.HEADERS).content)

        for data in response:
            comments.extend(get_comment_texts(data))

    return comments


@app.route('/')
def get_stats():
    # from models import Comment, Word
    now = datetime.datetime.now()
    comments = get_articles_comments(get_hot_article_ids())
    joined_comments = ' '.join(comments).lower()

    regex = re.compile('[,.!?;:/()]')
    words = regex.sub('', joined_comments).split(' ')
    # valid_words = filter(lambda s: s not in main.config.BANNED_WORDS, words)
    d = defaultdict(int)
    for word in words:
        if word not in main.config.BANNED_WORDS:
            d[word] += 1

    words_sorted_by_count = sorted(d.items(), key=lambda word: word[1], reverse=True)
    #
    # words_sorted_by_count = Counter(valid_words).most_common()
    print(datetime.datetime.now() - now)
    return render_template("home.html", data=words_sorted_by_count)
