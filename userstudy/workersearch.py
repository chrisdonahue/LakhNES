import csv
import sys

wid = sys.argv[1]

for csv_fp in ['./04_08_00_clip_5s/turi_turker_final.csv', './04_08_00_clip_5s/pref_turker_final.csv']:
  with open(csv_fp, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      rwid = row['WorkerId']
      if rwid == wid:
        print(csv_fp)
        print(row['AssignmentId'])
        sys.exit(0)
