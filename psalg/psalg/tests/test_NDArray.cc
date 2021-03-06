
#include <stdio.h>
#include <iostream> // cout
#include <sstream>

#include "psalg/calib/NDArray.hh"
#include "psalg/utils/NDArrayGenerators.hh"

using namespace psalg;

//-------------------

void print_hline(const uint nchars, const char c) {printf("%s\n", std::string(nchars,c).c_str());}

//-------------------
 
void test_NDArray() {

  typedef psalg::types::shape_t shape_t; // uint32_t
  typedef psalg::types::size_t  size_t;  // uint32_t

  printf("In test_NDArray\n");

  std::cout << "test external data buffer\n";

  const double dat1[] = {8,7,6,5,4,3,2,1};
        double dat2[] = {1,2,3,4,5,6,7,8};

  uint32_t sh1[] = {sizeof(dat1)/sizeof(double),};
  uint32_t nd1 = 1;
  NDArray<const double> nda1(sh1, nd1, dat1);
  std::cout << "  const data buffer - nda1: " << nda1 << '\n';

  shape_t sh2[] = {2,4};
  size_t nd2 = 2;
  NDArray<const double> nda2(sh2, nd2, dat1);
  std::cout << "  const data buffer - nda2: " << nda2 << '\n';

  NDArray<double> nda3(sh2, nd2, dat2);
  nda3(2)=30;
  std::cout << "  non-const data buffer - nda3: " << nda3 << '\n';
}

//-------------------
 
void test_input_pars(int i, const int j, int& k, const int& l) {
  cout << "\nvalue received as       int : " << i; 
  cout << "\nvalue received as const int : " << j; 
  cout << "\nvalue received as       int&: " << k; 
  cout << "\nvalue received as const int&: " << l; 
  cout << '\n'; 
}

//void test_met_signature(int i)       // accepts both const and non-const int
//void test_met_signature(const int i) // accepts both const and non-const intv
//void test_met_signature(int& i)      // accepts non-const int &
void test_met_signature(const int& i)  // accepts both const and non-const int &
{ 
  cout << "\n  [const] int [&] : " << i; 
}

void test_cpp() {
  printf("In test_cpp\n");
  const int i=1; const int j=2; int k=3; const int l=4;
  test_input_pars(i,j,k,l);

        double* p; *p = 6;
  const double* q; q=p;
  cout << "\n conversion double* p to const double* q: " << *q << '\n'; 

  const int v=5;
  int vnc=6;
  test_met_signature(v);
  test_met_signature(vnc);
  cout << '\n'; 
}
//-------------------

void test_NDArrayGenerators() {

  typedef psalg::types::shape_t shape_t; // uint32_t
  typedef psalg::types::size_t  size_t;  // uint32_t

  shape_t sh[] = {3,4};
  size_t  nd = 2;
  NDArray<double> a(sh, nd);
  std::cout << "  NDArray (raw)   : " << a << '\n';

  double v = 8;
  fill_ndarray_const<double>(a, v);
  std::cout << "  NDArray (const): " << a.string_ndarray(20) << '\n';

  NDArray<int> a2(sh, nd);
  int range=100;
  //srand(12345); // initialization of random numbers
  srand(time(0)); // initialization of random numbers
  fill_ndarray_random(a2, range);
  std::cout << "  NDArray (random): " << a2.string_ndarray(12) << '\n';

  NDArray<double> a3(sh, nd);
  double mean=0;
  double stddev=1;
  fill_ndarray_normal(a3, mean, stddev);
  std::cout << "  NDArray (normal): " << a3.string_ndarray(12) << '\n';
}

//-------------------

std::string usage(const std::string& tname="")
{
  std::stringstream ss;
  if (tname == "") ss << "Usage command> test_NDArray <test-number>\n  where test-number";
  if (tname == "" || tname=="1"	) ss << "\n  1  - test_NDArray()";
  if (tname == "" || tname=="2"	) ss << "\n  2  - test_cpp()";
  if (tname == "" || tname=="3"	) ss << "\n  3  - test_NDArrayGenerators()";
  ss << '\n';
  return ss.str();
}

//-------------------

int main(int argc, char* argv[])
{
  print_hline(80,'_');
  cout << "In test_NDArray\n";

  print_hline(80,'_');
  cout << usage();
  std::string tname((argc==1)? "1" : argv[1]);
  cout << "\nSelected:" << usage(tname); 

  if      (tname=="1")  test_NDArray();
  else if (tname=="2")  test_cpp();
  else if (tname=="3")  test_NDArrayGenerators();
  else cout << "Undefined test name \"" << tname << '\"';
 
  print_hline(80,'_');
  return EXIT_SUCCESS;
}

//-------------------

