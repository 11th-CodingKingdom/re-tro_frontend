from flask import Flask, render_template, jsonify, request, session
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "qwertyuiop"
bcrypt = Bcrypt(app)

client = MongoClient('mongodb://test:test@54.144.213.113:27017')
db = client.retro

# HTML 화면 보여주기
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login_status')
def login_status():
    if 'userID' in session:
        id = session['userID']
    else:
        id = ""
    return jsonify({'id': id})


@app.route('/main/chart', methods=['GET'])
def main_chart():
    chart_year = int(request.args.get('chart_year'))
    datas = list(db.musics.find({'rank_type':"AG", 'year':chart_year},{'_id': False}).limit(6))
    musics = []
    for music in datas:
        music.pop('albumID', None)
        music.pop('genre', None)
        music.pop('Region', None)
        music.pop('like', None)
        music.pop('rank_type', None)
        music.pop('year', None)
        musics.append(music)

    return jsonify({'music_list': musics})

@app.route('/login_page')
def login_page():
    return render_template('index-login.html')

@app.route('/login', methods=['POST'])
def login():
    id = request.form['id']
    pw = request.form['pw']
    information = db.users.find_one({'id':id}, {'_id': False})

    if information != None:
        if bcrypt.check_password_hash(information['pw'], pw):
            session['userID'] = id
            msg = "로그인 성공!"
        else:
            msg = "ID 혹은 비밀번호를 확인하세요"
    else:
        msg = "ID 혹은 비밀번호를 확인하세요"

    return jsonify({'msg': msg})

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')

@app.route('/regist_page')
def regist_page():
    return render_template('index-signup.html')

@app.route('/regist', methods=['POST'])
def regist():
    name = request.form['name']
    email = request.form['email']
    id = request.form['id']
    pw = bcrypt.generate_password_hash(request.form['pw'])
    pwCheck = request.form['pwCheck']
    likeMusic = []
    preferenceResult =""

    if db.users.find_one({'name': name}, {'_id': False}) != None:
        msg = "동일한 사용자가 존재합니다."

    elif email.find("@") == -1:
        msg = "올바른 이메일을 입력하세요"

    elif db.users.find_one({'id': id}, {'_id': False}) != None:
        msg = "입력하신 ID는 다른 사용자가 사용중입니다."

    elif len(request.form['pw']) < 10:
        msg = "비밀번호는 10자리 이상이어야 합니다."

    elif bcrypt.check_password_hash(pw, pwCheck) != True:
        msg = "비밀번호 입력을 다시 확인하세요."

    else:
        information = {'id': id, 'pw': pw, 'email': email, 'name': name, 'likeMusic':likeMusic, 'preferenceResult': preferenceResult}
        db.users.insert_one(information)
        msg = "회원가입 완료!"

    return jsonify({'msg': msg})

@app.route('/userinfo', methods=['GET'])
def mypage_info():
    id = request.args.get('id')
    userinfo = db.users.find_one({'id':id}, {'_id':False})
    userinfo.pop('pw',None)
    userinfo.pop('id',None)
    return jsonify({'userinfo': userinfo})

@app.route('/userinfo', methods=['POST'])
def mypage_infoex():
    id = request.form['id']
    pw = request.form['pw']
    email_new = request.form['email_new']
    information = db.users.find_one({'id':id}, {'_id': False})
    if information != None:
        if bcrypt.check_password_hash(information['pw'], pw):
            db.users.update_one({'id':id}, {"$set":{"email":email_new}})
            msg = "회원정보 수정이 완료되었습니다."
        else:
            msg = '비밀번호를 다시 확인해주세요'
    else:
        msg = "로그인 상태가 아닙니다."
    return jsonify({'msg': msg})

@app.route('/userinfo/pw', methods=['POST'])
def mypage_pwex():
    id = request.form['id']
    pw = request.form['pw']
    pw_new = bcrypt.generate_password_hash(request.form['pw_new'])
    pwCheck_new = request.form['pwCheck_new']
    information = db.users.find_one({'id':id}, {'_id': False})

    if information != None:
        if bcrypt.check_password_hash(information['pw'], pw):
            if bcrypt.check_password_hash(pw_new, pwCheck_new):
                db.users.update_one({'id':id}, {"$set":{"pw":pw_new}})
                msg = "비밀번호 변경이 완료되었습니다."
            else :
                msg = "비밀번호 입력을 다시 확인하세요."
        else:
            msg = '기존 비밀번호를 다시 확인하세요'
    else:
        msg = "로그인 상태가 아닙니다."
    return jsonify({'msg': msg})

@app.route('/userinfo/withdraw', methods=['POST'])
def mypage_withdraw():
    id = request.form['id']
    pw = request.form['pw']
    information = db.users.find_one({'id':id}, {'_id': False})
    if information != None:
        if bcrypt.check_password_hash(information['pw'], pw):
            db.users.delete_one({'id':id})
            msg = "회원탈퇴가 완료되었습니다."
        else:
            msg = '비밀번호를 다시 확인해주세요.'
    else:
        msg = "로그인 상태가 아닙니다."
    return jsonify({'msg': msg})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)