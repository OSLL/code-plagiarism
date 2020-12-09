#include <stdio.h>
#include <regex.h>
#include <string.h>
#include <stdlib.h>
#define MEMORY 10
#define REGULAR "(\\w+:\\/\\/)?(www\\.)?(\\w+((\\.\\w+)+))((\\/\\w+)*)\\/(\\w+\\.\\w+)\n"

void free_memory(char** text, int count){
    for(int i=0;i<count;i++)
    free(text[i]);
    free(text);
}

char* writesentence(int* eflag){
    char* sentence =(char*)calloc(MEMORY,sizeof(char));
    int count_of_simvol=0;
    char simvol;
    int flag =1;
    int size = MEMORY;
    do
    {
        if (count_of_simvol==size){
        size+=MEMORY;
        sentence=(char*)realloc(sentence,size*sizeof(char));
        }
    if(scanf("%c",&simvol)==EOF){
        flag=0;
        *(eflag)=0;
    }
	else if (simvol=='\n'){
        sentence[count_of_simvol]=simvol;
	    flag=0;
    }
	else
	    sentence[count_of_simvol]=simvol;
    count_of_simvol++;
    }while(flag);
    if (count_of_simvol==size){
        size+=1;
        sentence=(char*)realloc(sentence,size*sizeof(char));
        }
    sentence[count_of_simvol]='\0';
    return sentence;
}

char** writetext(int* count_of_sentences){
    int eflag=1;
    char** text=(char**)calloc(1,sizeof(char*));
    int count=0;
    do
    {
        text=(char**)realloc(text,(count+1)*sizeof(char*));
        text[count]=writesentence(&eflag);
        count++;
    }while (eflag);
    (*count_of_sentences)=count;
    return text;
}

void printresults(regmatch_t *result, char* sentence){
    for(int k=result[3].rm_so;k<result[3].rm_eo;k++)
        printf("%c",sentence[k]);
        printf(" - ");
    for(int k=result[8].rm_so;k<result[8].rm_eo;k++)
        printf("%c",sentence[k]);
    printf("\n");
}

int main(){
	size_t maxGroups = 9;
	int count_of_sentences =0;
	regex_t regexCompiled;
	regmatch_t groupArray[maxGroups];
	regcomp(&regexCompiled, REGULAR, REG_EXTENDED);
    char** text=writetext(&count_of_sentences);
    for (int i=0;i<count_of_sentences;i++){
        if (regexec(&regexCompiled, text[i], maxGroups, groupArray, 0) == 0){
            printresults(groupArray,text[i]);
        }
    }
    regfree(&regexCompiled);
    free_memory(text,count_of_sentences);
    return 0;
}
