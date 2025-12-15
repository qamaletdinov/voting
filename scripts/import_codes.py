import csv
import sys
import os
# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, VoterCode, app

if len(sys.argv) < 2:
    print('Usage: import_codes.py codes.csv')
    sys.exit(1)

path = sys.argv[1]

with app.app_context():
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            code = row.get('code')
            if not code:
                continue
            if VoterCode.query.filter_by(code=code).first():
                continue
            vc = VoterCode(code=code)
            db.session.add(vc)
            count += 1
        db.session.commit()
    print(f'Imported {count} codes')
