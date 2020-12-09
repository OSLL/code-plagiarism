#include <stdio.h>
#include <stdlib.h>
#include <regex.h>
#include <string.h>

#define A 256
#define B 256

int main()
{
    regex_t phrase;
    regmatch_t kateg[B];
    char txt[A];
    
    if (regcomp(&phrase, "[Ww\\.]*([[:alnum:]]*(\\.[[:alnum:]]+)+)\\/([[:alnum:]]+\\/)*([[:alnum:]]+\\.[[:alnum:]]+)", REG_EXTENDED)) {
       
        printf("??????");
    }
    else {
        while(fgets(txt, A, stdin)) {
            if (strcmp(txt, "Fin.\n") == 0) {
                break;
                
            }
            
            if(regexec(&phrase, txt, B, kateg, 0) == 0) {
                for (int i = kateg[1].rm_so; i < kateg[1].rm_eo; i++) {
                    putchar(txt[i]);
                    
                }
                
                printf(" - ");
                
                for (int j = kateg[4].rm_so; j < kateg[4].rm_eo; j++) {
                    putchar(txt[j]);
                }
                
                puts("");
            }
        }
    }
    regfree(&phrase);
    return 0;
}
