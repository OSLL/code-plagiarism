#include "header.h"
#include <string>
// #include <iostream>
using namespace std;

int func(int a){
    if(a > 18){
        return 1;
    }
    return 0;
}

int main(){
    A *a = new A();
    a->num = 123;

    func(a->num);

    return 0;
}