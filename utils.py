import numpy as np
import torch
import torch.nn.functional as F

def load_vocab(vocab_fp):
  idx2sym = ['<S>']
  wait_amts = []
  with open(vocab_fp, 'r') as f:
    for line in f:
      idx2sym.append(line.strip().split(',')[-1])
      if line[:2] == 'WT':
        wait_amts.append(int(line[3:]))
  sym2idx = {s:i for i, s in enumerate(idx2sym)}
  return idx2sym, sym2idx, wait_amts


def quantize_wait_event(wait_event):
  wait_time = int(wait_event[3:])
  diff = float('inf')
  candidate = None

  for t in wait_amts:
    cur_diff = abs(wait_time - t)
    if cur_diff < diff:
      diff = cur_diff
      candidate = t
    else:
      break
  return 'WT_{}'.format(candidate)


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
