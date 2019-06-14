from collections import defaultdict, Counter
from csv import DictReader
import sys
import numpy as np

key_fp, results_fp = sys.argv[1:]

uuid_to_method = {}
with open(key_fp, 'r') as f:
  lines = f.read().strip().splitlines()
for l in lines:
  uuid, method, _ = l.split(',')
  uuid_to_method[uuid] = method

wid_to_count = Counter()
wid_to_mexp = {}
wid_to_cexp = {}
wid_to_time = {}
wid_to_task = defaultdict(list)
wids = set()
wid_to_control_tot = Counter()
wid_to_control_failed = Counter()
with open(results_fp, 'r') as f:
  reader = DictReader(f)
  for row in reader:
    wid = row['WorkerId']
    wids.add(wid)
    wid_to_count[wid] += 1

    mexp = int(row['Answer.musical_expertise'])
    cexp = int(row['Answer.chiptune_expertise'])

    if wid in wid_to_mexp and mexp != wid_to_mexp[wid]:
      pass
      #print(wid, mexp, wid_to_mexp[wid])

    wid_to_mexp[wid] = mexp
    wid_to_cexp[wid] = cexp

    i = 0
    while 'Input.pair_{}_clip_a_url'.format(i) in row:
      a_url = row['Input.pair_{}_clip_a_url'.format(i)]
      b_url = row['Input.pair_{}_clip_b_url'.format(i)]

      a_uuid = a_url.split('/')[-1].split('.')[0]
      b_uuid = b_url.split('/')[-1].split('.')[0]

      a_method = uuid_to_method[a_uuid]
      b_method = uuid_to_method[b_uuid]
      assert a_method != b_method
      if a_method == 'txl_scratch_noaug' or b_method == 'txl_scratch_noaug':
        i += 1
        continue

      user_answer = row['Answer.pair_{}_pref'.format(i)]

      if a_method == 'control' or b_method == 'control':
        assert a_method == 'real_data' or b_method == 'real_data'
        answer = 'A' if a_method == 'real_data' else 'B'
        if user_answer != answer:
          wid_to_control_failed[wid] += 1
        wid_to_control_tot[wid] += 1
      else:
        wid_to_task[wid].append((a_method, b_method, user_answer))

      i += 1

wid_to_control_pct = {}
for wid in wids:
  wid_to_control_pct[wid] = float(wid_to_control_failed[wid]) / wid_to_control_tot[wid] 

banned = set()
wids_failed_control = set()
for wid, pct in sorted(wid_to_control_pct.items(), key=lambda x:x[1]):
  tot = wid_to_control_tot[wid]
  print(wid, tot, pct)
  if pct > 0.05:
    wids_failed_control.add(wid)
  if pct >= 0.05:
    banned.add(wid)

csv = [['Worker ID', 'UPDATE-NES-Banned']]
for wid in list(banned):
  csv.append((wid, '1'))
with open('banned.csv', 'w') as f:
  f.write('\n'.join([','.join(p) for p in csv]))

print(wid_to_count)
print(wids_failed_control)
print('{} tot {} failed'.format(len(wids), len(wids_failed_control)))
print('{} mean musical experience'.format(np.mean(list(wid_to_mexp.values()))))
print('{} mean chiptune experience'.format(np.mean(list(wid_to_cexp.values()))))

method_to_wins = Counter()
method_to_loses = Counter()
nexcellent = 0
ntot = 0
nbad = 0
nbadtot = 0
for wid, tasks in wid_to_task.items():
  if wid in wids_failed_control:
    continue
  for a_method, b_method, answer in tasks:
    if answer == 'A':
      winner = a_method
      loser = b_method
    else:
      assert answer == 'B'
      winner = b_method
      loser = a_method

    if loser == 'real_data' and winner == 'txl_finetune_nu':
      nexcellent += 1
      ntot += 1
    if winner == 'real_data' and loser == 'txl_finetune_nu':
      ntot += 1

    if loser == 'real_data' and winner == 'lstm_flat_large':
      nbad += 1
      nbadtot += 1
    if winner == 'real_data' and loser == 'lstm_flat_large':
      nbadtot += 1

    method_to_wins[winner] += 1
    method_to_loses[loser] += 1

print(nexcellent, ntot)
print(nbad, nbadtot)
print('-' * 80)
methods = set(method_to_wins.keys() + method_to_loses.keys())
for method in methods:
  loses = method_to_loses[method]
  wins = method_to_wins[method]
  print(method, wins, loses)

print('-' * 80)
tot = sum(method_to_wins.values())
for method, wins in method_to_wins.items():
  acc = wins / float(tot)
  stderr = np.sqrt((acc * (1-acc))/float(tot))
  print(method, tot, acc, stderr)
