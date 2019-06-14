if __name__ == '__main__':
  from collections import defaultdict, Counter
  from argparse import ArgumentParser
  import os
  import random

  parser = ArgumentParser()

  parser.add_argument('anon_dir', type=str)
  parser.add_argument('csv_fp', type=str)
  parser.add_argument('--nhits', type=int)
  parser.add_argument('--nperhit', type=int)
  parser.add_argument('--ncontrol', type=int)
  parser.add_argument('--seed', type=int)
  parser.add_argument('--skip_methods', type=str)

  parser.set_defaults(
      anon_dir=None,
      nhits=100,
      nperhit=10,
      ncontrol=2,
      seed=0,
      skip=None)

  args = parser.parse_args()

  skip = set()
  if args.skip_methods is not None:
    skip = set(args.skip_methods.split(','))

  # Randomize (consistently)
  random.seed(args.seed)

  # Parse answer key
  method_to_uuids = defaultdict(list)
  with open(os.path.join(args.anon_dir, 'key.csv'), 'r') as f:
    lines = f.read().strip().splitlines()
    for l in lines:
      uuid, method, _ = l.split(',')
      if method in skip:
        continue
      method_to_uuids[method].append(uuid)
  all_methods = list(set(method_to_uuids.keys()) - set(['control']) - set(['real_data']))
  uuid_to_method = {}
  for method, uuids in method_to_uuids.items():
    for u in uuids:
      uuid_to_method[u] = method
    print(method, len(uuids))

  method_to_uuid_set = defaultdict(set)
  def sample_without_replacement(method, n):
    if len(method_to_uuid_set[method]) < n:
      method_to_uuid_set[method] = set(method_to_uuids[method])
    uuid_set = method_to_uuid_set[method]
    sample = random.sample(uuid_set, n)
    method_to_uuid_set[method] = uuid_set - set(sample)
    return sample

  hits = []
  hit = []
  for i in range(args.nperhit):
    hit.append('pair_{}_clip_a_url'.format(i))
    hit.append('pair_{}_clip_b_url'.format(i))
  hits.append(','.join(hit))

  URL_TEMPL = 'http://deepyeti.ucsd.edu/cdonahue/txlnesmdb/turkhits/{}/mp3s/{}.mp3'
  anon_dir_name = os.path.split(args.anon_dir)[1]

  method_to_n = Counter()
  for i in range(args.nhits):
    print('-' * 80)
    real = sample_without_replacement('real_data', args.nperhit)
    control = sample_without_replacement('control', args.ncontrol)
    methods = [random.choice(all_methods) for _ in range(args.nperhit - args.ncontrol)]
    fake = [sample_without_replacement(m, 1)[0] for m in methods]
    fake = control + fake
    random.shuffle(fake)
    hit = []
    for r, f in zip(real, fake):
      method_to_n[uuid_to_method[r]] += 1
      method_to_n[uuid_to_method[f]] += 1
      if random.random() < 0.5:
        hit.append(r)
        hit.append(f)
      else:
        hit.append(f)
        hit.append(r)
      print(uuid_to_method[hit[-2]], uuid_to_method[hit[-1]])
    hits.append(','.join([URL_TEMPL.format(anon_dir_name, h) for h in hit]))

  print('-' * 80)
  for method, n in method_to_n.items():
    print(method, float(n) / sum(method_to_n.values()))

  with open(args.csv_fp, 'w') as f:
    f.write('\n'.join(hits))
