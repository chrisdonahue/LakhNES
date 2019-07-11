import xmlrpc.client

if __name__ == '__main__':
  import sys

  if len(sys.argv) < 3:
    raise Exception('Need two arguments: TX1_IN_FP and WAV_OUT_FP')

  tx_in_fp, wav_out_fp = sys.argv[1:3]

  midi_downsample_rate = 0
  if len(sys.argv) > 3:
    midi_downsample_rate = int(sys.argv[3])

  s = xmlrpc.client.ServerProxy('http://localhost:1337')

  if 'tx1' in tx_in_fp:
    s.tx1_to_wav(tx_in_fp, wav_out_fp, midi_downsample_rate)
  else:
    s.tx2_to_wav(tx_in_fp, wav_out_fp, midi_downsample_rate)
