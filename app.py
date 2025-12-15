import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load env
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///voting.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ADMIN_CODE'] = os.getenv('ADMIN_CODE', 'admin123')

# Ensure database directory exists
db_url = app.config['SQLALCHEMY_DATABASE_URI']
if db_url.startswith('sqlite:///'):
    db_path = db_url.replace('sqlite:///', '')
    if db_path != ':memory:':
        # Handle relative paths
        if not os.path.isabs(db_path):
            db_path = os.path.join(app.root_path, db_path)

        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir)
                print(f"Created database directory: {db_dir}")
            except OSError as e:
                print(f"Error creating database directory {db_dir}: {e}")

db = SQLAlchemy(app)

class VoterCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(128), unique=True, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    votes = db.Column(db.Integer, default=0)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)

# Ensure DB is created and initialized
with app.app_context():
    try:
        db.create_all()
        if not Settings.query.filter_by(key='voting_status').first():
            db.session.add(Settings(key='voting_status', value='closed'))
            db.session.commit()
    except Exception as e:
        print(f"Database initialization error: {e}")

def vote_open():
    # Check DB for status
    # We need app context if called outside request, but usually called within request
    try:
        s = Settings.query.filter_by(key='voting_status').first()
        return s and s.value == 'open'
    except:
        return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/enter', methods=['GET', 'POST'])
def enter():
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        if not code:
            flash('Введите код')
            return redirect(url_for('enter'))
        vc = VoterCode.query.filter_by(code=code).first()
        if not vc:
            flash('Код не найден')
            return redirect(url_for('enter'))
        if vc.used:
            flash('Код уже использован')
            return redirect(url_for('enter'))
        if not vote_open():
            flash('Голосование закрыто')
            return redirect(url_for('enter'))
        return redirect(url_for('vote', code=code))
    return render_template('enter.html')


@app.route('/vote/<code>', methods=['GET', 'POST'])
def vote(code):
    vc = VoterCode.query.filter_by(code=code).first_or_404()
    if vc.used:
        flash('Код уже использован')
        return redirect(url_for('enter'))
    if not vote_open():
        flash('Голосование закрыто')
        return redirect(url_for('enter'))
    candidates = Candidate.query.all()
    if request.method == 'POST':
        cid = request.form.get('candidate')
        c = Candidate.query.get(int(cid))
        if not c:
            flash('Кандидат не найден')
            return redirect(url_for('vote', code=code))
        # Mark used and count vote
        vc.used = True
        c.votes = c.votes + 1
        db.session.commit()
        flash('Спасибо! Ваш голос принят.')
        return redirect(url_for('index'))
    return render_template('vote.html', candidates=candidates, code=code)


@app.route('/admin/init')
def admin_init():
    # Create DB and some candidates for demo
    db.create_all()
    if Candidate.query.count() == 0:
        # User said they will enter candidates themselves, but init is useful for structure
        pass
    return 'DB Initialized'


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        code = request.form.get('code')
        if code == app.config['ADMIN_CODE']:
            return redirect(url_for('admin_report', code=code))
        flash('Неверный код администратора')
    return render_template('admin_login.html')


@app.route('/admin/report')
def admin_report():
    code = request.args.get('code')
    if code != app.config['ADMIN_CODE']:
        return redirect(url_for('admin_login'))

    candidates = Candidate.query.order_by(Candidate.votes.desc()).all()
    total_votes = sum(c.votes for c in candidates)

    # Get status
    s = Settings.query.filter_by(key='voting_status').first()
    status = s.value if s else 'closed'

    return render_template('admin_report.html', candidates=candidates, total_votes=total_votes, code=code, status=status)

@app.route('/admin/action', methods=['POST'])
def admin_action():
    code = request.form.get('code')
    if code != app.config['ADMIN_CODE']:
        return redirect(url_for('admin_login'))

    action = request.form.get('action')

    if action == 'start':
        s = Settings.query.filter_by(key='voting_status').first()
        if not s:
            s = Settings(key='voting_status', value='open')
            db.session.add(s)
        else:
            s.value = 'open'
        db.session.commit()
        flash('Голосование запущено')

    elif action == 'stop':
        s = Settings.query.filter_by(key='voting_status').first()
        if not s:
            s = Settings(key='voting_status', value='closed')
            db.session.add(s)
        else:
            s.value = 'closed'
        db.session.commit()
        flash('Голосование остановлено')

    elif action == 'reset':
        # Reset votes and codes
        Candidate.query.update({Candidate.votes: 0})
        VoterCode.query.update({VoterCode.used: False})
        db.session.commit()
        flash('Голоса и использование кодов сброшены')

    return redirect(url_for('admin_report', code=code))

if __name__ == '__main__':
    app.run(debug=True)
