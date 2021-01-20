#include <stdio.h>
#include <regex.h>
#include <string.h>
#include <stdlib.h>

char * get(char * string)
{
 
   char* text = realloc(string, 5 * sizeof(char));
   fgets(text, 5, stdin);
   while (text[strlen(text) - 1] != '\n' && strcmp(text, "Fin.")){
        text = (char*)realloc(text, (strlen(text) + 5));
        fgets(text + strlen(text) , 5, stdin);
    }
    return text;
 }
 
int main()
{
    char * regstring = "(\\w+:\\/\\/)?(www\\.)?((\\w+\\.)+\\w+)\\/(\\w+\\/)*(.+\\.\\w+)";
    regex_t regexCompiled;
    size_t maxGroups = 7;
    regmatch_t groupArray[maxGroups];
    char * string = malloc(5 * sizeof(char));
    regcomp(&regexCompiled, regstring, REG_EXTENDED);
    do{
            string = get(string);
        if (regexec(&regexCompiled, string, maxGroups, groupArray, 0) == 0)
            {
               
            for(int i = groupArray[3].rm_so; i < groupArray[3].rm_eo; i++)
            {
                printf("%c", string[i]);
               
            }
            printf(" - ");
            for(int i = groupArray[6].rm_so; i < groupArray[6].rm_eo; i++)
            {
                printf("%c", string[i]);
               
            }
            }
            printf("\n");
       
    }while(strcmp(string, "Fin."));
    free(string);
    regfree(&regexCompiled);
    return 0;
}
