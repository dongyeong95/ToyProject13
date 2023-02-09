from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient
import certifi

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.5dl7iec.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

SECRET_KEY = 'SPARTA'

import jwt

import datetime, timedelta

import hashlib


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('board_list.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})


@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']


    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()


    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})


    if result is not None:

        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=50)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})

    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})




@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:

        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/board_add')
def board_add():
    return render_template('board_add.html')


@app.route('/boardget', methods=["GET"])
def check():
    print(request.args.get('_id'))
    _id = request.args.get('_id')
    board = db.board.find_one({'_id': int(_id)})
    print(board)
    return render_template('board.html', board=board)


@app.route('/board', methods=["GET"])
def board():
    num_receive = request.form['num_give']
    numstr = int(num_receive)
    print(numstr)
    return redirect(url_for('board', num=numstr))


@app.route('/board/modify', methods=["POST"])
def board_modify():
    num_receive = request.form['modify_num_give']
    title_receive = request.form['modify_title_give']
    comment_receive = request.form['modify_comment_give']
    print(num_receive, title_receive, comment_receive)
    print(type(num_receive))
    print(type(title_receive))
    print(type(comment_receive))
    db.board.update_one({'_id': int(num_receive)}, {'$set':{'title':title_receive}})
    db.board.update_one({'_id': int(num_receive)}, {'$set':{'comment':comment_receive}})
    return jsonify({'msg': '수정 완료'})


@app.route('/board/delete', methods=["POST"])
def board_delete():
    num_receive = request.form['delete_num_give']
    print("delete : " + num_receive)
    db.board.delete_one({'_id': int(num_receive)})
    return jsonify({'msg': '삭제 완료'})


@app.route('/show_list', methods=["POST"])
def show_list():
    # comment_list = list(db.board.find({}, {'_id': False}).sort([{'_id', -1}]))
    comment_list = list(db.board.find({}))
    print(comment_list)
    return jsonify(comment_list)


@app.route("/comment_save", methods=["POST"])
def comment_save():
    title_receive = request.form['title_give']
    comment_receive = request.form['comment_give']
    if title_receive == "":
        return jsonify({'msg': '제목을 넣어주세요!'})

    addlist_num = list(db.board.find({}, {'_id': False}))
    count_num = len(addlist_num) + 1

    name = "홍길동"  # test
    name_num = str(count_num)  # test

    doc = {
        '_id': count_num,
        # 이름은 jwt에서 가지고 와야 하는데.... 구글링해야함
        'name': name + name_num,
        'title': title_receive,
        'comment': comment_receive,
    }
    db.board.insert_one(doc)
    return jsonify({'msg': '게시글 등록 완료'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
