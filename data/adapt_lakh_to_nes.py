import itertools
import os

import pretty_midi
pretty_midi.pretty_midi.MAX_TICK = 1e16
import random

nes_ins_name_to_min_pitch = {
    'p1': 33,
    'p2': 33,
    'tr': 21
}
nes_ins_name_to_max_pitch = {
    'p1': 108,
    'p2': 108,
    'tr': 108
}


def instrument_is_monophonic(ins):
  # Ensure sorted
  notes = ins.notes
  last_note_start = -1
  for n in notes:
    assert n.start >= last_note_start
    last_note_start = n.start

  monophonic = True
  for i in range(len(notes) - 1):
    n0 = notes[i]
    n1 = notes[i + 1]
    if n0.end > n1.start:
      monophonic = False
      break
  return monophonic


def emit_nesmdb_midi_examples(
    midi_fp,
    output_dir,
    min_num_instruments=1,
    filter_mid_len_below_seconds=5.,
    filter_mid_len_above_seconds=600.,
    filter_mid_bad_times=True,
    filter_ins_max_below=21,
    filter_ins_min_above=108,
    filter_ins_duplicate=True,
    output_include_drums=True,
    output_max_num=16,
    output_max_num_seconds=180.):
  midi_name = os.path.split(midi_fp)[1].split('.')[0]

  if min_num_instruments <= 0:
    raise ValueError()

  # Ignore unusually large MIDI files (only ~25 of these in the dataset)
  if os.path.getsize(midi_fp) > (512 * 1024): #512K
    return

  try:
    midi = pretty_midi.PrettyMIDI(midi_fp)
  except:
    return

  # Filter MIDIs with extreme length
  midi_len = midi.get_end_time()
  if midi_len < filter_mid_len_below_seconds or midi_len > filter_mid_len_above_seconds:
    return

  # Filter out negative times and quantize to audio samples
  for ins in midi.instruments:
    for n in ins.notes:
      if filter_mid_bad_times:
        if n.start < 0 or n.end < 0 or n.end < n.start:
          return
      n.start = round(n.start * 44100.) / 44100.
      n.end = round(n.end * 44100.) / 44100.

  instruments = midi.instruments

  # Filter out drum instruments
  drums = [i for i in instruments if i.is_drum]
  instruments = [i for i in instruments if not i.is_drum]

  # Filter out instruments with bizarre ranges
  instruments_normal_range = []
  for ins in instruments:
    pitches = [n.pitch for n in ins.notes]
    min_pitch = min(pitches)
    max_pitch = max(pitches)
    if max_pitch >= filter_ins_max_below and min_pitch <= filter_ins_min_above:
      instruments_normal_range.append(ins)
  instruments = instruments_normal_range
  if len(instruments) < min_num_instruments:
    return

  # Sort notes for polyphonic filtering and proper saving
  for ins in instruments:
    ins.notes = sorted(ins.notes, key=lambda x: x.start)
  if output_include_drums:
    for ins in drums:
      ins.notes = sorted(ins.notes, key=lambda x: x.start)

  # Filter out polyphonic instruments
  instruments = [i for i in instruments if instrument_is_monophonic(i)]
  if len(instruments) < min_num_instruments:
    return

  # Filter out duplicate instruments
  if filter_ins_duplicate:
    uniques = set()
    instruments_unique = []
    for ins in instruments:
      pitches = ','.join(['{}:{:.1f}'.format(str(n.pitch), n.start) for n in ins.notes])
      if pitches not in uniques:
        instruments_unique.append(ins)
        uniques.add(pitches)
    instruments = instruments_unique
    if len(instruments) < min_num_instruments:
      return

  # TODO: Find instruments that have a substantial fraction of the number of total notes
  """
  min_notes_frac = num_instruments_to_min_notes_frac(num_instruments)
  total_num_notes = sum([len(i.notes) for i in instruments])
  instruments = [i for i in instruments if (len(i.notes) / float(total_num_notes)) >= min_notes_frac]
  num_instruments = len(instruments)
  if num_instruments < min_num_instruments:
    return
  """

  # TODO: ensure tempo and other metadata is alright

  # TODO: ensure number of notes is alright

  # Create assignments of MIDI instruments to NES instruments
  num_instruments = len(instruments)
  if num_instruments == 1:
    instrument_perms = [(0, -1, -1), (-1, 0, -1), (-1, -1, 0)]
  elif num_instruments == 2:
    instrument_perms = [(-1, 0, 1), (-1, 1, 0), (0, -1, 1), (0, 1, -1), (1, -1, 0), (1, 0, -1)]
  elif num_instruments > 32:
    instrument_perms = list(itertools.permutations(random.sample(range(num_instruments), 32), 3))
  else:
    instrument_perms = list(itertools.permutations(range(num_instruments), 3))

  if len(instrument_perms) > output_max_num:
    instrument_perms = random.sample(instrument_perms, output_max_num)

  num_drums = len(drums) if output_include_drums else 0
  instrument_perms_plus_drums = []
  for perm in instrument_perms:
    selection = -1 if num_drums == 0 else random.choice(range(num_drums))
    instrument_perms_plus_drums.append(perm + (selection,))
  instrument_perms = instrument_perms_plus_drums

  # Emit midi files
  for i, perm in enumerate(instrument_perms):
    # Create MIDI instruments
    p1_prog = pretty_midi.instrument_name_to_program('Lead 1 (square)')
    p2_prog = pretty_midi.instrument_name_to_program('Lead 2 (sawtooth)')
    tr_prog = pretty_midi.instrument_name_to_program('Synth Bass 1')
    no_prog = pretty_midi.instrument_name_to_program('Breath Noise')
    p1 = pretty_midi.Instrument(program=p1_prog, name='p1', is_drum=False)
    p2 = pretty_midi.Instrument(program=p2_prog, name='p2', is_drum=False)
    tr = pretty_midi.Instrument(program=tr_prog, name='tr', is_drum=False)
    no = pretty_midi.Instrument(program=no_prog, name='no', is_drum=True)

    # Filter out invalid notes
    perm_mid_ins_notes = []
    for mid_ins_id, nes_ins_name in zip(perm, ['p1', 'p2', 'tr', 'no']):
      if mid_ins_id < 0:
        perm_mid_ins_notes.append(None)
      else:
        if nes_ins_name == 'no':
          mid_ins = drums[mid_ins_id]
          mid_ins_notes_valid = mid_ins.notes
        else:
          mid_ins = instruments[mid_ins_id]
          mid_ins_notes_valid = [n for n in mid_ins.notes if n.pitch >= nes_ins_name_to_min_pitch[nes_ins_name] and n.pitch <= nes_ins_name_to_max_pitch[nes_ins_name]]
        perm_mid_ins_notes.append(mid_ins_notes_valid)
    assert len(perm_mid_ins_notes) == 4

    # Calculate length of this ensemble
    start = None
    end = None
    for notes in perm_mid_ins_notes:
      if notes is None or len(notes) == 0:
        continue
      ins_start = min([n.start for n in notes])
      ins_end = max([n.end for n in notes])
      if start is None or ins_start < start:
        start = ins_start
      if end is None or ins_end > end:
        end = ins_end
    if start is None or end is None:
      continue

    # Clip if needed
    if (end - start) > output_max_num_seconds:
      end = start + output_max_num_seconds

    # Create notes
    for mid_ins_notes, nes_ins_name, nes_ins in zip(perm_mid_ins_notes, ['p1', 'p2', 'tr', 'no'], [p1, p2, tr, no]):
      if mid_ins_notes is None:
        continue

      if nes_ins_name == 'no':
        random_noise_mapping = [random.randint(1, 16) for _ in range(128)]

      last_nend = -1
      for ni, n in enumerate(mid_ins_notes):
        nvelocity = n.velocity
        npitch = n.pitch
        nstart = n.start
        nend = n.end

        # Drums are not necessarily monophonic so we need to filter
        if nes_ins_name == 'no' and nstart < last_nend:
          continue
        last_nend = nend

        assert nstart >= start
        if nend > end:
          continue
        assert nend <= end

        nvelocity = 1 if nes_ins_name == 'tr' else int(round(1. + (14. * nvelocity / 127.)))
        assert nvelocity > 0
        if nes_ins_name == 'no':
          npitch = random_noise_mapping[npitch]
        nstart = nstart - start
        nend = nend - start

        nes_ins.notes.append(pretty_midi.Note(nvelocity, npitch, nstart, nend))

    # Add instruments to MIDI file
    midi = pretty_midi.PrettyMIDI(initial_tempo=120, resolution=22050)
    midi.instruments.extend([p1, p2, tr, no])

    # Create indicator for end of song
    eos = pretty_midi.TimeSignature(1, 1, end - start)
    midi.time_signature_changes.append(eos)

    # Save MIDI file
    out_fp = '{}_{}.mid'.format(midi_name, str(i).zfill(3))
    out_fp = os.path.join(output_dir, out_fp)
    midi.write(out_fp)


if __name__ == '__main__':
  import glob
  import shutil
  import multiprocessing

  import numpy as np
  import pretty_midi
  from tqdm import tqdm

  midi_fps = glob.glob('./lakh/lmd_full/*/*.mid*')
  out_dir = './out'

  if os.path.isdir(out_dir):
    shutil.rmtree(out_dir)
  os.makedirs(out_dir)

  def _task(x):
    emit_nesmdb_midi_examples(x, out_dir)

  with multiprocessing.Pool(8) as p:
    r = list(tqdm(p.imap(_task, midi_fps), total=len(midi_fps)))
