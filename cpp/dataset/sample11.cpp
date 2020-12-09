#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>
#define N 1024

int main() {
    regex_t regexpr; regmatch_t groups[7]; char str[N];
    
    if(regcomp(&regexpr, "[Ww\\.]*([[:alnum:]]*(\\.[[:alnum:]]+)+)\\/([[:alnum:]]+\\/)*([[:alnum:]]+\\.[[:alnum:]]+)", REG_EXTENDED)) {
        puts("ERROR: REGULAR EXPRESSION");
        exit(1);
    }
    while(fgets(str, N, stdin)) {
    if (strcmp(str, "Fin.\n") == 0) {
        break;
    }
 	if(regexec(&regexpr, str, 7, groups, 0) == 0) {
        for(int i = groups[1].rm_so; i < groups[1].rm_eo; i++) {
            putchar(str[i]);
        }
        printf(" - ");
        for (int j = groups[4].rm_so; j < groups[4].rm_eo; j++) {
            putchar(str[j]);
        }
        puts("");
    }
    }
    
    regfree(&regexpr);
    return 0;
}
