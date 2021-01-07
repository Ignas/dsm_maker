dsm_maker
=========

Dot to dsm to svg converter.

Usage:

  `PYTHONPATH=src python -m dsm_maker in_file.dot -o out_file.svg --title "Graph title"`

Dependencies:

```
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt
pip install -e .
```

Ubuntu:
```
$ sudo apt-get install libcairo2
```

macOS:

```
brew install cairo
```

TODO:

* Package
