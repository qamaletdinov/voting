import csv
import os
from app import app, db, VoterCode, Candidate, Settings

def setup():
    with app.app_context():
        # 1. Create tables
        db.create_all()
        
        # 2. Ensure candidates exist
        if Candidate.query.count() == 0:
            candidates = [
                Candidate(name="Партия Яшьлек, кандидат - Камалетдинов Райян Эмилевич, цифровизация, социальные проекты, широкие возможности для молодежи"),
                Candidate(name="Партия Хайп движение, кандидат - Якунин Никита, коммуникация, удовольствие от учебы, невероятный хайп"),
                Candidate(name="Партия «Лидеры перемен», кандидат - Аглиуллина Аделина, объединение и сплочение кафедры, оснащение оргтехникой для студентов.")
            ]
            db.session.add_all(candidates)
        
        # 3. Import codes
        # Clear existing codes to avoid duplicates if we are re-running fully
        # Or just add missing ones. Let's just add missing ones.
        
        if os.path.exists('codes.csv'):
            with open('codes.csv', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    code = row.get('code')
                    if not code:
                        continue
                    if not VoterCode.query.filter_by(code=code).first():
                        vc = VoterCode(code=code)
                        db.session.add(vc)
                        count += 1
            print(f"Imported {count} new codes.")
        
        # 4. Ensure Settings exist
        if not Settings.query.filter_by(key='voting_status').first():
            s = Settings(key='voting_status', value='closed')
            db.session.add(s)
            
        db.session.commit()
        
        with open('setup_done.txt', 'w') as f:
            f.write(f'Setup completed. Candidates: {Candidate.query.count()}, Codes: {VoterCode.query.count()}')

if __name__ == '__main__':
    setup()

