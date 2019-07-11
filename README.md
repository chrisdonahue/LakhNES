# LakhNES

## Get the data

LakhNES is first trained on [Lakh MIDI](https://colinraffel.com/projects/lmd/) and then fine tuned on [NES-MDB](https://github.com/chrisdonahue/nesmdb). The MIDI files from these datasets are first converted into a list of musical *events* (words), so that the data is easily ingested into NLP-focused pipelines.

The NES-MDB dataset has been preprocessed into two event-based formats: `TX1` and `TX2`. The [`TX1` format](#tx1-format) only has *composition* information: the notes and their timings. The [`TX2` format](#tx2-format) has *expressive* information: dynamics and timbre information.

You can get the data in `TX1` and `TX2` (**not used in our paper**) formats here:

* (10 MB) [Download](https://drive.google.com/open?id=1WO6guGagqaw22LH32_NEBeavtbaWy_ar "94763d90ba98ca457b64af3c49b1ed7d9e1434e5ef534be34e836c71d4693cbe") NES-MDB in [TX1 Format](#tx1-format)
* (20 MB) [Download](https://drive.google.com/open?id=1ko3LXvotfubZ-C8Xq_K01bWd5NWiduH9 "c787a4e04bcf6439a8674683e66f2b87062383296199f3ae3c0ef66de23c50e4") NES-MDB in [TX2 Format](#tx2-format)

### TX1 Format

TODO

### TX2 Format

TODO

## Generation environment

```
cd LakhNES
virtualenv -p python3 --no-site-packages LakhNES-gen
source LakhNES-gen/bin/activate
```

## Synthesis environment

LakhNES requires the Python package `nesmdb` to synthesize chiptune audio. Unfortunately, `nesmdb` has not been updated to Python 3.

We *strongly* recommend using `virtualenv` to install `nesmdb` and run it as a synthesis server. To do this, run the following commands from this repository:

```
cd LakhNES
virtualenv -p python2.7 --no-site-packages LakhNES-synth
source LakhNES-synth/bin/activate
pip install nesmdb
pip install pretty_midi
python data/synth_server.py 1337
```

This will expose an RPC server on port `1337` with a two methods `tx1_to_wav` and `tx2_to_wav`. Both take a `tx1/tx2 input file path`, a `wav output file path`, and optionally a `MIDI downsample rate`. A lower `MIDI downsample rate` speeds up synthesis but will mess up the rhythms.

Once you [have the data](#get-the-data) and have both your [generation](#generation-environment) and [synthesis](#synthesis-environment) ready, you can test your synthesis environment from another pane:

```
source LakhNES-gen/bin/activate
python data/synth_client.py data/nesmdb_tx1/train/191_Kirby_sAdventure_02_03PlainsLevel.tx1.txt plains_tx1.wav 48
aplay plains_tx1.wav
python data/synth_client.py data/nesmdb_tx2/train/191_Kirby_sAdventure_02_03PlainsLevel.tx2.txt plains_tx2.wav 48
aplay plains_tx2.wav
```
