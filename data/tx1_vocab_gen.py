import json
def quantize_wait(wait):
    wait = min(wait, 100000)

    if wait > 10000:
      wait = 1000 * int(round(float(wait) / 1000) + 1e-4)
    elif wait > 1000:
      wait = 100 * int(round(float(wait) / 100) + 1e-4)
    elif wait > 100:
      wait = 10 * int(round(float(wait) / 10) + 1e-4)

    return wait

vocab = []

# Add waits
last_wait = None
for i in range(1, 100001):
  wait = quantize_wait(i)
  if last_wait is None or wait != last_wait:
    vocab.append('WT_{}'.format(wait))
    last_wait = wait

# Add notes
with open('min_max_pitches.json', 'r') as f:
  ins_to_range = json.loads(f.read())

for ins in ins_to_range:
  vocab.append('{}_NOTEOFF'.format(ins))
  lo = ins_to_range[ins]['min_pitch']
  hi = ins_to_range[ins]['max_pitch']
  for n in range(lo, hi + 1):
    vocab.append('{}_NOTEON_{}'.format(ins, n))

with open('vocab.txt', 'w') as f:
  f.write('\n'.join(vocab))
