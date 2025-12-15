from app import app, db, VoterCode, Candidate, Settings

with app.app_context():
    try:
        c_count = Candidate.query.count()
        vc_count = VoterCode.query.count()
        s = Settings.query.filter_by(key='voting_status').first()
        status = s.value if s else 'closed'

        print(f"Candidates: {c_count}")
        print(f"Voter Codes: {vc_count}")
        print(f"Voting Status: {status}")
    except Exception as e:
        print(f"Error: {e}")

