#!/usr/bin/env python
#

import sys, os
import time
import getopt
import pprint

from PyDgram import PyDgram
from Event import Event
sys.path.append('../build/psana')
import dgram
#

class DataSource:
    """Stores variables and arrays loaded from an XTC source.\n"""
    def __init__(self, expStr, verbose=0, debug=0):
        ### Parameter expStr can be an xtc filename or 
        ### an 'exp=expid:run=runno' string
        if os.path.isfile(expStr):
            self.exp = expStr
            self.runno = 0
            self.xtcFiles = [expStr]
        else:
            for expKeyVal in expStr.split(":"):
                key, val = expKeyVal.split("=")
                if key == 'exp':
                    self.exp = val
                elif key == 'run':
                    self.runno = int(val)
                else:
                    print("Unrecongnized argument: %s"%(expKeyVal))
                    print("Example of valid argument: exp=cxitut13:run=10")
                    print("System Exit")
                    exit()
            ### Read xtc file list from somewhere...
            self.xtcFiles = ['e001-r0001-s00.smd.xtc','e001-r0001-s01.smd.xtc']
        self.configs = []
        self._configs = []
        assert len(self.xtcFiles) > 0
        ### Open xtc files
        for xtcdata_filename in self.xtcFiles:
            fd = os.open(xtcdata_filename,
                         os.O_RDONLY|os.O_LARGEFILE)
            self._configs.append(dgram.Dgram(file_descriptor=fd,
                                                 verbose=verbose,
                                                 debug=debug))
            self.configs.append(PyDgram(self._configs[-1]))
        
    def __iter__(self):
        return self

    def __next__(self):
        # Loop through all files and grab dgrams
        dgrams = []
        for _config in self._configs:
            d=dgram.Dgram(config=_config)
            dgrams.append(PyDgram(d))
        return Event(dgrams=dgrams)

    def jump(self, offset=0):
        # Random access only works if the datasource is
        # a single file (mostly used to jump around in bigdata).
        d=dgram.Dgram(config=self._configs[0], offset=offset)
        event = Event(dgrams=[PyDgram(d)])
        return event

    def _get_verbose(self):
        return getattr(self._config, "verbose")
    def _set_verbose(self, value):
        setattr(self._config, "verbose", value)
    _verbose = property(_get_verbose, _set_verbose)

    def _get_debug(self):
        return getattr(self._config, "debug")
    def _set_debug(self, value):
        setattr(self._config, "debug", value)
    _debug = property(_get_debug, _set_debug)


def parse_command_line():
    opts, args_proper = getopt.getopt(sys.argv[1:], 'hvd:f:')
    verbose=0
    debug=0
    xtcdata_filename="data.xtc"
    for option, parameter in opts:
        if option=='-h': usage_error()
        if option=='-v': verbose+=1
        if option=='-d': debug = int(parameter)
        if option=='-f': xtcdata_filename = parameter
    if xtcdata_filename is None:
        xtcdata_filename="data.xtc"
    if verbose>0:
        sys.stdout.write("xtcdata filename: %s\n" % xtcdata_filename)
        sys.stdout.write("verbose: %d\n" % verbose)
        sys.stdout.write("debug: %d\n" % debug)
    elif debug>0:
        sys.stdout.write("debug: %d\n" % debug)
    return (args_proper, xtcdata_filename, verbose, debug)

def getMemUsage():
    pid=os.getpid()
    ppid=os.getppid()
    cmd="/usr/bin/ps -q %d --no-headers -eo size" % pid
    p=os.popen(cmd)
    size=int(p.read())
    return size

def main():
    args_proper, xtcdata_filename, verbose, debug = parse_command_line()
    ds=DataSource(xtcdata_filename, verbose=verbose, debug=debug)
    print("vars(ds):")
    for var_name in sorted(vars(ds)):
        print("  %s:" % var_name)
        e=getattr(ds, var_name)
        for key in sorted(e.__dict__.keys()):
            print("%s: %s" % (key, e.__dict__[key]))
    print()
    count=0
    for evt in ds:
        print("evt:", count)
        for var_name in sorted(vars(evt)):
            e=getattr(evt, var_name)
            print("  %s: %s" % (var_name, e))
        a=evt.array0Pgp
        try:
            a[0][0]=999
        except ValueError:
            print("The evt.array0_pgp array is read-only, as it should be.")
        else:
            print("Warning: the evt.array0_pgp array is writable")
        print()
        count+=1
    return

def usage_error():
    s="usage: python %s" %  os.path.basename(sys.argv[0])
    sys.stdout.write("%s [-h] [-v] [-d <DEBUG_NUMBER>]\n" % s)
    sys.stdout.write("%s [-f xtcdata_filename]\n" % (" "*len(s)))
    sys.exit(1)

if __name__=='__main__':
    main()

