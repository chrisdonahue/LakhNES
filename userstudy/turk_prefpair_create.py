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
  all_methods = set(method_to_uuids.keys()) - set(['control'])
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
    control = sample_without_replacement('control', args.ncontrol)
    real = sample_without_replacement('real_data', args.ncontrol)

    control_pairs = [list(p) for p in zip(control, real)]
    for p in control_pairs:
      random.shuffle(p)

    method_pairs = [random.sample(all_methods, 2) for _ in range(args.nperhit - args.ncontrol)]
    method_pairs = [(sample_without_replacement(a, 1)[0], sample_without_replacement(b, 1)[0]) for a, b in method_pairs]

    pairs = control_pairs + method_pairs
    random.shuffle(pairs)

    print('-' * 80)
    hit = []
    for a, b in pairs:
      a_method, b_method = uuid_to_method[a], uuid_to_method[b]
      print(a_method, b_method)
      method_to_n[a_method] += 1
      method_to_n[b_method] += 1
      hit.append(a)
      hit.append(b)

    hits.append(','.join([URL_TEMPL.format(anon_dir_name, i) for i in hit]))

  print('-' * 80)
  for method, n in method_to_n.items():
    print(method, float(n) / sum(method_to_n.values()))

  with open(args.csv_fp, 'w') as f:
    f.write('\n'.join(hits))
