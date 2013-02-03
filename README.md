dsm_maker
=========

Dot to dsm to svg converter.

Usage:

  python deps.py in_file.dot out_file.svg

Dependencies:

  sudo apt-get install python-rsvg python-pydot

Notes:

  Seems like there is only one loop in the data, so it should be
possible to sort everything so that all thye connections would be in
the bottom triangle, I just need to find an algorithm that does it.
