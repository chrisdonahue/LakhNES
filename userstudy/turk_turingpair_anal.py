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

      if uuid_to_method[a_uuid] == 'real_data':
        answer = 'A'
        method = uuid_to_method[b_uuid]
        assert uuid_to_method[b_uuid] != 'real_data'
      else:
        answer = 'B'
        method = uuid_to_method[a_uuid]
        assert uuid_to_method[b_uuid] == 'real_data'

      user_answer = row['Answer.pair_{}_pref'.format(i)]

      if a_method == 'control' or b_method == 'control':
        assert a_method == 'real_data' or b_method == 'real_data'
        if user_answer != answer:
          wid_to_control_failed[wid] += 1
        wid_to_control_tot[wid] += 1

      wid_to_task[wid].append((a_method, b_method, answer, user_answer))

      i += 1

wid_to_control_pct = {}
for wid in wids:
  wid_to_control_pct[wid] = float(wid_to_control_failed[wid]) / wid_to_control_tot[wid] 

wids_failed_control = set()
banned = set()
for wid, pct in sorted(wid_to_control_pct.items(), key=lambda x:x[1]):
  tot = wid_to_control_tot[wid]
  print(wid, tot, pct)
  if pct > 0. or tot < 6:
    wids_failed_control.add(wid)
  if pct >= 0.05:
    banned.add(wid)

csv = [['Worker ID', 'UPDATE-NES-Banned']]
csv += [[wid, '1'] for wid in list(banned)]
with open('banned.csv', 'w') as f:
  f.write('\n'.join([','.join(l) for l in csv]))

print(wid_to_count)
print(wids_failed_control)
print('{} tot {} failed'.format(len(wids), len(wids_failed_control)))
print('{} mean musical experience'.format(np.mean(list(wid_to_mexp.values()))))
print('{} mean chiptune experience'.format(np.mean(list(wid_to_cexp.values()))))
print('-' * 80)

method_to_correct = Counter()
method_to_tot = Counter()
for wid, tasks in wid_to_task.items():
  if wid in wids_failed_control:
    continue
  for a_method, b_method, answer, user_answer in tasks:
    if a_method == 'real_data':
      method = b_method
    else:
      method = a_method

    method_to_correct[method] += int(answer == user_answer)
    method_to_tot[method] += 1

for method in method_to_correct.keys():
  correct = method_to_correct[method]
  tot = method_to_tot[method]

  acc = correct / float(tot)
  stderr = np.sqrt((acc * (1-acc))/float(tot))
  print(method, correct, tot, acc, stderr)
