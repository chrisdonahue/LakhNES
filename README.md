# LakhNES: Generate 8-bit music with machine learning

<p align="center">
<img src="https://chrisdonahue.com/LakhNES/logo.png" width="50%"/>
</p>

LakhNES ([paper](), [music examples](https://chrisdonahue.com/LakhNES)) is a deep neural network capable of generating music that can be played by the audio synthesis chip on the Nintendo Entertainment System (NES). It was trained on music composed for the NES by humans. Our model takes advantage of transfer learning: we pre-train on the heterogeneous [Lakh MIDI](https://colinraffel.com/projects/lmd/) dataset before fine tuning on the [NES Music Database](https://github.com/chrisdonahue/nesmdb) target domain.

## Using this codebase

### Generating new chiptunes

This codebase primarily functions to allow for the generation of musical material using the pre-trained LakhNES model. LakhNES outputs sequences of musical events which need to be separately synthesized into 8-bit audio. The steps required are as follows:

1. [Set up your model environment](#model-environment)
1. [Set up your audio synthesis environment](#synthesis-environment)
1. [Download a pre-trained checkpoint](#download-checkpoints)
1. [Generate and listen to chiptunes](#generate-new-chiptunes)

### Evaluating pre-trained checkpoints

This codebase also allows you to evaluate pre-trained models to reproduce the paper results. The steps required for this use case are as follows:

1. [Set up your model environment](#model-environment)
1. [Download the pre-trained checkpoints](#download-checkpoints)
1. [Run the eval script](#reproduce-paper-results)

### Training new checkpoints

With this codebase you can also train a new model (though the documentation for this is still being improved):

1. [Set up your model environment](#model-environment)
1. [Download the data](#download-data)
1. [Train a new model](#train-lakhnes)

## Model environment

The model environment requires Python 3 and Pytorch. The development version of Pytorch was `1.0.1.post2`, but hopefully the newest version will continue to work (see [this section](#reproduce-paper-results) for a sanity check).

We recommend using `virtualenv` as you will need a separate environment to perform [audio synthesis](#synthesis-environment).

```
cd LakhNES
virtualenv -p python3 --no-site-packages LakhNES-model
source LakhNES-model/bin/activate
pip install torch==1.0.1.post2 torchvision==0.2.2.post3
```

## Synthesis environment

LakhNES requires the Python package `nesmdb` to synthesize chiptune audio. Unfortunately, `nesmdb` does not support Python 3 (which the rest of this codebase depends on).

We *strongly* recommend using `virtualenv` to install `nesmdb` and run it is a local RPC server. To do this, run the following commands from this repository:

```
cd LakhNES
virtualenv -p python2.7 --no-site-packages LakhNES-synth
source LakhNES-synth/bin/activate
pip install nesmdb
pip install pretty_midi
python data/synth_server.py 1337
```

This will expose an RPC server on port `1337` with two methods: `tx1_to_wav` and `tx2_to_wav`. Both take a `TX1/TX2` input file path, a `WAV` output file path, and optionally a `MIDI` downsampling rate. A lower rate speeds up synthesis but will mess up the rhythms (if not specified, no downsampling will occur).

### (Optional) Test your synthesis environment on human-composed music

If you wish to test your synthesis environment on human-composed music, you first need to [download the data](#download-data). Then, if you have both your [model](#model-environment) and [synthesis](#synthesis-environment) environments ready, you can synthesize a chiptune from Kirby's Adventure:

```
source LakhNES-model/bin/activate
python data/synth_client.py data/nesmdb_tx1/train/191_Kirby_sAdventure_02_03PlainsLevel.tx1.txt plains_tx1.wav 48
aplay plains_tx1.wav
python data/synth_client.py data/nesmdb_tx2/train/191_Kirby_sAdventure_02_03PlainsLevel.tx2.txt plains_tx2.wav 48
aplay plains_tx2.wav
```

## Download checkpoints

Here we provide all of the Transformer-XL checkpoints used for the results in our paper. We recommend using the `LakhNES` checkpoint which was pretrained on Lakh MIDI for 400k batches before fine tuning on NES-MDB. However, the others can also produce interesting results (in particular `NESAug`).

* (147 MB) (**Recommended**) [Download](https://drive.google.com/open?id=1ND27trP3pTAl6eAk5QiYE9JjLOivqGsd "856e2ec6db1568d6712d73703804a518616174aaf6eb419ea763bf7490b0b61c") `LakhNES` (400k steps Lakh pre-training)
* (147 MB) [Download](https://drive.google.com/open?id=19SN-1vxbNhm_i3lMb_swMVeg5PYiQmkF "b4cec0333e30be6bea04fddfef807ca426e7367c64688619b2da085ff5d1fcfb") `Lakh200k` (200k steps Lakh pre-training)
* (147 MB) [Download](https://drive.google.com/open?id=1dmqCQ7qqjfyJF-wK8AYgPqgNRRDjyYmR "1fe9606306e9d1e8511a730ab2e67909a86d76a79e96aa90d49be90e0de75a18") `Lakh100k` (100k steps Lakh pre-training)
* (147 MB) [Download](https://drive.google.com/open?id=13lCurR-OWpqCAu_KehogkAU18-jVm3lU "d137ddc03796bd247d5b200512c0464c1ab33772e7c7511de9e9b2bc7d4a2d83") `NESAug` (No Lakh pre-training but uses data augmentation)
* (147 MB) [Download](https://drive.google.com/open?id=1qgN1PxOdSZ8T-zwLqSRvjIXmdV062J3- "b297c5afedd6f11e5d2d4a57e89887161f29c9dada97af0d367da76b06c43e65") `NES` (No Lakh pre-training or data augmentation)

## Generate new chiptunes

To generate new chiptunes, first [set up your model environment](#model-environment), [download a checkpoint](#download-checkpoints), and [start your synthesis server](#synthesis-environment). Then, run the following:

```
source LakhNES-model/bin/activate
python generate.py \
	<MODEL_DIR> \
	--out_dir ./generated \
	--num 1
python data/synth_client.py ./generated/0.tx1.txt ./generated/0.tx1.wav
aplay ./generated/0.tx1.wav
```

We've also included the IPython notebooks we used to create the continuations of human-composed chiptunes (`continuations.ipynb`) and rhythm accompaniment examples (`accompany_rhythm.ipynb`) as heard on our [examples page](https://chrisdonahue.com/LakhNES).

## Download data

<p align="center">
<img src="https://chrisdonahue.com/LakhNES/tx1.png" width="50%"/>
</p>

LakhNES is first trained on [Lakh MIDI](https://colinraffel.com/projects/lmd/) and then fine tuned on [NES-MDB](https://github.com/chrisdonahue/nesmdb). The MIDI files from these datasets are first converted into a list of musical *events* to adapt them to the Transformer architecture. An example is outlined in the above image.

The NES-MDB dataset has been preprocessed into two event-based formats: `TX1` and `TX2`. The [`TX1` format](#tx1-format) only has *composition* information: the notes and their timings. The [`TX2` format](#tx2-format) has *expressive* information: dynamics and timbre information.

You can get the data in `TX1` (used in our paper) and `TX2` (*not* used in our paper) formats here:

* (10 MB) [Download](https://drive.google.com/open?id=1WO6guGagqaw22LH32_NEBeavtbaWy_ar "94763d90ba98ca457b64af3c49b1ed7d9e1434e5ef534be34e836c71d4693cbe") NES-MDB in [TX1 Format](#tx1-format)
* (20 MB) [Download](https://drive.google.com/open?id=1ko3LXvotfubZ-C8Xq_K01bWd5NWiduH9 "c787a4e04bcf6439a8674683e66f2b87062383296199f3ae3c0ef66de23c50e4") NES-MDB in [TX2 Format](#tx2-format)

Other instructions in this README assume that you have moved (at least one of) these bundles to the `LakhNES/data` folder and `tar xvfz` them there.

## Reproduce paper results

If you download all of the above checkpoints and `tar xvfz` them under `LakhNES/model/pretrained`, you can reproduce the exact numbers from our paper (Table 2 and Figure 3):

```
source LakhNES-model/bin/activate
cd model
./reproduce_paper_eval.sh
```

This should take a few minutes and yield valid PPLs of `[4.099, 3.175, 2.911, 2.817, 2.800]` and test PPLs of `[3.501, 2.741, 2.545, 2.472, 2.460]` in order.

## Train LakhNES

I (Chris) admit it. My patch of [the official Transformer-XL codebase](https://github.com/kimiyoung/transformer-xl) (which lives under the `model` subdirectory) is among the ugliest code I've ever written. Instructions about how to use it are forthcoming, though the adventurous among you are welcome to try before then. For now, I focused on making the [pretrained checkpoints](#download-checkpoints) easy to use. I hope that will suffice for now.

One asset of our training pipeline, the code which adapts Lakh MIDI to NES MIDI for transfer learning, is somewhat more polished. It can be found at `LakhNES/data/adapt_lakh_to_nes.py`.

## User study

Information about how to use the code for our Amazon Mechanical Turk user study (under `LakhNES/userstudy`) is forthcoming.

## Attribution

If you use this work in your research, please cite us via the following BibTeX:

```
@inproceedings{donahue2019lakhnes,
  title={LakhNES: Improving multi-instrumental music generation with cross-domain pre-training},
  author={Donahue, Chris and Mao, Huanru Henry and Li, Yiting Ethan and Cottrell, Garrison W. and McAuley, Julian},
  booktitle={ISMIR},
  year={2019}
}
```
