#include <string>
#include <sstream>

#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <signal.h>

#include "psdaq/hsd/Module64.hh"
#include "psdaq/hsd/QABase.hh"
#include "psdaq/hsd/PV64Stats.hh"
#include "psdaq/hsd/PV64Ctrls.hh"
#include "psdaq/mmhw/AxiVersion.hh"
#include "psdaq/mmhw/Xvc.hh"

#include "psdaq/service/Routine.hh"
#include "psdaq/service/Task.hh"
#include "psdaq/service/Timer.hh"


extern int optind;

using Pds::Task;

namespace Pds {

  namespace HSD {

    static Module64* reg = NULL;

    static void sigHandler( int signal )
    {
      if (reg) {
        reg->stop();
        reinterpret_cast<HSD::QABase*>((char*)reg->reg()+0x80000)->dump();
      }

      ::exit(signal);
    }

    class PvAllocate : public Routine {
    public:
      PvAllocate(PV64Stats& pvs,
                 PV64Ctrls& pvc,
                 const char* prefix) :
        _pvs(pvs), _pvc(pvc), _prefix(prefix) {}
    public:
      void routine() {
        std::ostringstream o;
        o << _prefix;
        std::string pvbase = o.str();
        _pvs.allocate(pvbase);
        _pvc.allocate(pvbase);
        delete this;
      }
    private:
      PV64Stats&    _pvs;
      PV64Ctrls&    _pvc;
      std::string   _prefix;
    };

    class StatsTimer : public Timer {
    public:
      StatsTimer(Module64& dev);
      ~StatsTimer() { _task->destroy(); }
    public:
      void allocate(const char* prefix);
      void start   ();
      void cancel  ();
      void expired ();
      Task* task() { return _task; }
      unsigned duration  () const { return 1000; }
      //      unsigned duration  () const { return 1010; }  // 1% error on timer
      unsigned repetitive() const { return 1; }
    private:
      Module64&  _dev;
      Task*    _task;  // Serialize all register access through this task
      PV64Stats  _pvs;
      PV64Ctrls  _pvc;
    };
  };
};

using namespace Pds::HSD;

StatsTimer::StatsTimer(Module64& dev) :
  _dev      (dev),
  _task     (new Task(TaskObject("PtnS"))),
  _pvs      (dev),
  _pvc      (dev, *_task)
{
}

void StatsTimer::allocate(const char* prefix)
{
  _task->call(new PvAllocate(_pvs, _pvc, prefix));
}

void StatsTimer::start()
{
  //theTimer = this;

  Timer::start();
}

void StatsTimer::cancel()
{
  Timer::cancel();
  expired();
}

//
//  Update EPICS PVs
//
void StatsTimer::expired()
{
  _pvs.update();
}

void usage(const char* p) {
  printf("Usage: %s [options]\n",p);
  printf("Options: -d <device>  (default: /dev/qadca)\n"
         "         -P <prefix>  (default: DAQ:LAB2:HSD)\n"
         "         -I           (Interleave)\n");
}

int main(int argc, char** argv)
{
  extern char* optarg;

  int c;
  bool lUsage = false;

  const char* dev    = "/dev/qadca";
  const char* prefix = "DAQ:LAB2:HSD";

  while ( (c=getopt( argc, argv, "d:P:Ih")) != EOF ) {
    switch(c) {
    case 'd':
      dev    = optarg;      break;
    case 'P':
      prefix = optarg;      break;
    case 'I':
      Pds::HSD::PV64Ctrls::interleave(true); break;
    case '?':
    default:
      lUsage = true;      break;
    }
  }

  if (optind < argc) {
    printf("%s: invalid argument -- %s\n",argv[0], argv[optind]);
    lUsage = true;
  }

  if (lUsage) {
    usage(argv[0]);
    exit(1);
  }

  int fd = open(dev, O_RDWR);
  if (fd<0) {
    perror("Open device failed");
    return -1;
  }

  Module64* m = Module64::create(fd);

  std::string buildStamp = m->version().buildStamp();
  printf("BuildStamp: %s\n",buildStamp.c_str());

  //  m->setup_timing(M64);
  m->setup_timing(M3_7);
  m->setup_jesd();

  m->set_local_id(strtoul(dev+strlen(dev)-2,NULL,16));

  StatsTimer* timer = new StatsTimer(*m);

  ::signal( SIGINT, sigHandler );

  timer->allocate(prefix);
  timer->start();

  //  Pds::Mmhw::Xvc::launch( m->xvc(), false );
  while(1)
    sleep(1);                    // Seems to help prevent a crash in cpsw on exit

  return 0;
}
