import os
from app import app, db, VoterCode, Candidate


def test_smoke():
    # Use in-memory sqlite for test
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        c = Candidate(name='Тест')
        db.session.add(c)
        vc = VoterCode(code='testcode')
        db.session.add(vc)
        db.session.commit()

        client = app.test_client()
        # try enter
        r = client.post('/enter', data={'code': 'testcode'}, follow_redirects=True)
        data = r.data.decode('utf-8', errors='ignore')
        assert 'Голосование' in data or 'Голосование закрыто' in data
