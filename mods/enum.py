# Copyright 2010, Alec Thomas
# Licensed under Attribution-ShareAlike 3.0 Unported
# From http://stackoverflow.com/revisions/1695250/2

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
