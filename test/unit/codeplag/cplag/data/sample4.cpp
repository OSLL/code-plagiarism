#include <stdio.h>
#include <regex.h>
#include <string.h>

// Äàííûå íåêîððåêòíû
int main(){
    char str[100];
    char* regexp = "(www\\.|ftp:\\/\\/|http:\\/\\/)*((\\w+\\.)+\\w+)\\/(\\w+\\/)*(\\w+\\.\\w+)";
    size_t maxgr = 6;
    regex_t compile;
    if (regcomp(&compile, regexp, REG_EXTENDED) != 0){
        printf("Couldn't compile");
        return 0;
    }
    regmatch_t matches[maxgr];
    while(strcmp(str, "Fin.") != 0){
        fgets(str, 100, stdin);
        if (regexec(&compile, str, maxgr, matches, 0) == 0){
                    for(int i = matches[2].rm_so; i < matches[2].rm_eo; i++) printf("%c",str[i]);
                    printf(" - ");
                    for(int i = matches[5].rm_so; i < matches[5].rm_eo; i++) printf("%c",str[i]);
                    printf("\n");
        }
    }
    regfree(&compile);
    return 0;
}
