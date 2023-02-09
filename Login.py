from flask import Flask, render_template, request, jsonify, url_for, redirect
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb+srv://test:1234@cluster0.4siqk1w.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.users


@app.route('/')
def home():
    return render_template('board_list.html')


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