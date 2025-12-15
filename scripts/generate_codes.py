import csv
import sys
import secrets

# Usage: python generate_codes.py input.csv output_codes.csv
# input.csv may contain list of emails/names but we only need to produce codes

if len(sys.argv) < 3:
    print('Usage: generate_codes.py input.csv output_codes.csv')
    sys.exit(1)

input_path = sys.argv[1]
output_path = sys.argv[2]

codes = []
with open(input_path, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        # create a 12-char urlsafe token
        token = secrets.token_urlsafe(9)
        codes.append((row[0] if row else '', token))

with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['identifier', 'code'])
    writer.writerows(codes)

print(f'Generated {len(codes)} codes to {output_path}')

