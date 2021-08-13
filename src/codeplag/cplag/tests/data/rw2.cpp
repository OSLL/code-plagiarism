#include <iostream>
#include <fstream>
using namespace std;

int main () {
  char data[255];
  ofstream myfile ("example.txt");

  if (!myfile.is_open())
    return 1;

  cout << "Writing" << endl;
  cout << "Enter name: "; 
  cin.getline(data, 100);
  
  myfile << data << endl;

  cout << "Enter age: "; 
  cin >> data;
  cin.ignore();

  myfile << data << endl;
  myfile.close();
  

  ifstream infile; 
  if (infile.is_open())
    return 2;

  infile.open("example.txt"); 

  cout << "Reading" << endl; 
  infile >> data; 

  cout << data << endl;

  infile >> data; 
  cout << data << endl; 

  infile.close();

  return 0;
}