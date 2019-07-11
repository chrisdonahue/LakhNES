# LakhNES

## Setting up the synthesis package

LakhNES requires the Python package `nesmdb` to synthesize chiptune audio. Unfortunately, `nesmdb` has not been updated to Python 3.

We *strongly* recommend using `virtualenv` to install `nesmdb` and run it as a synthesis server. To do this, run the following commands from this repository:

```
cd LakhNES
virtualenv -p python2.7 --no-site-packages nesmdb-server
source nesmdb-server/bin/activate
pip install nesmdb
python data/rpc.py
```

Then,
