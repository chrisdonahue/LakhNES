from __future__ import print_function

from tx1_midi import tx1_to_midi
from tx2_midi import tx2_to_midi

import nesmdb.convert
from scipy.io.wavfile import write as wavwrite
from SimpleXMLRPCServer import SimpleXMLRPCServer

def tx1_to_wav(tx1_fp, out_fp, midi_downsample_rate=None):
  if midi_downsample_rate == 0:
    midi_downsample_rate = None

  print('(Rate {}) {}->{}'.format(midi_downsample_rate, tx1_fp, out_fp))
  with open(tx1_fp, 'r') as f:
    tx1 = f.read()
  midi = tx1_to_midi(tx1)
  wav = nesmdb.convert.midi_to_wav(midi, midi_downsample_rate)
  wavwrite(out_fp, 44100, wav)
  print('Done: {}'.format(wav.shape))
  return True


def tx2_to_wav(tx2_fp, out_fp, midi_downsample_rate=None):
  if midi_downsample_rate == 0:
    midi_downsample_rate = None

  print('(Rate {}) {}->{}'.format(midi_downsample_rate, tx2_fp, out_fp))
  with open(tx2_fp, 'r') as f:
    tx2 = f.read()
  midi = tx2_to_midi(tx2)
  wav = nesmdb.convert.midi_to_wav(midi, midi_downsample_rate)
  wavwrite(out_fp, 44100, wav)
  print('Done: {}'.format(wav.shape))
  return True


if __name__ == '__main__':
  import sys

  if len(sys.argv) < 2:
    port = 1337
  else:
    try:
      port = int(sys.argv[1])
    except:
      raise Exception('Invalid port specified')

  server = SimpleXMLRPCServer(('localhost', port))
  server.register_function(tx1_to_wav, 'tx1_to_wav')
  server.register_function(tx2_to_wav, 'tx2_to_wav')
  print('Opened chiptune synthesis server on port {}'.format(port))
  server.serve_forever()
