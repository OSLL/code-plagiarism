#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>

char* enterSent(){
    int sentenceLength = 5;
    int a = 0;
    char lit;
    char* s = calloc(sentenceLength + 1, sizeof(char));
    while((lit = getchar()) && lit != '\n'){
        if(a == sentenceLength - 2){
            sentenceLength *= 2;
            s = realloc(s, sentenceLength*sizeof(char));
        }
        s[a] = lit;
        ++a;
        if(strcmp(s, "Fin.") == 0){
            return s;
        }
    }
    s[a] = '\0';
    return s;
}

int main(){
    int textLength = 8;
    char** arr = malloc(textLength*sizeof(char*));
    int num = 0;
    char* s;
    while(1){
        s = enterSent();
        if(num == textLength - 1){
            textLength *= 2;
            arr = realloc(arr, textLength*sizeof(char*));
        }
        arr[num] = s;
        num++;
        if(strcmp(s, "Fin.") == 0){
            break;
        }
    }
    char* regExpression = "(www\\.)?(([a-zA-Z]+\\.[a-zA-Z]+)+)\\/([a-zA-Z]+\\/)*([a-zA-Z]+\\.[a-zA-Z0-9]+)";
    size_t maxGroups = 7;
    regex_t regexCompiled;
    regmatch_t groups[maxGroups];
    regcomp(&regexCompiled, regExpression, REG_EXTENDED);
    for(int i = 0; i < num; i++){
        if(regexec(&regexCompiled, arr[i], maxGroups, groups, 0) == 0){
            for(int j = groups[2].rm_so; j < groups[2].rm_eo; j++){
                printf("%c", arr[i][j]);
            }
            printf(" - ");
            for(int j = groups[5].rm_so; j < groups[5].rm_eo; j++){
                printf("%c", arr[i][j]);
            }
            printf("\n");
        }
    }
    regfree(&regexCompiled);
    for(int i = 0; i < num; i++){
        free(arr[i]);
    }
    free(arr);
    return 0;
}
