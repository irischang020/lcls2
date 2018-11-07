# NOTE:
# To test on 'real' bigdata: 
# xtc_dir = "/reg/d/psdm/xpp/xpptut15/scratch/mona/test"
# >bsub -n 64 -q psfehq -o log.txt mpirun python user.py
#
# Todo
# - Use detector interface in eventCode
import os
from psana import DataSource

def filter_fn(evt):
    return True

xtc_dir = os.path.join(os.getcwd(),'.tmp')
ds = DataSource('exp=xpptut13:run=1:dir=%s'%(xtc_dir), filter=filter_fn)

# Usecase#1 : two iterators
#beginJobCode
for run in ds.runs():
    det = run.Detector('xppcspad')
    #beginRunCode
    for evt in run.events():
        #eventCode
        for d in evt:
            assert d.xppcspad.raw.arrayRaw.shape == (18,)
    #endRunCode
#endJobCode

# Usecase#2: one iterator
for evt in ds.events():
    pass

# Todo: MONA add back configUpdates()
# Usecase#3: looping through configs
#for run in ds.runs():
#    for configUpdate in run.configUpdates():
#        for config in configUpdate.events():