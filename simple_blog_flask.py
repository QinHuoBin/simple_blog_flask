from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Note(db.Model):
    '''帖子的数据库模型'''
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    author = db.Column(db.Text)
    published_datetime = db.Column(db.DateTime)
    view_num = db.Column(db.Integer, default=0)
    comment_num = db.Column(db.Integer, default=0)

    # 表示帖子的访问权限
    permission_dict = {'visitor': 0, 'user': 1, 'admin': 2}
    permission = db.Column(db.Integer, default=permission_dict['visitor'])

    def to_json(self):
        '''实例转json'''
        _dict = self.__dict__.copy()
        if "_sa_instance_state" in _dict:
            del _dict["_sa_instance_state"]
        return _dict


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    belong_to = db.Column(db.Integer)
    nickname = db.Column(db.Text)
    body = db.Column(db.Text)
    published_datetime = db.Column(db.DateTime, default=datetime.datetime.now())

    def to_json(self):
        '''实例转json'''
        _dict = self.__dict__.copy()
        if "_sa_instance_state" in _dict:
            del _dict["_sa_instance_state"]
        return _dict


class User(db.Model):
    '''用户的数据库模型'''
    username = db.Column(db.Text, unique=True, nullable=False, primary_key=True)
    password = db.Column(db.Text, nullable=False)
    permission_dict = {'visitor': 0, 'user': 1, 'admin': 2}
    permission = db.Column(db.Integer, default=permission_dict['user'])


def clear_db():
    db.drop_all()
    db.create_all()
    add_some_notes()
    add_some_users()
    add_some_comments()


def add_some_notes():
    note1 = Note(title='1', body='222222222222222222222222222222222222222',
                 author='aaa', published_datetime=datetime.datetime(2021, 2, 27, 16, 44, 0))
    note2 = Note(title='a', body='c', author='d', published_datetime=datetime.datetime.now(), permission=1)
    note3 = Note(title='管理员の秘密',
                 body=u'吶吶吶，米娜桑，扣祢起哇，瓦込西二刺猿の焼酒嚏!あああ，辻我仞一-起守択，最好の二刺猿肥!吶吶，不憧我的，愚蠢の人炎們呵，果畔那塞，我二刺猿の焼酒是不会和祢有共同語言的jio豆麻袋,'
                      u'込祥子垪活有什幺錯喝?吶,告泝我呵。搜嚆,祢仞已経不喜炊了呵..真是冷酷の人昵,果鮮納塞,止祢看到不愉快のな西了。像我送祥的人,果然消失就好了昵。也午只有在二次元的世界里,'
                      u'オ有真正的美好存在的肥,'
                      u'吶?ねぇねぇねぇ，果然灰悪了呵，帯jio不，瓦込西，二刺猿の焼酒!博古哇zeidei'
                      u'不会人輸!米娜桑!吶!瓦込西二刺猿ぁぁ!哦晦吻扣賽伊弓斯!吶吶吶!米娜桑!我要幵劫了~一キ打去咢死!诶多诶多~「多洗忒」?为什么要「妄.图.抹.杀」这样的「自己」呢?★('
                      u'笑)呐、「中二病的你」也好、「二次元的你」也好....「全部」daisuki~呐~二次元民那赛高desuwa'
                      u'!今后也.请.多.多.指.教.喔?~啊啊……是♡鲜♡血♡の♡味♡道♡呐♡~！（眯眼笑）kukuku'
                      u'——汝の「血」、会是什么样的「气味」呢☆？诶多多~说着说着有些期待了呢♪品尝「挚·爱·之·人」の「鲜血」什么的~嘛……如果是「你」的话，一定可以的!',
                 author='d', published_datetime=datetime.datetime.now(), permission=2, view_num=1, comment_num=1)
    note4 = Note(title='love', body='python', author='very', published_datetime=datetime.datetime.today())
    db.session.add(note1)
    db.session.add(note2)
    db.session.add(note3)
    db.session.add(note4)
    db.session.commit()


def add_some_users():
    user1 = User(username='1', password='1')
    user2 = User(username='admin', password='admin', permission=2)
    user3 = User(username='2', password='123456')
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()


def add_some_comments():
    commemt = Comment(belong_to=3, nickname='niconiconi', body='草（一种植物）')
    db.session.add(commemt)
    db.session.commit()


@app.route('/api/get_note_list', methods=['GET'])
def get_note_list():
    note_list = []
    for note in Note.query.all():
        if note.permission == 0:
            note.body = note.body[0:20]  # 截取每篇帖子的前20个字，避免帖子内容全部泄露
        elif note.permission == 1:
            note.body = '需要登录以查看'
        elif note.permission == 2:
            note.body = '需要管理员权限以查看'
        note_list.append(note.to_json())
    note_list.reverse()
    return jsonify(note_list)


@app.route('/api/add_comment', methods=['POST'])
def add_comment():
    data = json.loads(str(request.data, 'utf-8'))
    belong_to = data['belong_to']
    nickname = data['nickname']
    body = data['body']
    comment = Comment(belong_to=belong_to, nickname=nickname, body=body)
    db.session.add(comment)

    note = Note.query.filter_by(id=belong_to).first()
    note.comment_num += 1
    db.session.commit()
    return '添加成功！'


@app.route('/api/get_comment')
def get_comment():
    belong_to = request.args.get('belong_to')
    comment_list = []
    for comment in Comment.query.filter_by(belong_to=belong_to).all():
        comment_list.append(comment.to_json())
    return jsonify(comment_list)


@app.route('/api/get_note')
def get_note():
    note_id = request.args.get('note_id')
    username = request.args.get('username')
    password = request.args.get('password')
    note = Note.query.filter_by(id=note_id).first()
    if note:
        _note = note.to_json()
        if note.permission > 0:
            if not username or not password:
                _note['body'] = '请先登录'
                return _note
            user = User.query.filter_by(username=username, password=password).first()
            if not user:
                _note['body'] = '用户名或密码错误'
                return _note
            if user.permission < note.permission:
                _note['body'] = '权限不足'
                return _note
        note.view_num += 1
        db.session.commit()
        return _note
    else:
        return '404'


@app.route('/api/update_note', methods=['POST'])
def update_note():
    '''note_id为-1时，添加帖子，其余为修改帖子'''
    data = json.loads(str(request.data, 'utf-8'))
    note_id = data['id']
    title = data['title']
    body = data['body']
    published_datetime = datetime.datetime.now()
    author = data['username']
    password = data['password']
    permission = data['permission']
    user = User.query.filter_by(username=author, password=password).first()
    if not user:
        return '用户名或密码错误'
    if note_id == -1:
        note = Note(title=title, body=body, published_datetime=published_datetime, author=author, permission=permission)
        db.session.add(note)
        db.session.commit()
    else:
        note = Note.query.filter_by(id=note_id).first()
        if not note:
            return '找不到相应的帖子~'
        note.title = title
        note.body = body
        note.published_datetime = published_datetime
        note.author = 'testtesttest'
        db.session.commit()
    return '提交成功！'


@app.route('/api/register_user', methods=['GET'])
def register_user():
    username = request.args.get('username')
    password = request.args.get('password')
    if User.query.filter_by(username=username).first():
        return '用户名%s已存在！' % username
    user = User.query.filter_by(password=password).first()
    if user:
        return '密码已被%s占用！' % user.username

    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return '注册成功！'


@app.route('/register.html')
def register_page():
    return app.send_static_file('register.html')


@app.route('/read_note/<int:note_id>')
def read_note_page(note_id):
    return app.send_static_file('read_note.html')


@app.route('/post_note.html')
def post_note_page():
    return app.send_static_file('post_note.html')


@app.route('/')
def index_page():
    # return render_template('index.html',get_note_list=get_note_list)
    return app.send_static_file('index.html')


if __name__ == '__main__':
    # clear_db()
    app.run(debug=True)
