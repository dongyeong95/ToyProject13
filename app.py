from flask import Flask, render_template, request, jsonify, url_for
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb+srv://toy:toy@cluster0.aowjbzf.mongodb.net/?retryWrites=true&w=majority')
#db = client.users

db = client['board']
boards = db['boards']
#boards.insert_one({"text": 'Test!'})

#test_board = boards.find_one({"text": 'Test!'})



@app.route('/')
def home():
    writing_list = list(boards.find())

    return render_template('board_list.html', data=writing_list)

@app.route('/create-page')
def home2():
    return render_template('board_writing.html')

@app.route('/board', methods=["GET"])
def check():
    print('되나???????')
    print(request.args.get('_id'))
    _id = request.args.get('_id')
    board= boards.find_one({'_id': int(_id)})
    print(board)
    return render_template('detail_board.html', board=board)


@app.route("/create", methods=["POST"])
def create():
    title_receive = request.form['title']
    #name_receive= request.form['name']
    comment_receive = request.form['comment']
    writing_list = list(boards.find({}, {'_id': False}))
    count = len(writing_list) + 1

    doc = {
        '_id': count,
        'title': title_receive,
        'name': '-',
        'comment': comment_receive
    }

    boards.insert_one(doc)
    return render_template('board_list.html')



@app.route("/writing", methods=["POST"])
def writing_get():
    writingpage = list(boards.find())
    return jsonify(writingpage)



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)