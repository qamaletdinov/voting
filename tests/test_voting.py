import unittest
import werkzeug
# Monkeypatch for werkzeug 3.0+ compatibility with older Flask
if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "3.0.0"

from datetime import datetime, timedelta
from app import app, db, VoterCode, Candidate

class VotingTestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing if used
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

        # Create candidates
        self.c1 = Candidate(name='Candidate 1')
        self.c2 = Candidate(name='Candidate 2')
        db.session.add_all([self.c1, self.c2])

        # Create codes
        self.valid_code = VoterCode(code='valid123')
        self.used_code = VoterCode(code='used123', used=True)
        db.session.add_all([self.valid_code, self.used_code])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def set_voting_time(self, start_offset_days=0, end_offset_days=0):
        # Helper to set env vars for time
        now = datetime.utcnow()
        start = now + timedelta(days=start_offset_days)
        end = now + timedelta(days=end_offset_days)
        fmt = "%Y-%m-%dT%H:%M:%S"
        os.environ['VOTE_START'] = start.strftime(fmt)
        os.environ['VOTE_END'] = end.strftime(fmt)

    def test_vote_counting(self):
        import os
        # Set time to be open (start yesterday, end tomorrow)
        self.set_voting_time(-1, 1)

        # Check initial votes
        c1 = Candidate.query.filter_by(name='Candidate 1').first()
        self.assertEqual(c1.votes, 0)

        # Vote for Candidate 1
        response = self.app.post(f'/vote/valid123', data={'candidate': c1.id}, follow_redirects=True)
        self.assertIn('Спасибо! Ваш голос принят.', response.get_data(as_text=True))

        # Check votes incremented
        c1 = Candidate.query.filter_by(name='Candidate 1').first()
        self.assertEqual(c1.votes, 1)

        # Check code marked as used
        vc = VoterCode.query.filter_by(code='valid123').first()
        self.assertTrue(vc.used)

    def test_invalid_code(self):
        response = self.app.post('/enter', data={'code': 'invalid'}, follow_redirects=True)
        self.assertIn('Код не найден', response.get_data(as_text=True))

    def test_used_code(self):
        response = self.app.post('/enter', data={'code': 'used123'}, follow_redirects=True)
        self.assertIn('Код уже использован', response.get_data(as_text=True))

    def test_voting_closed_future(self):
        import os
        # Voting starts tomorrow
        self.set_voting_time(1, 2)

        response = self.app.post('/enter', data={'code': 'valid123'}, follow_redirects=True)
        self.assertIn('Голосование закрыто', response.get_data(as_text=True))

    def test_voting_closed_past(self):
        import os
        # Voting ended yesterday
        self.set_voting_time(-2, -1)

        response = self.app.post('/enter', data={'code': 'valid123'}, follow_redirects=True)
        self.assertIn('Голосование закрыто', response.get_data(as_text=True))

if __name__ == '__main__':
    import os
    unittest.main()
