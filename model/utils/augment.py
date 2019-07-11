from collections import defaultdict

_INSTAG2MIN = {
    'P1': 33,
    'P2': 33,
    'TR': 21,
    'NO': 1
}

_INSTAG2MAX = {
    'P1': 108,
    'P2': 108,
    'TR': 108,
    'NO': 16
}


def nesmdb_select_instruments(events, ins=['P1', 'P2', 'TR', 'NO']):
  if len(ins) == 4:
    return events

  events_selected = []
  for event in events:
    event_tokens = event.split('_')
    if event_tokens[0] == 'WT' or event_tokens[0] in ins:
      events_selected.append(event)

  return events_selected


def nesmdb_switch_pulse(events):
  events_pulse_switched = []
  for event in events:
    tokens = event.split('_')
    if tokens[0] == 'P1':
      tokens[0] = 'P2'
    elif tokens[0] == 'P2':
      tokens[0] = 'P1'
    events_pulse_switched.append('_'.join(tokens))

  return events_pulse_switched


def nesmdb_transpose(events, transpose_amt=0, instag2min=_INSTAG2MIN, instag2max=_INSTAG2MAX):
  if transpose_amt == 0:
    return events

  events_transposed = []
  for event in events:
    event_tokens = event.split('_')
    if event_tokens[1] == 'NOTEON' and event_tokens[0] in ['P1', 'P2', 'TR']:
      instag = event_tokens[0]
      midi_note = int(event_tokens[2])
      new_midi_note = midi_note + transpose_amt
      if new_midi_note >= instag2min[instag] and new_midi_note <= instag2max[instag]:
        events_transposed.append('{}_NOTEON_{}'.format(instag, new_midi_note))
    else:
      events_transposed.append(event)

  return events_transposed


def nesmdb_stretch(events, playback_speed=1.):
  if playback_speed == 1:
    return events
  if playback_speed < 0:
    raise ValueError()

  stretch_amt = 1. / playback_speed

  samp_events = defaultdict(list)
  samp = 0
  for event in events:
    if event[:2] == 'WT':
      samp += int(event[3:])
    else:
      samp_events[samp].append(event)

  samp_events_stretched = defaultdict(list)
  for samp, events in sorted(samp_events.items(), key=lambda x: x[0]):
    new_samp = int(round(samp * stretch_amt))
    samp_events_stretched[new_samp].extend(events)

  events_stretched = []
  last_samp = 0
  for samp, events in sorted(samp_events_stretched.items(), key=lambda x: x[0]):
    wait_amt = samp - last_samp
    assert samp == 0 or wait_amt > 0
    if wait_amt > 0:
      events_stretched.append('WT_{}'.format(wait_amt))
    events_stretched.extend(events)
    last_samp = samp

  return events_stretched


if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('input_txt_fp', type=str)
  parser.add_argument('output_txt_fp', type=str)
  parser.add_argument('--select_instruments', type=str)
  parser.add_argument('--transpose_amt', type=int)
  parser.add_argument('--playback_speed', type=float)
  parser.add_argument('--pulse_switch', action='store_true')

  parser.set_defaults(
      select_instruments='P1,P2,TR,NO',
      transpose_amt=0,
      playback_speed=1.,
      pulse_switch=False)

  args = parser.parse_args()

  with open(args.input_txt_fp, 'r') as f:
    events = f.read().strip().splitlines()

  events = nesmdb_select_instruments(events, args.select_instruments.split(','))
  if args.pulse_switch:
    events = nesmdb_switch_pulse(events)
  events = nesmdb_transpose(events, args.transpose_amt)
  events = nesmdb_stretch(events, args.playback_speed)

  with open(args.output_txt_fp, 'w') as f:
    f.write('\n'.join(events))
