import sys
import os
# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, Candidate

with app.app_context():
    Candidate.query.delete()
    candidates = [
        Candidate(name="Партия Яшьлек, кандидат - Камалетдинов Райян Эмилевич, цифровизация, социальные проекты, широкие возможности для молодежи"),
        Candidate(name="Партия Хайп движение, кандидат - Якунин Никита, коммуникация, удовольствие от учебы, невероятный хайп"),
        Candidate(name="Партия «Лидеры перемен», кандидат - Аглиуллина Аделина, объединение и сплочение кафедры, оснащение оргтехникой для студентов.")
    ]
    db.session.add_all(candidates)
    db.session.commit()
    print("Candidates reset.")
