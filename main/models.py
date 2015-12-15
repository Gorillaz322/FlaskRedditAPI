from app import db
from sqlalchemy.orm.exc import NoResultFound


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    reddit_id = db.Column(db.String(64), unique=True)

    @classmethod
    def add(cls, reddit_id, text):
        try:
            comment_obj = db.session.query(Comment).filter(Comment.reddit_id == reddit_id).one()
            created = False
        except NoResultFound:
            comment_obj = Comment(reddit_id=reddit_id, text=text)
            db.session.add(comment_obj)
            created = True

        if created:
            from views import get_img_urls_from_string

            for url in get_img_urls_from_string(comment_obj.text):
                Image.add(url, comment_obj)

        return comment_obj, created


class Word(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1024))
    count = db.Column(db.Integer, default=0)

    @classmethod
    def add(cls, word):
        try:
            word_obj = db.session.query(Word).filter(Word.text == word).one()
            created = False
        except NoResultFound:
            word_obj = Word(text=word)
            db.session.add(word_obj)
            created = True
        return word_obj, created

    def update_count(self, count):
        self.count = self.count + count
        db.session.query(Word).filter_by(id=self.id).update({'count': self.count})
        return self.count


class WordsCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)
    comment_id = db.Column(db.ForeignKey('comments.id'))
    comment = db.relationship('Comment', backref=db.backref('words_count', lazy='dynamic'))
    word_id = db.Column(db.ForeignKey('words.id'))
    word = db.relationship('Word', backref=db.backref('counts', lazy='dynamic'))

    @classmethod
    def add(cls, comment_obj, word_obj, count):
        count_to_update = None
        try:
            count_obj = db.session.query(WordsCount).filter(
                WordsCount.word == word_obj,
                WordsCount.comment == comment_obj).one()
            if count_obj.count != count:
                count_to_update = comment_obj.count - count
                db.session.query(WordsCount).filter_by(id=count_obj.id).update({'count': count})
            created = False
        except NoResultFound:
            word_obj.update_count(count)
            count_obj = WordsCount(
                word=word_obj, comment=comment_obj, count=count)
            db.session.add(count_obj)
            count_to_update = count
            created = True

        if count_to_update:
            word_obj.update_count(count_to_update)

        return count_obj, created


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1024))
    comment_id = db.Column(db.ForeignKey('comments.id'))
    comment = db.relationship('Comment', backref=db.backref('images', lazy='dynamic'))

    @classmethod
    def add(cls, url, comment):
        try:
            img_obj = db.session.query(Image).filter(
                Image.url == url, Image.comment == comment).one()
            created = False
        except NoResultFound:
            img_obj = Image(url=url, comment=comment)
            db.session.add(img_obj)
            created = True

        return img_obj, created
