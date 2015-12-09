from flask import Flask, render_template
import requests
import json
import datetime
from collections import Counter

app = Flask(__name__)
app.debug = True

HEADERS = {"User-Agent": "CustomAPI"}


def get_hot_article_ids():
    response = json.loads(requests.get("https://reddit.com/hot/.json", headers=HEADERS).content)
    ids_list = [article['data']['id'] for article in response['data']['children']]
    return ids_list

#test1
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
    for article_id in ids_list:
        response = json.loads(
            requests.get("https://reddit.com/comments/{}/.json".format(article_id), headers=HEADERS).content)

        for data in response:
            comments.extend(get_comment_texts(data))

    return comments


@app.route('/get_stats')
def get_stats():
    now = datetime.datetime.now()
    comments = get_articles_comments(get_hot_article_ids())
    words = []
    banned_characters = [',', '.', '!', '?', ';', ':']
    banned_words = ['a', 'the', 'at', 'on', 'by', 'an', '']
    for comment in comments:
        comment_words = comment.split(' ')
        for word in comment_words:
            word = word.lower()
            if any(character in word for character in banned_characters):
                for s in banned_characters:
                    word = word.replace(s, "")
            if word not in banned_words:
                words.append(word)

    words_sorted_by_count = sorted(dict(Counter(words)).items(), key=lambda item: item[1], reverse=True)
    print(datetime.datetime.now() - now)
    return render_template("home.html", data=words_sorted_by_count)

if __name__ == '__main__':
    app.run()
