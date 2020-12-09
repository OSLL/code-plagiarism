#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <regex.h>
#define REG  "(\\w+:\\/\\/)?(www\\.)?((\\w+\\.)+\\w+)\\/(\\w+\\/)*(\\w+\\.\\w+)"
char * ReadSent()
{
    int buf=5;
    char* sent=(char*)malloc(buf*sizeof(char));
    char c;
    int count=0;
    while((c=getchar()) && (c!='\n'))
    {
    sent[count]=c;
    count++;
    if(count==buf)
        {
        buf+=5;
        sent=(char*)realloc(sent,buf*sizeof(char));
        }
    sent[count]='\0';
    if(!strcmp(sent,"Fin."))
        return NULL;
    }
    
    return sent;
}
char ** ReadText(int *count)
{
    int number=0;
    int buf=5;
    char** text=(char**)malloc(buf*sizeof(char*));
    text[number]=ReadSent();
    while(text[number]!=NULL)
    {
         number++;
        if(number==buf)
        {
            buf+=5;
            text=(char**)realloc(text,buf*sizeof(char*));
        }
        text[number]=ReadSent();
    }
    *count=number;
    return text;
} 
int main()
{
    
    int count=0;
    char** text=ReadText(&count);
       regex_t template;
        size_t group_num = 7;
        regmatch_t groups[group_num];
 
        if (regcomp(&template, REG, REG_EXTENDED)) return 0;
 
        for (int i = 0; i < count; i++) {
 
                if (regexec(&template, text[i], group_num, groups, 0) == 0) {
 
                        for (int j = groups[3].rm_so; j < groups[3].rm_eo; j++) printf("%c", text[i][j]);
                        printf(" - ");
                        for (int j = groups[6].rm_so; j < groups[6].rm_eo; j++) printf("%c", text[i][j]);
                        printf("\n");
                }
        }
            regfree(&template);
        for (int i = 0; i < count; i++) free(text[i]);
        free(text);

    
return 0;
}

