from flask import Flask,redirect,url_for,render_template,request,flash,jsonify,session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from sqlalchemy import asc,desc
import uuid



app=Flask(__name__,template_folder='../frontend')
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/e_test"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.db"
app.config['SECRET_KEY'] = 'something'
db = SQLAlchemy(app)
Migrate(app,db)
bcrypt = Bcrypt(app)

class Students(db.Model):
       id = db.Column(db.Integer,primary_key=True,unique=True,autoincrement=True)
       user_id = db.Column(db.String(100),unique=True)
       username = db.Column(db.String(100),unique=True)
       email = db.Column(db.String(100),unique=True)
       def __str__(self):
              return self.username
       
class Admin(db.Model):
       id = db.Column(db.Integer,primary_key=True,unique=True,autoincrement=True)
       user_id = db.Column(db.String(100),unique=True)
       username = db.Column(db.String(100),unique=True)
       email = db.Column(db.String(100),unique=True)
       def __str__(self):
              return self.username
              
class Question(db.Model):
       id = db.Column(db.Integer,primary_key=True,unique=True,autoincrement=True)
       
       test_id = db.Column(db.String(100),default=str(uuid.uuid4()))
       question = db.Column(db.String(1000))
       choose_a = db.Column(db.String(100))
       choose_b = db.Column(db.String(100))
       choose_c = db.Column(db.String(100))
       choose_d = db.Column(db.String(100))
       ans = db.Column(db.String(100))
       total_time = db.Column(db.String(100))
       title = db.Column(db.String(100))
       def __str__(self):
              return self.ans
       
class Test_Taken(db.Model):
       id = db.Column(db.Integer,primary_key=True,unique=True,autoincrement=True)
       test_id = db.Column(db.String(100))
       student = db.Column(db.String(100))
       score = db.Column(db.String(100))
       grade = db.Column(db.String(100))
       section = db.Column(db.String(100))
       question = db.Column(db.String(100))
       relative_score = db.Column(db.String(100))
       def __str__(self):
              return self.student
              






@app.route('/')
def home():
       return render_template('index.html')

@app.route('/student/add',methods=['POST','GET'])
def signup():
       username = session.get('admin')
       if not username:
             return redirect('/')
       if request.method == "POST":
              username = request.form['username']
              email = request.form['email']
              user_id = str(uuid.uuid4().int)[:6]
              try:
                     insert = Students(username=username,email=email,user_id=user_id)
                     db.session.add(insert)
                     db.session.commit()
                     flash(f'New user Created id = {user_id}','success')
                     return redirect('/student/add')
              except IntegrityError:
                     flash('User already exists Please use annother username','error')
                     return redirect('/student/add')
       return render_template('admin/add_student.html')       
@app.route('/login',methods=['POST','GET'])
def login():
       if request.method == "POST":
              id = request.form['id']
              print(id)
              get = Students.query.filter_by(user_id=id).first()
              if get:
                     session['student'] = get.username
                     return redirect('/student/dashboard')
              else:
                     flash('no user found','error')
                     return redirect('/login') 
       return render_template('student/login.html')                           
              
@app.route('/admin/add',methods=['POST','GET'])    
def add_a():
       username = session.get('admin')
       if not username:
             return redirect('/')
       if request.method == "POST":
              username = request.form['username']
              email = request.form['email']
              user_id = str(uuid.uuid4().int)[:6]
              try:
                     insert = Admin(username=username,email=email,user_id=user_id)
                     db.session.add(insert)
                     db.session.commit()
                     flash(f'New admin created id={user_id}')
                     return redirect('/admin/add')
              except IntegrityError:
                     flash('user already exists please another username')       
                     return redirect('/admin/add')
       return render_template('admin/add_admin.html')
       
@app.route('/admin/login',methods=["POST",'GET'])
def admin_login():
       if request.method == "POST":
              user_id = request.form['id']
              get = Admin.query.filter_by(user_id=user_id).first()
              if get:
                     session['admin'] = get.username
                     return redirect('/admin/dashboard')
              else:  
                     flash('no admin found')
                     return redirect('/admin/login') 
       return render_template('admin/admin_login.html')    

@app.route("/admin/upload_questions", methods=["POST"])
def upload_questions():
    username = session.get('admin')
    if not username:
       return redirect('/')
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400

        title = data.get("title")
        questions_list = data.get("questions")
        if not title or not questions_list:
            return jsonify({"error": "Title and questions are required"}), 400

        created_questions = []

        for q in questions_list:
            question_text = q.get("question")
            choose_a = q.get("choose_a")
            choose_b = q.get("choose_b")
            choose_c = q.get("choose_c")
            choose_d = q.get("choose_d")
            ans = q.get("ans")
            total_time = q.get("total_time", "")

            if not all([question_text, choose_a, choose_b, choose_c, choose_d, ans]):
                continue

            question = Question(
                question=question_text,
                choose_a=choose_a,
                choose_b=choose_b,
                choose_c=choose_c,
                choose_d=choose_d,
                ans=ans,
                total_time=total_time,
                title=title
            )
            db.session.add(question)
            created_questions.append(question)

        db.session.commit()

        return jsonify({
            "message": f"{len(created_questions)} questions created successfully.",
            "questions": [str(q) for q in created_questions]
        }), 201

    except Exception as e:
        # Always return JSON on error
        return jsonify({"error": str(e)}), 500

@app.route('/admin/upload')
def upload():
       username = session.get('admin')
       if not username:
             return redirect('/')
       return render_template('admin/upload.html')



@app.route('/admin/dashboard')
def dashboard():
       username = session.get('admin')
       if not username:
             return redirect('/')
       total_test = Question.query.group_by(Question.title).count()
       t = total_test if total_test else 0
       total_student = Students.query.count()
       exam_taken = Test_Taken.query.count()
       return render_template('admin/dashboard.html',total_student=total_student,exam_taken=exam_taken,total_test=t)

@app.route('/top/student')
def student():
       username = session.get('admin')
       if not username:
             return redirect('/')
       get = Test_Taken.query.order_by(asc(Test_Taken.relative_score)).group_by(Test_Taken.student).all()
       return render_template('admin/top_student.html',get=get)

@app.route('/uploaded/question')
def uq():
       get = Question.query.with_entities(
        Question.title,
        Question.total_time,
        Question.test_id
    ).group_by(Question.title).all()

    # Count number of questions per title manually
       data = []
       for g in get:
              title = g.title
              total_time = g.total_time
              id = g.test_id
              nq = Question.query.filter_by(title=title).count()  # number of questions in this exam
              data.append({
              "title": title,
              "total_time": total_time,
              "nq": nq,
              "id":id
              })

       return render_template('admin/uploaded.html', get=data)

@app.route('/delete/<name>')
def dele(name):
      get = Question.query.filter_by(title=name).all()
      for q in get:
       db.session.delete(q)
      db.session.commit()
      return redirect('/uploaded/question')

@app.route('/student/dashboard')
def sd():
      username = session.get('student')
      if not username:
             return redirect('/login')
      
      s = Test_Taken.query.filter_by(student=username).count()
      t = Question.query.group_by(Question.title).count()
      highest = Test_Taken.query.order_by(desc(Test_Taken.score)).first()
      total = Test_Taken.query.filter_by(student=student).all()
      a = 0
      v = Test_Taken.query.filter_by(student=student).count()
      g = v if v else 1
      avg = a/int(g)
      for i in total:
            a += int(i)
      return render_template('student/dashboard.html',s=int(s),highest=int(highest.score),p=int(highest.question),t=int(t),total=int(a),avg_score=float(avg))

@app.route('/student/exam')
def ex():
       username = session.get('student')
       if not username:
             return redirect('/login')
       get = Question.query.with_entities(
        Question.title,
        Question.total_time,
        Question.test_id
    ).group_by(Question.title).all()

    # Count number of questions per title manually
       data = []
       for g in get:
              title = g.title
              total_time = g.total_time
              id = g.test_id
              nq = Question.query.filter_by(title=title).count()  # number of questions in this exam
              data.append({
              "title": title,
              "total_time": total_time,
              "nq": nq,
              "id":id
              })

       return render_template('student/exam.html', get=data)

@app.route('/search')
def saa():
       username = session.get('student')
       if not username:
             return redirect('/login')
       search = request.args.get('search')
       get = Question.query.with_entities(
        Question.title,
        Question.total_time,
        Question.test_id
    ).filter(Question.title.ilike(f"%{search}%") | Question.test_id.ilike(f"%{search}%")).group_by(Question.title).all()

    # Count number of questions per title manually
       data = []
       for g in get:
              title = g.title
              total_time = g.total_time
              id = g.test_id
              nq = Question.query.filter_by(title=title).count()  # number of questions in this exam
              data.append({
              "title": title,
              "total_time": total_time,
              "nq": nq,
              "id":id
              })

       return render_template('student/exam.html', get=data)


@app.route('/search/admin')
def saaa():
       search = request.args.get('search')
       get = Question.query.with_entities(
        Question.title,
        Question.total_time,
        Question.test_id
    ).filter(Question.title.ilike(f"%{search}%") | Question.test_id.ilike(f"%{search}%")).group_by(Question.title).all()

    # Count number of questions per title manually
       data = []
       for g in get:
              title = g.title
              total_time = g.total_time
              id = g.test_id
              nq = Question.query.filter_by(title=title).count()  # number of questions in this exam
              data.append({
              "title": title,
              "total_time": total_time,
              "nq": nq,
              "id":id
              })

       return render_template('admin/uploaded.html', get=data)

@app.route('/student/top')
def studentjhgf():
       username = session.get('student')
       if not username:
             return redirect('/login')
       get = Test_Taken.query.order_by(asc(Test_Taken.relative_score)).group_by(Test_Taken.student).all()
       return render_template('student/top_student.html',get=get)

@app.route('/logout')
def logout():
       username = session.get('student')
       if not username:
             return redirect('/login')
       session.pop('student')
       return redirect('/')



@app.route('/get/<id>', methods=['GET', 'POST'])
def gett(id):

    student = session.get('student')
    if not student:
        flash("Please log in first.", "error")
        return redirect('/login')

    questions = Question.query.filter_by(test_id=id).all()

    if request.method == 'POST':

        total_score = 0
        total_questions = len(questions)

        for idx, q in enumerate(questions, start=1):

            student_ans = request.form.get(f'answer_{idx}')

            is_correct = 1 if student_ans == q.ans else 0
            total_score += is_correct

            test_taken = Test_Taken(
                test_id=q.test_id,
                student=student,
                score=is_correct,
                grade='Correct' if is_correct else 'Wrong',
                section='',
                question=q.question,
                relative_score=student_ans   # store selected answer
            )

            db.session.add(test_taken)

        db.session.commit()

        flash(
            f'Quiz submitted! You scored {total_score}/{total_questions}',
            'success'
        )

        return redirect(url_for('review_test', test_id=id))

    return render_template('student/get.html', a=questions)


@app.route('/review/<test_id>')
def review_test(test_id):

    student = session.get('student')

    questions = Question.query.filter_by(
        test_id=test_id
    ).all()

    student_answers = Test_Taken.query.filter_by(
        test_id=test_id,
        student=student
    ).all()

    # student selected answer
    answer_map = {
        i.question: i.relative_score
        for i in student_answers
    }

    return render_template(
        "student/review.html",
        questions=questions,
        answers=answer_map
    )

@app.route('/admin/logout')
def yudt():
      session.pop('admin')
      return redirect('/')




      





              



if __name__ == '__main__':
     
       app.run(port=5000,debug=True)
