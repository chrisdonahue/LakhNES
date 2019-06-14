import numpy as np
import torch
import torch.nn.functional as F

class TxlSimpleSampler:
  def __init__(self, model, device, tgt_len=1, mem_len=896, ext_len=0):
    if tgt_len != 1:
      raise ValueError()
    if ext_len != 0:
      raise ValueError()
    self.model = model
    self.model.eval()
    self.model.reset_length(1, ext_len, mem_len)
    self.device = device
    self.reset()
    
          
  def reset(self):
    self.mems = []
    self.generated = []
  
  
  @torch.no_grad()
  def sample_next_token_updating_mem(self, last_token=None, temp=1., topk=None, exclude_eos=True):
    last_token = last_token if last_token is not None else 0

    # Ensure that user is always passing 0 on first call
    if len(self.generated) == 0:
      assert len(self.mems) == 0
      if last_token != 0:
        raise Exception()

    # Ensure that user isn't passing 0 after first call
    if last_token == 0 and len(self.generated) > 0:
      raise Exception()

    # Sanitize sampling params
    if temp < 0:
      raise ValueError()
    if topk is not None and topk < 1:
      raise ValueError()
    
    # Append last input token because we've officially selected it
    self.generated.append(last_token)
    
    # Create input array
    _inp = [last_token]
    _inp = np.array(_inp, dtype=np.int64)[:, np.newaxis]
    inp = torch.from_numpy(_inp).to(self.device)

    # Evaluate the model, saving its memory.
    ret = self.model.forward_generate(inp, *self.mems)
    all_logits, self.mems = ret[0], ret[1:]
    
    # Select last timestep, only batch item
    logits = all_logits[-1, 0]
    
    if exclude_eos:
      logits = logits[1:]
    
    # Handle temp 0 (argmax) case
    if temp == 0:
      probs = torch.zeros_like(logits)
      probs[logits.argmax()] = 1.
    else:    
      # Apply temperature spec
      if temp != 1:
        logits /= temp

      # Compute softmax
      probs = F.softmax(logits, dim=-1)
    
    if exclude_eos:
      probs = F.pad(probs, [1, 0])
    
    # Select top-k if specified
    if topk is not None:
      _, top_idx = torch.topk(probs, topk)
      mask = torch.zeros_like(probs)
      mask[top_idx] = 1.
      probs *= mask
      probs /= probs.sum()
    
    # Sample from probabilities
    token = torch.multinomial(probs, 1)
    token = int(token.item())
    
    return token, probs


if __name__ == '__main__':
  import os

  MODELS = [
    '/home/cdonahue/txl/transformer-xl/models/papermodels/finetune400k',
  ]
  OUT_DIRS = [
    './testchurr'
  ]
  EXTS = [
      '.tx1.txt',
  ]

  USE_CUDA = True
  GEN_LEN = 2048

  for model_dir, sample_dir, ext in zip(MODELS, OUT_DIRS, EXTS):
    model_fp = os.path.join(model_dir, 'model.pt')
    vocab_fp = os.path.join(model_dir, 'vocab.txt')
    if not os.path.isdir(sample_dir):
      os.makedirs(sample_dir)

    device = torch.device("cuda" if USE_CUDA else "cpu")

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
    idx2sym = ['<S>']
    with open(vocab_fp, 'r') as f:
      for line in f:
        idx2sym.append(line.strip().split(',')[-1])
    sym2idx = {s:i for i, s in enumerate(idx2sym)}

    for memlen in [512]:
      for temp in [0.9, 0.92, 0.94, 0.96, 0.98, 1.]:
        for topk in [16, 32, 64]:
          for i in range(64):
            out_fn = 'memlen_{}_temp_{}_topk_{}_i_{}{}'.format(memlen, temp, topk, i, ext)
            out_fp = os.path.join(sample_dir, out_fn)
            if os.path.exists(out_fp):
              print(out_fp)
              continue
            sampler = TxlSimpleSampler(model, device, mem_len=memlen)
            seq = [0]
            for _ in range(GEN_LEN):
              token, _ = sampler.sample_next_token_updating_mem(seq[-1], temp=temp, topk=topk)
              seq.append(token)
            with open(out_fp, 'w') as f:
              f.write('\n'.join(idx2sym[t] for t in seq[1:]))
