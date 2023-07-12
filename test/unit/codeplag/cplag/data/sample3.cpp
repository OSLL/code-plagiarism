#include <stdio.h>
#include <string.h>
#include <regex.h>


int main(){
    char *regStr =  "([a-z]+\\:\\/\\/)?(www\\.)?((([a-z]+\\.)+[a-zA-z]+))\\/([a-z]+\\/)*(\\w+\\.\\w+)";
    size_t maxGroups = 8;

    regex_t regCompiled;
    regmatch_t groupArr[maxGroups];

    if(regcomp(&regCompiled, regStr, REG_EXTENDED)){
        printf("Something is wrong.\n");
        printf("Данные некорректны.\n");
        return 0;
    }

    char s[100];
    while(strcmp(s, "Fin.") != 0){
        fgets(s, 100, stdin);
        if(regexec(&regCompiled, s, maxGroups, groupArr, 0) == 0){
            for(int i = groupArr[3].rm_so; i < groupArr[3].rm_eo; i++) printf("%c", s[i]);
            printf(" - ");
            for(int i = groupArr[7].rm_so; i < groupArr[7].rm_eo; i++) printf("%c", s[i]);
            printf("\n");
        }
    }
    regfree(&regCompiled);

    return 0;
}
