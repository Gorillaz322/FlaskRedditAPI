from itertools import islice
import logging
from app import app, db
from flask import render_template
import re
import requests
import json
from collections import defaultdict
import main.config
from models import Comment, WordsCount, Word, Image
import mimetypes

logger = logging.getLogger(__name__)


@app.route('/chart')
def get_most_popular_words_dict():
    chart_word_count = 50
    words = []
    for word in list(islice(db.session.query(Word).order_by('count')[::-1], 0, chart_word_count)):
        words.append({
            'word': word.text,
            'count': word.count
        })

    return render_template('chart.html', data=json.dumps(words))


def get_hot_article_ids():
    response = json.loads(requests.get(main.config.HOT_ARTICLES_URL, headers=main.config.HEADERS).content)
    ids_list = [article['data']['id'] for article in response['data']['children']]
    return ids_list


def get_articles_comments(ids_list, get_ids=False):

    def get_comment_texts(comments_info):
        comment_texts = []
        for comment in comments_info['data']['children']:
            comment_data = comment['data']
            comment_text = comment_data.get('body')
            if comment_text:
                if get_ids:
                    item_to_append = (comment_data['id'], comment_text)
                else:
                    item_to_append = comment_text
                comment_texts.append(item_to_append)
            replies = comment_data.get('replies')
            if replies:
                comment_texts.extend(get_comment_texts(replies))
        return comment_texts

    comments = []
    for article_id in ids_list:
        response = json.loads(
            requests.get(main.config.ARTICLE_COMMENTS_URL.format(article_id), headers=main.config.HEADERS).content)

        for data in response:
            comments.extend(get_comment_texts(data))

    return comments


@app.route('/add_comments')
def add_comments():
    """
    Create db entries for comments
    :return:
    """
    comments = get_articles_comments(get_hot_article_ids(), get_ids=True)
    for index, comment in enumerate(comments):
        comment_id, comment_text = comment
        print('[VIEW] Comment {}'.format(index))

        comment_obj, created = Comment.add(comment_id, comment_text)
        if not created and comment_obj.text == comment_text:
            continue
        counted_words = get_words_count(comment_text)

        # delete old words
        if not created:
            words_to_delete = db.session.query(WordsCount).filter(
                WordsCount.comment == comment_obj,
                ~WordsCount.word.has(Word.text.in_([s[0] for s in counted_words]))).all()
            if words_to_delete:
                for word in words_to_delete:
                    db.session.delete(word)

        for word, count in counted_words:
            word_obj, created = Word.add(word)
            WordsCount.add(comment_obj, word_obj, count)

    db.session.commit()

    return render_template("stats.html", data=comments)


def get_words_count(text):
    regex = re.compile('[,.!?;:/"()]')
    words = regex.sub('', text).lower().split(' ')
    d = defaultdict(int)
    for word in words:
        if word not in main.config.BANNED_WORDS:
            d[word] += 1
    words_sorted_by_count = sorted(d.items(), key=lambda word: word[1], reverse=True)
    return words_sorted_by_count


@app.route('/stats')
def get_stats():
    return render_template("stats.html", data=db.session.query(Word).order_by('count')[::-1])


def get_img_urls_from_string(string):
    img_urls = []
    for url in re.findall(r'(https?://\S+(?<![)])$)', string):
        url_type, encoding = mimetypes.guess_type(url)
        if url_type and ('image' or 'gif') in url_type:
            img_urls.append(url)

    return img_urls


@app.route('/get_imgs')
def get_imgs():
    return render_template('imgs.html', data=db.session.query(Image).all())
