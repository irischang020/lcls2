"""
Test smd0 and eventbuilder for handling step dgrams.
See https://docs.google.com/spreadsheets/d/1VlVCwEVGahab3omAFJLaF8DJWFcz-faI9Q9aHa7QTUw/edit?usp=sharing for test setup.

"""
import os, time, glob, sys
from psana.smdreader import SmdReader
from psana.dgram import Dgram
from setup_input_files import setup_input_files
from psana import DataSource
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

test_xtc_dir = os.environ.get('TEST_XTC_DIR', '.')
xtc_dir = os.path.join(test_xtc_dir, '.tmp_smd0')

def run_smd0(n_events):
    filenames = glob.glob(os.path.join(xtc_dir, '.tmp', 'smalldata', '*.xtc2'))
    fds = [os.open(filename, os.O_RDONLY) for filename in filenames]

    # Move file ptrs to datagram part
    configs = [Dgram(file_descriptor=fd) for fd in fds]
    
    limit = len(filenames)
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    
    st = time.time()
    smdr = SmdReader(fds[:limit])
    got_events = -1
    processed_events = 0
    smdr.get(n_events)
    got_events = smdr.got_events
    result = {'each_read':[], 'total_n_events':0}
    cn_i = 0
    while got_events != 0:
        step_chunk_nbytes = 0
        smd_chunk_nbytes = 0
        for i in range(limit):
            smd_view = smdr.view(i)
            if smd_view:
                smd_chunk_nbytes += smd_view.nbytes
            step_view = smdr.view(i, update=True)
            if step_view:
                step_chunk_nbytes += step_view.nbytes
        result['each_read'].append([got_events, smd_chunk_nbytes, step_chunk_nbytes])
        processed_events += got_events
       
        # Read more events
        smdr.get(n_events)
        got_events = smdr.got_events
        cn_i += 1

    en = time.time()
    result['total_n_events'] = processed_events

    for fd in fds:
        os.close(fd)

    return result

def run_serial_read(n_events):
    exp_xtc_dir = os.path.join(xtc_dir, '.tmp')
    os.environ['PS_SMD_N_EVENTS'] = str(n_events)
    ds = DataSource(exp='xpptut13', run=1, dir=exp_xtc_dir)
    cn_steps = 0
    cn_events = 0
    result = {'evt_per_step':[], 'n_steps': 0, 'n_events':0}
    for run in ds.runs():
        for i, step in enumerate(run.steps()):
            cn_evt_per_step = 0
            for j, evt in enumerate(step.events()):
                cn_evt_per_step += 1
                cn_events += 1
            cn_steps +=1
            result['evt_per_step'].append(cn_evt_per_step)

    result['n_steps'] = cn_steps
    result['n_events'] = cn_events
    return result
    

if __name__ == "__main__":
    import pathlib
    p = pathlib.Path(xtc_dir)
    if not p.exists():
        if rank == 0:
            p.mkdir()
            setup_input_files(p, n_files=2, slow_update_freq=4, n_motor_steps=3, n_events_per_step=10, gen_run2=False)
    
    comm.Barrier()
    result = run_serial_read(51)
    print(result)
    """
    # Expected result: 
    # each_read n_events, smd_chunk_nbytes, step_chunk_nbytes
    # total_n_events
    # Test 1: No. of chunk-read events covers the entire smds
    expected_result = {'each_read': [[30, 6728, 888]], 'total_n_events': 30}
    result = run_smd0(51)
    assert result == expected_result

    # Test 2: No. of chunk-read events covers beyond the next BeginStep
    expected_result = {'each_read': [[20, 4464, 592], [10, 2264, 296]], 'total_n_events': 30}
    result = run_smd0(20)
    assert result == expected_result

    # Test 3: No. of chunk-read events covers the next BeginStep
    expected_result = {'each_read': [[19, 4296, 592], [11, 2432, 296]], 'total_n_events': 30}
    result = run_smd0(19)
    assert result == expected_result

    if size == 1:
        expected_result = {'evt_per_step': [10, 10, 10], 'n_steps': 3, 'n_events': 30}
        result = run_serial_read(51)
        assert result == expected_result
        
        expected_result = {'evt_per_step': [10, 10, 0, 10], 'n_steps': 4, 'n_events': 30}
        result = run_serial_read(20)
        assert result == expected_result

        expected_result = {'evt_per_step': [10, 9, 1, 10], 'n_steps': 4, 'n_events': 30}
        result = run_serial_read(19)
        assert result == expected_result

    else:
        expected_result = {'evt_per_step': [0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1], 'n_steps': 45, 'n_events': 30}
        result = run_serial_read(51)
        if rank == 2: # assuming mpirun -n 3 test
            assert result == expected_result
            
        result = run_serial_read(20)
        if rank == 2: # assuming mpirun -n 3 test
            assert result == expected_result
        
        result = run_serial_read(19)
        if rank == 2: # assuming mpirun -n 3 test
            assert result == expected_result
   """ 
