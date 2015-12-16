import os

HEADERS = {
    "User-Agent": "CustomAPI"
}

BANNED_WORDS = [
    'a', 'the', 'at', 'on', 'by', 'an', '', 'and', 'of', 'to', 'i', 'it', 'in', 'that', 'you', 'for', 'this', 'they',
    'are', 'was', 'be', 'with', 'have', 'but', 'not', 'my', 'as', "it's", 'if', 'so', 'your', 'from', 'or', 'can',
    'would', 'that', 'what', 'about', 'me', 'out', 'there', 'we', 'do', 'will', 'no', 'up', 'he', 'she', "don't",
    'when', "i'm", 'has', 'had', 'them', 'how', '-', 'is'
]

HOT_ARTICLES_URL = "https://reddit.com/hot/.json"

ARTICLE_COMMENTS_URL = "https://reddit.com/comments/{}/.json"

DEBUG = True

DATABASE_URL = os.environ.get('DATABASE_URL', '')
