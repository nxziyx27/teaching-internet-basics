from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'internet_basics.db')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret-key')

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

COURSE = [
    {
        'day': 1, 'title': '🌐 Introduction to Internet', 'color': '#2196F3',
        'subtitle': 'Learn what the Internet is and how it helps us in daily life.',
        'image': 'day1_internet.png',
        'content': 'The Internet is a worldwide network that connects millions of computers, phones and other devices. It allows people to communicate, learn, work, shop and share information online.',
        'points': ['The Internet connects computers and devices all over the world.', 'It helps us communicate with people.', 'We can learn new things online.', 'We can work, shop and share information.'],
        'examples': 'Google • YouTube • Wikipedia • Gmail • Online Shopping'
    },
    {
        'day': 2, 'title': '🌍 Web Browsers', 'color': '#00A896',
        'subtitle': 'Learn how to open and use websites with a web browser.',
        'image': 'day2_browser.png',
        'content': 'A web browser is software used to access and view websites on the Internet. Popular browsers include Google Chrome, Microsoft Edge, Mozilla Firefox and Safari.',
        'points': ['A browser is used to access websites.', 'Chrome, Edge, Firefox and Safari are browsers.', 'A website address is typed into the address bar.', 'Press Enter to open the website.'],
        'examples': 'Chrome • Edge • Firefox • Safari'
    },
    {
        'day': 3, 'title': '🔍 Search Engines', 'color': '#F4A261',
        'subtitle': 'Learn how to search for useful information on the Internet.',
        'image': 'day3_search.png',
        'content': 'A search engine helps us find information on the Internet. Popular search engines include Google, Bing and Yahoo. Use simple and clear keywords and read results carefully.',
        'points': ['A search engine helps us find information.', 'Use simple and clear keywords.', 'Read the search results carefully.', 'Do not open suspicious results or links.'],
        'examples': 'Google • Bing • Yahoo'
    },
    {
        'day': 4, 'title': '📧 Email', 'color': '#E76F9A',
        'subtitle': 'Learn how to send and receive messages using email.',
        'image': 'day4_email.png',
        'content': 'Email means Electronic Mail. It allows us to send and receive messages through the Internet. To send an email, compose a message, enter the receiver, subject and message, then click Send.',
        'points': ['Email means Electronic Mail.', 'Email can be used to send and receive messages.', "Always check the receiver's email address.", 'Never share your email password.'],
        'examples': 'Gmail • Outlook • Yahoo Mail'
    },
    {
        'day': 5, 'title': '🛡️ Internet Safety', 'color': '#8E5CC2',
        'subtitle': 'Learn how to stay safe and protect your personal information online.',
        'image': 'day5_safety.png',
        'content': 'Internet safety means using the Internet carefully and protecting personal information. Never share OTPs or passwords, avoid unknown links, use strong passwords and think before clicking.',
        'points': ['Never share OTPs or passwords.', 'Avoid unknown or suspicious links.', 'Use strong passwords and protect personal information.', 'Logout when using a public computer.', 'STOP • THINK • CHECK before clicking.'],
        'examples': 'OTP • Password • Links • Personal Information'
    }
]

QUESTIONS = [
    ('🌐 What is the Internet?', ['A worldwide network connecting computers', 'A mobile application', 'A type of printer', 'A computer game'], 'A worldwide network connecting computers'),
    ('🌍 Which application is used to browse websites?', ['Calculator', 'Google Chrome', 'Camera', 'Notepad'], 'Google Chrome'),
    ('🔍 You want to find information about Mumbai. What should you use?', ['Music Player', 'Calculator', 'Paint', 'Search Engine'], 'Search Engine'),
    ('📧 What is Email mainly used for?', ['Taking photographs', 'Sending and receiving messages online', 'Playing offline games', 'Editing videos'], 'Sending and receiving messages online'),
    ("📩 In an email, where do you enter the receiver's email address?", ['To', 'Subject', 'Message', 'Attachment'], 'To'),
    ('📝 What should you write in the Subject of an email?', ['Your OTP', 'Your password', 'The main topic of the email', 'Your phone PIN'], 'The main topic of the email'),
    ('📎 You want to send a photo with an email. What can you use?', ['Attachment', 'Subject', 'Search Bar', 'Browser History'], 'Attachment'),
    ('🔐 Which action is safest while using the Internet?', ['Never share your OTP or password', 'Click every unknown link', 'Share your password with friends', 'Use the same password everywhere'], 'Never share your OTP or password'),
    ("⚠️ You receive a message saying 'You won a prize! Click this unknown link.' What should you do?", ['Give your OTP', 'Click immediately', 'Share it with friends', 'Avoid clicking the link'], 'Avoid clicking the link'),
    ('🔑 Which password is the strongest?', ['123456', 'password', 'N@ziya123!', 'abcdef'], 'N@ziya123!')
]


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS learners (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, course_started TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS quiz_attempts (id INTEGER PRIMARY KEY AUTOINCREMENT, learner_id INTEGER, score INTEGER, total_questions INTEGER, percentage REAL, result TEXT, attempt_date TEXT, FOREIGN KEY (learner_id) REFERENCES learners(id));
    CREATE TABLE IF NOT EXISTS lesson_progress (id INTEGER PRIMARY KEY AUTOINCREMENT, learner_id INTEGER NOT NULL, lesson_number INTEGER NOT NULL, completed_at TEXT, UNIQUE(learner_id, lesson_number), FOREIGN KEY (learner_id) REFERENCES learners(id));
    ''')
    conn.commit(); conn.close()


def learner_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'learner_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped


def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return wrapped


def current_learner():
    if 'learner_id' not in session: return None
    conn = db(); row = conn.execute('SELECT * FROM learners WHERE id=?', (session['learner_id'],)).fetchone(); conn.close(); return row


def progress_for(learner_id):
    conn = db(); rows = conn.execute('SELECT lesson_number FROM lesson_progress WHERE learner_id=? ORDER BY lesson_number', (learner_id,)).fetchall(); conn.close(); return [r['lesson_number'] for r in rows]


def stats_for(learner_id):
    conn = db()
    attempts = conn.execute('SELECT COUNT(*) c FROM quiz_attempts WHERE learner_id=?', (learner_id,)).fetchone()['c']
    best = conn.execute('SELECT MAX(percentage) v FROM quiz_attempts WHERE learner_id=?', (learner_id,)).fetchone()['v']
    latest = conn.execute('SELECT * FROM quiz_attempts WHERE learner_id=? ORDER BY id DESC LIMIT 1', (learner_id,)).fetchone()
    conn.close(); return attempts, best, latest


@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'learner_id' in session else url_for('login'))


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name','').strip(); email = request.form.get('email','').strip().lower()
        conn = db(); learner = conn.execute('SELECT * FROM learners WHERE name=? AND email=?', (name, email)).fetchone(); conn.close()
        if learner:
            session.clear(); session['learner_id'] = learner['id']; session['student_name'] = learner['name']; return redirect(url_for('dashboard'))
        flash('Learner not found. Please register first.', 'error')
    return render_template('login.html', title='Learner Login')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name','').strip(); email = request.form.get('email','').strip().lower()
        if not name or not email: flash('Please enter name and email.', 'error'); return render_template('register.html', title='Register')
        now = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        try:
            conn=db(); conn.execute('INSERT INTO learners(name,email,course_started,created_at) VALUES(?,?,?,?)',(name,email,now,now)); conn.commit(); learner_id=conn.execute('SELECT id FROM learners WHERE email=?',(email,)).fetchone()['id']; conn.close()
            session.clear(); session['learner_id']=learner_id; session['student_name']=name; flash('Registration successful!', 'success'); return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError:
            flash('An account with this email already exists. Please login.', 'error')
    return render_template('register.html', title='Register')


@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))


@app.route('/dashboard')
@learner_required
def dashboard():
    learner=current_learner(); completed=progress_for(learner['id']); attempts,best,latest=stats_for(learner['id']); return render_template('dashboard.html', title='Dashboard', learner=learner, completed=completed, attempts=attempts, best=best, latest=latest, total_lessons=5)


@app.route('/course/<int:day>')
@learner_required
def course_day(day):
    if day < 1 or day > 5: return redirect(url_for('course_day', day=1))
    completed=progress_for(session['learner_id']); lesson=COURSE[day-1]; return render_template('course.html', title=lesson['title'], lesson=lesson, completed=completed)


@app.route('/course/<int:day>/complete', methods=['POST'])
@learner_required
def complete_day(day):
    if 1 <= day <= 5:
        conn=db(); conn.execute('INSERT OR IGNORE INTO lesson_progress(learner_id,lesson_number,completed_at) VALUES(?,?,?)',(session['learner_id'],day,datetime.now().strftime('%d-%m-%Y %H:%M:%S'))); conn.commit(); conn.close(); flash(f'Day {day} marked as completed!', 'success')
    return redirect(url_for('course_day', day=min(day+1,5)))


@app.route('/quiz', methods=['GET','POST'])
@learner_required
def quiz():
    if request.method == 'POST':
        score=0; unanswered=[]
        for i,(_,_,answer) in enumerate(QUESTIONS,1):
            selected=request.form.get(f'q{i}')
            if not selected: unanswered.append(i)
            elif selected == answer: score += 1
        if unanswered:
            flash('Please answer all 10 questions before submitting.', 'error'); return render_template('quiz.html', title='Quiz', questions=QUESTIONS)
        percentage=score/len(QUESTIONS)*100; result='PASSED' if percentage >= 70 else 'FAILED'
        conn=db(); conn.execute('INSERT INTO quiz_attempts(learner_id,score,total_questions,percentage,result,attempt_date) VALUES(?,?,?,?,?,?)',(session['learner_id'],score,len(QUESTIONS),percentage,result,datetime.now().strftime('%d-%m-%Y %H:%M:%S'))); conn.commit(); conn.close()
        return render_template('quiz_result.html', title='Quiz Result', score=score, total=len(QUESTIONS), percentage=percentage, result=result)
    return render_template('quiz.html', title='Quiz', questions=QUESTIONS)


@app.route('/certificate')
@learner_required
def certificate():
    attempts,best,latest=stats_for(session['learner_id'])
    if not latest or latest['percentage'] < 70: flash('Complete the quiz and score at least 70% to access the certificate.', 'error'); return redirect(url_for('dashboard'))
    learner=current_learner(); return render_template('certificate.html', title='Certificate', learner=learner, latest=latest, issued=datetime.now().strftime('%d %B %Y'))


@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        if request.form.get('username') == ADMIN_USERNAME and request.form.get('password') == ADMIN_PASSWORD:
            session['admin']=True; return redirect(url_for('admin'))
        flash('Invalid admin credentials.', 'error')
    return render_template('admin_login.html', title='Admin Login')


@app.route('/admin/logout')
def admin_logout(): session.pop('admin',None); return redirect(url_for('login'))


@app.route('/admin')
@admin_required
def admin():
    conn=db(); learners=conn.execute('''SELECT l.id,l.name,l.email,COUNT(q.id) attempts,MAX(q.score) best_score,MAX(q.percentage) best_percentage FROM learners l LEFT JOIN quiz_attempts q ON l.id=q.learner_id GROUP BY l.id ORDER BY l.id DESC''').fetchall(); total=conn.execute('SELECT COUNT(*) c FROM learners').fetchone()['c']; quiz_count=conn.execute('SELECT COUNT(*) c FROM quiz_attempts').fetchone()['c']; conn.close(); return render_template('admin.html', title='Admin Dashboard', learners=learners,total=total,quiz_count=quiz_count)


with app.app_context(): init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
