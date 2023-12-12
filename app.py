from flask import Flask , render_template ,request ,redirect ,session ,url_for
from data import Articles
from mysql import Mysql
import config
import pymysql
from datetime import timedelta
# print(Articles())
from functools import wraps
import requests
from kakao_controller import Oauth

app = Flask(__name__)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=10)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

mysql = Mysql(password=config.PASSWORD)

def is_loged_in(func):
    @wraps(func)
    def wrap(*args , **kwargs):
        if 'is_loged_in' in session:
            return func(*args , **kwargs)
        else:
            return redirect('/loginst')
    return wrap

@app.route('/' , methods=['GET','POST'])
# @is_loged_in
def index():
    if request.method == "GET":
        os_info = dict(request.headers)
        print(os_info) 
        name = request.args.get("name")
        print(name)
        hello = request.args.get("hello")
        print(hello)
        return render_template('indexst.html',header=f'{name}님 {hello}!!' )
    
    elif request.method == "POST":
        data  = request.form.get("name")
        data_2 = request.form['hello']
        print(data_2)
        return render_template('indexst.html',header= "안녕하세요 김태경입니다.!!!")
    print(session['is_loged_in'])
    return render_template('indexst.html')

@app.route('/hello', methods=['GET', 'POST'])
def hello():
    if request.method =="GET":
        return render_template('hello.html')
    
    elif request.method =="POST":
        name = request.form['name']
        hello = request.form['hello']
        return render_template('indexst.html', name=name , hello = hello)

@app.route('/list', methods=['GET' , 'POST'])
def list():
    if request.method == "GET":
        # data = Articles()
        result = mysql.get_data()
        # print(result)
        return render_template('list.html' , data=result)
    
    elif request.method =="POST":
        title = request.form['title']
        desc = request.form['desc']
        author = request.form['author']
        result = mysql.insert_list(title , desc , author)
        print(result)
        return redirect('/list')

@app.route('/create_list')
def create_list():
        return render_template('dashboard.html')
    


@app.route('/registerst', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        print(username , email , phone , password)
        
        db = pymysql.connect(host=mysql.host, user=mysql.user, db=mysql.db, password=mysql.password, charset=mysql.charset)
        curs = db.cursor()

        sql = f'SELECT * FROM user WHERE email = %s;'
        curs.execute(sql , email)
        
        rows = curs.fetchall()
        print(rows)
        if rows:

            return render_template('registerst.html' , data = 1)
        else:
            result = mysql.insert_user(username, email ,phone,password )
            print(result)
            return redirect('/loginst')
    
    elif request.method == "GET":
        return render_template('registerst.html', data=0)
    
@app.route('/loginst',  methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('loginst.html')
    elif request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        db = pymysql.connect(host=mysql.host, user=mysql.user, db=mysql.db, password=mysql.password, charset=mysql.charset)
        curs = db.cursor()

        sql = f'SELECT * FROM user WHERE email = %s;'
        curs.execute(sql , email)
        
        rows = curs.fetchall()
        print(rows)

        if rows:
            result = mysql.verify_password(password, rows[0][4])
            if result:
                session['is_loged_in'] = True
                session['username'] = rows[0][1]
                return redirect('/')
                # return render_template('index.html', is_loged_in = session['is_loged_in'] , username=session['username'] )
            else:
                return redirect('/login')
        else:
            return render_template('loginst.html')
        
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/facelogin',  methods=['GET', 'POST'])
def facelogin():
    if request.method == "GET":
        return render_template('facelogin.html')
    elif request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        db = pymysql.connect(host=mysql.host, user=mysql.user, db=mysql.db, password=mysql.password, charset=mysql.charset)
        curs = db.cursor()

        sql = f'SELECT * FROM user WHERE email = %s;'
        curs.execute(sql , email)
        
        rows = curs.fetchall()
        print(rows)

        if rows:
            result = mysql.verify_password(password, rows[0][4])
            if result:
                session['is_loged_in'] = True
                session['username'] = rows[0][1]
                return redirect('/')
                # return render_template('index.html', is_loged_in = session['is_loged_in'] , username=session['username'] )
            else:
                return redirect('/facelogin')
        else:
            return render_template('facelogin.html')

@app.route('/edit/<ids>',methods=['GET','POST'])
def edit(ids):
    if request.method == 'GET':
        db = pymysql.connect(host=mysql.host, user=mysql.user, db=mysql.db, password=mysql.password, charset=mysql.charset)
        curs = db.cursor()

        sql = f'SELECT * FROM list WHERE `id` = %s;'
        curs.execute(sql , ids)
        
        rows = curs.fetchall()
        print(rows)
        db.close()
        return render_template('list_edit.html',data = rows)
    
    elif request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        author = request.form['author']

        result = mysql.update_list(ids,title,desc,author)
        print(result)
        return redirect('/list')
    
# @app.route('/login')
# def kakao_sign_in():
#     # 카카오톡으로 로그인 버튼을 눌렀을 때
#     kakao_oauth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
#     return redirect(kakao_oauth_url)

# @app.route('/callback')
# def callback():
#     code = request.args["code"]

#     # 전달받은 authorization code를 통해서 access_token을 발급
#     oauth = Oauth()
#     auth_info = oauth.auth(code)

#     # error 발생 시 로그인 페이지로 redirect
#     if "error" in auth_info:
#         print("에러가 발생했습니다.")
#         return {'message': '인증 실패'}, 404

#     # 아닐 시
#     user = oauth.userinfo("Bearer " + auth_info['access_token'])

#     print(user)
#     kakao_account = user["kakao_account"]
#     profile = kakao_account["profile"]
#     name = profile["nickname"]
#     if "email" in kakao_account.keys():
#         email = kakao_account["email"]
#     else:
#         email = f"{name}@kakao.com"

#     user = user.query.filter(user.name == name).first()

#     # if user is None:
#     #     # 유저 테이블에 추가
#     #     user = user(name, email, generate_hashed_password(name))
#     #     db.session.add(user)
#     #     db.session.commit()

#     #     message = '회원가입이 완료되었습니다.'
#     #     value = {"status": 200, "result": "success", "msg": message}

#     session['email'] = user.email
#     session['isKakao'] = True
#     # message = '로그인에 성공하였습니다.'
#     # value = {"status": 200, "result": "success", "msg": message}

#     return redirect('indexst.html')

# # 꺽쇠로 파람스 처리 <ids>
# @app.route('/delete/<ids>')
# def delete(ids):
#     result = mysql.delete_list(ids)
#     print(result)

#     return redirect('/list')


# 네이버 로그인
@app.route("/naver")
def NaverLogin():
    client_id = "xQblil4Y1DlLCIc7nLfa"
    redirect_uri = "http://localhost:5000/callback"
    url = f"https://nid.naver.com/oauth2.0/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    return redirect(url)
@app.route("/callback")
def callback():
    params = request.args.to_dict()
    code = params.get("code")
    client_id = "xQblil4Y1DlLCIc7nLfa"
    client_secret = "tDRlsSv0cz"
    redirect_uri = "http://localhost:5000/callback"
    token_request = requests.get(f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}")
    token_json = token_request.json()
    print(token_json)
    access_token = token_json.get("access_token")
    profile_request = requests.get("https://openapi.naver.com/v1/nid/me", headers={"Authorization" : f"Bearer {access_token}"},)
    profile_data = profile_request.json()
    print(profile_data)
    # 네이버 접속 시 유저 정보 전달 받기
    naver_name = profile_data['response']['name']
    naver_email = profile_data['response']['email']
    naver_phone = "naver"
    naver_password = profile_data['response']['id']
    # print(naver_name)
    # print(naver_email)
    # print(naver_id)
    # user_naver = mysql.naver_insert_user(naver_id, naver_age, naver_gender, naver_email, naver_name)
    # print(user_naver)
    # print(profile_data['response']['email'])
    # 접속한 유저 정보 중 email정보를 통해 가입여부를 확인
    result  = mysql.naver_email_check(naver_name, naver_email, naver_phone, naver_password)
    print(result)
    return redirect('/')




if __name__ == '__main__':
    app.config['SECRET_KEY'] ='eungok'
    app.run(debug=True)