#include <stdio.h>
#include <regex.h>
#include <malloc.h>
#include <string.h>
#define COMP "Fin."
 
char* stdin_sent();
 
int main(){
    char* pattern = "(\\w*:\\/\\/)?(www.)?(\\w*(\\.\\w+)+)\\/(\\w+\\/)*(\\w+\\.\\w+)$";
    size_t maxGroups = 7;
    regex_t regexCompiled;
    regmatch_t groupArray [maxGroups];
    regcomp (&regexCompiled, pattern, REG_EXTENDED);
    char* s = stdin_sent();
    while(strcmp(s, COMP) != 0){
        if(regexec(&regexCompiled, s, maxGroups, groupArray, 0) == 0){
            for(int j=groupArray[3].rm_so;j<groupArray[3].rm_eo;j++){
                printf("%c", s[j]);
            }
            printf(" - ");
            for(int j=groupArray[6].rm_so;j<groupArray[6].rm_eo;j++){
                printf("%c", s[j]);
            }
            printf("\n");
        }
        s = stdin_sent();
    }
    return 0;
}
char* stdin_sent(){
    char c;
    int lenght = 2, i = 0;
    char* sent = malloc(lenght * sizeof(char));
    c = getchar();
    while ((c != '\n') && (strcmp(sent, COMP) !=0)){
        lenght += 1;
        sent = realloc(sent, lenght * sizeof(char));
        sent[i] = c;
        i += 1;
        c = getchar();
    }
    sent[i] = '\0';
    return sent;
}

