
"""
Module :py:class:`GCDaqControl` contains proxy and singleton for psdaq/control/collection.py
=============================================================================================

Usage ::

    from psdaq.control_gui.GCDaqControl import daq_control, DaqControl

    print('DaqControl.transitions:', DaqControl.transitions)
    print('DaqControl.states  :', DaqControl.states)

    daq_control.set_daq_control(DaqControl(host='localhost', platform=2, timeout=10000))

    daq_control.setstate('running') # DaqControl.states[5]
    state = daq_control().getstate()


See:
    - :class:`CGDaqControl`
    - `graphqt documentation <https://lcls-psana.github.io/graphqt/py-modindex.html>`_.

Created on 2019-02-01 by Mikhail Dubrovin
"""

#----------

import logging
logger = logging.getLogger(__name__)

from psdaq.control.collection import DaqControl

#----------

class DaqControlProxy:
  def __init__(self, o=None) :
      """Creates proxy object, e.g. for singleton.
      """
      self.o = None
      self.set_daq_control(o)

  def set_daq_control(self, o=None) :
      """Sets object whenever it is available, Nobe by default.
      """
      if self.o is not None : del self.o
      self.o = o

  def __call__(self) :
      """Access object, e.g. using singleton:
         state = daq_control().getstate()
      """
      return self.o

#---------- SINGLETON

daq_control = DaqControlProxy()

def worker_set_state(dicio):
    state = dicio.get('state_in','N/A')
    logger.debug('worker_set_state %s' % state)
    daq_control().setState(state)
       
def worker_get_state(dicio):
    dicio['state_out'] = daq_control().getState()

#----------
#----------
#----------

if __name__ == "__main__" :
  def proc() :
    print('DaqControl.transitions:', DaqControl.transitions)
    print('DaqControl.states  :', DaqControl.states)

    o = DaqControl(host='localhost', platform=6, timeout=5000) # msec
    daq_control.set_daq_control(o)

    state = daq_control().getState()
    print('DaqControl.states  :', state)

#----------

if __name__ == "__main__" :
    proc()

#----------