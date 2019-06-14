from argparse import ArgumentParser
from collections import defaultdict
import glob
import os
import random
import shutil
import subprocess
import tempfile
import uuid


def wav_fp_to_num_samples(wav_fp):
  wav_size = os.stat(wav_fp).st_size
  # Subtract header
  data_size = wav_size - 44
  assert data_size % 2 == 0
  nsamps = data_size // 2
  return nsamps


def tx1_fp_ensemble_complete(tx1_fp):
  with open(tx1_fp, 'r') as f:
    tx1 = f.read()
  p1 = 'P1_NOTEON' in tx1
  p2 = 'P2_NOTEON' in tx1
  tr = 'TR_NOTEON' in tx1
  no = 'NO_NOTEON' in tx1
  return p1 and p2 and tr and no


if __name__ == '__main__':
  parser = ArgumentParser()

  parser.add_argument('wav_dirs', type=str, nargs='+')
  parser.add_argument('--anon_dir', type=str)
  parser.add_argument('--nclips', type=int)
  parser.add_argument('--slice_len', type=float)
  parser.add_argument('--seed', type=int)

  parser.set_defaults(
      wav_dirs=[],
      anon_dir=None,
      nclips=None,
      slice_len=5,
      seed=0)

  args = parser.parse_args()

  # Randomize (consistently)
  random.seed(args.seed)

  # Gather waveforms of at least slice_len
  slice_len_samps = int(round(args.slice_len * 44100.))
  method_tag_to_fns = {}
  method_tag_to_dir = {}
  print('-' * 80)
  for d in args.wav_dirs:
    method_tag = os.path.split(d)[1]
    fps = sorted(glob.glob(os.path.join(d, '*.wav')))
    fps = [fp for fp in fps if wav_fp_to_num_samples(fp) >= slice_len_samps]
    fps = [fp for fp in fps if tx1_fp_ensemble_complete(fp.replace('.tx1.wav', '.tx1.txt'))]
    fns = ['.'.join(os.path.split(fp)[1].split('.')[:-1]) for fp in fps]
    random.shuffle(fns)

    print(method_tag, len(fps))

    if len(fps) < args.nclips:
      print('Warning: not enough clips from {} ({})'.format(method_tag, len(fps)))
    nsamp = min(args.nclips, len(fps))

    method_tag_to_fns[method_tag] = random.sample(fns, nsamp)
    method_tag_to_dir[method_tag] = d

  # Create output directory
  if os.path.isdir(args.anon_dir):
    shutil.rmtree(args.anon_dir)
  os.makedirs(args.anon_dir)
  hit_mp3_dir = os.path.join(args.anon_dir, 'mp3s')
  os.makedirs(hit_mp3_dir)

  # Strip revealing information (create UUIDs)
  uuids = set()
  uuid_key = []
  method_tag_to_uuids = defaultdict(list)
  for method_tag, fns in method_tag_to_fns.items():
    for fn in fns:
      wav_fp = os.path.join(method_tag_to_dir[method_tag], '{}.wav'.format(fn))
      nsamps = wav_fp_to_num_samples(wav_fp)
      nsecs = nsamps / 44100.
      offset = random.random() * (nsecs - args.slice_len)

      wav_uuid = uuid.uuid4().hex
      assert wav_uuid not in uuids
      uuid_key.append('{},{},{}'.format(wav_uuid, method_tag, fn))
      uuids.add(wav_uuid)
      method_tag_to_uuids[method_tag].append(wav_uuid)

      out_fp = os.path.join(hit_mp3_dir, '{}.mp3'.format(wav_uuid))
      with tempfile.NamedTemporaryFile() as f:
        shutil.copyfile(wav_fp, f.name)
        cmd = 'ffmpeg -i {} -ss {} -t {} -q:a 2 -loglevel error -hide_banner -y {}'.format(f.name, offset, args.slice_len, out_fp)
        res = subprocess.call(cmd, shell=True)
        if res > 0:
          raise Exception('ffmpeg failed')

  # Create key
  with open(os.path.join(args.anon_dir, 'key.csv'), 'w') as f:
    f.write('\n'.join(sorted(uuid_key)))
