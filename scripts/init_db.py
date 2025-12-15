from app import app, db, Candidate

with app.app_context():
    db.create_all()

    if Candidate.query.count() == 0:
        candidates = [
            Candidate(name="Иванов Иван Иванович"),
            Candidate(name="Петров Петр Петрович"),
            Candidate(name="Сидоров Сидор Сидорович")
        ]
        db.session.add_all(candidates)
        db.session.commit()
        print("Database initialized and candidates added.")
    else:
        print("Database already contains candidates.")

