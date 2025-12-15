import sys
import os
# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, Candidate, VoterCode, Settings
import csv
import os

def reset_db():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()

        # Add Candidates
        print("Adding candidates...")
        candidates = [
            Candidate(name="Партия Яшьлек, кандидат - Камалетдинов Райян Эмилевич, цифровизация, социальные проекты, широкие возможности для молодежи"),
            Candidate(name="Партия Хайп движение, кандидат - Якунин Никита, коммуникация, удовольствие от учебы, невероятный хайп"),
            Candidate(name="Партия «Лидеры перемен», кандидат - Аглиуллина Аделина, объединение и сплочение кафедры, оснащение оргтехникой для студентов.")
        ]
        db.session.add_all(candidates)

        # Add Settings
        print("Adding settings...")
        db.session.add(Settings(key='voting_status', value='closed'))

        # Import Codes
        print("Importing codes...")
        if os.path.exists('codes.csv'):
            with open('codes.csv', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    code = row.get('code')
                    if code:
                        db.session.add(VoterCode(code=code))
                print(f"Imported {count} codes.")

        db.session.commit()
        print("Database reset complete.")

if __name__ == '__main__':
    reset_db()
