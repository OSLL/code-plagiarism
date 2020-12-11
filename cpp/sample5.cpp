#include <stdio.h>
#include <string.h>
#include <regex.h>
#include <stdbool.h>
#include <stdlib.h>


int main(){
    char str[100][100];
    int k = 0;
    while (fgets(str[k], 100, stdin))
    {
        if(strchr(str[k], '\n')){
            str[k][strlen(str[k])-1] = '\0';
            k++;
            }
        if(!strcmp(str[k-1], "Fin.")){
            k++;
            break;
        }
    }
    char* sent;
    char* regexString = "([A-Za-z]+:\\/\\/)?(w{3}\\.)?([A-Za-z0-9]+(\\.[A-Za-z0-9]+)+)\\/([A-Za-z0-9]+\\/)*([A-Za-z0-9]+\\.[A-Za-z0-9]+)$";
    int maxGrops = 7;
    regex_t regexCompiled;
    regmatch_t groupArray[maxGrops];
    regcomp(&regexCompiled, regexString, REG_EXTENDED);
    for(int i = 0; i < k; i++)
    {
        sent = str[i]; 
        if (!regexec(&regexCompiled, sent, maxGrops, groupArray, 0))
        {
            for(int j = groupArray[3].rm_so; j < groupArray[3].rm_eo; ++j)
                 printf("%c", sent[j]);
            printf(" - %s\n", sent + groupArray[6].rm_so);
        }
    }
    regfree(&regexCompiled);
    return 0;
}
