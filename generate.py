if __name__ == '__main__':
  from argparse import ArgumentParser
  import os
  import sys
  import torch
  import numpy
  import random

  script_dir = os.path.dirname(os.path.abspath(__file__))
  code_model_dir = os.path.abspath(os.path.join(script_dir, 'model'))
  code_utils_dir = os.path.join(code_model_dir, 'utils')
  sys.path.extend([code_model_dir, code_utils_dir])

  from utils import TxlSimpleSampler, load_vocab

  parser = ArgumentParser()

  parser.add_argument('model_dir', type=str, help='Directory with model')
  parser.add_argument('--tx2', action='store_false', dest='tx1')
  parser.add_argument('--out_dir', type=str, help='Output directory')
  parser.add_argument('--cpu', action='store_false', dest='gpu')
  parser.add_argument('--num', type=int, help='Number of samples to generate')
  parser.add_argument('--mem_len', type=int, help='Max length of Transformer memory')
  parser.add_argument('--gen_len', type=int, help='Length of generation')
  parser.add_argument('--temp', type=float, help='Generation temperature')
  parser.add_argument('--topk', type=int, help='Top-k sampling')
  parser.add_argument('--seed', type=int,
    help='Seed for the random number generators, allowing reproducibility')

  parser.set_defaults(
      model_dir=None,
      tx1=True,
      out_dir='./',
      gpu=True,
      num=1,
      mem_len=512,
      gen_len=1024,
      temp=0.95,
      topk=32)

  args = parser.parse_args()

  if(args.seed is not None):
    # https://pytorch.org/docs/stable/notes/randomness.html
    random.seed(args.seed)
    numpy.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.use_deterministic_algorithms(True)

  model_fp = os.path.join(args.model_dir, 'model.pt')
  vocab_fp = os.path.join(args.model_dir, 'vocab.txt')
  if not os.path.isdir(args.out_dir):
    os.makedirs(args.out_dir)
  ext = '.tx1.txt' if args.tx1 else '.tx2.txt'
  device = torch.device('cuda' if args.gpu else 'cpu')

  # Load the best saved model.
  with open(model_fp, 'rb') as f:
    model = torch.load(f)
  model.backward_compatible()
  model = model.to(device)

  # Make sure model uses vanilla softmax.
  if model.sample_softmax > 0:
    raise NotImplementedError()
  if model.crit.n_clusters != 0:
    raise NotImplementedError()

  # Load the vocab.
  idx2sym, _, _ = load_vocab(vocab_fp)

  # Generate.
  for i in range(args.num):
    out_fn = str(i) + ext
    out_fp = os.path.join(args.out_dir, out_fn)
    sampler = TxlSimpleSampler(model, device, mem_len=args.mem_len)
    seq = [0]
    for _ in range(args.gen_len):
      token, _ = sampler.sample_next_token_updating_mem(
          seq[-1], temp=args.temp, topk=args.topk)
      seq.append(token)
    with open(out_fp, 'w') as f:
      f.write('\n'.join(idx2sym[t] for t in seq[1:]))
