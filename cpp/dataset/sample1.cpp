#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>

#define MAX_GROUPS 7
#define EXPRESSION "([a-z]+:\\/\\/)?(www.)?((\\w+\\.\\w+)+)\\/(\\w+\\/)*(\\w+\\.\\w+)"

char** character_reading(const char* final_sen, int* size_text){
        char c;
        int i=0;
        int j=0;
        int size_sen=3;
        *size_text=1;
        char** text=calloc(*size_text, sizeof(char*));
        text[j]=(char*)calloc(size_sen, sizeof(char));
                do{
                if (j>=*size_text){
                        text=realloc(text, (*size_text+=1)*sizeof(char*));
                        text[j]=(char*)calloc(3, sizeof(char));
                }
                size_sen=2;
                i=0;    
                while ((c=getchar())!='\n'){
                if (i>=size_sen-3){
                        text[j]=realloc(text[j], (size_sen+=2)*sizeof(char));
                        }
                text[j][i++]=c;
                if (strcmp(text[j], final_sen)==0)
                        break;
                        }
                text[j][i++]='\n';
                text[j][i]='\0';
		j++;
                }while (strstr(text[j-1], final_sen)==NULL);
	return text; 
}

int main(){
	int size_text;
	char** text=character_reading("Fin.", &size_text);
	char* reg=EXPRESSION;
	regex_t rgcom;
	size_t mxgr=MAX_GROUPS;
	regmatch_t grarr[mxgr];
	if(regcomp(&rgcom, reg, REG_EXTENDED)){
		printf("Sorry, can't compile");
		return 0;
	}
	for (int j=0; j<size_text-1; j++){
		if (regexec(&rgcom, text[j], mxgr, grarr, 0)==0){
			{
			if (grarr[0].rm_so==-1)
                    		break;
                	for (int i=grarr[3].rm_so; i<grarr[3].rm_eo; i++)
                    		printf("%c",text[j][i]);
			printf(" - ");
			for (int i=grarr[6].rm_so; i<grarr[6].rm_eo; i++)
				printf("%c", text[j][i]);
			printf ("\n");
			}
		}
	}	
	
    	for (int j=0; j<size_text; j++)
        	free (text[j]);
    	free (text);
	regfree(&rgcom);
	return 0;
}
