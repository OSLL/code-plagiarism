#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <regex.h>
#include <string.h>

#define PATTERN "([a-z]+:\\/\\/)?(www\\.)?(([a-zA-Z0-9]+\\.)+[a-zA-z0-9]+)\\/([a-zA-z0-9]+\\/)*([a-zA-Z0-9_]+\\.[a-z0-9]+)"
#define MAXGROUPS 7
#define BUFFER 5
char* read_sentence(){
    int k = 1;
    int i = 0;
    int n_flag =0;
    char* sentence = (char*)malloc((k+1)*sizeof(char));
    char letter;
    letter = fgetc(stdin);
    while(letter != '\n'){
	    sentence[i] = letter;
	    if(letter == '.'){
        sentence[i+1] = '\0';
		    if(strcmp(sentence, "Fin.")==0){
			    return sentence;
		    }
	    }			
      k++;
      i++;
      sentence = realloc(sentence, (k+1)*sizeof(char));
      letter = fgetc(stdin);
    }
    sentence[i] = letter;
    sentence[i+1] = '\0';
    return sentence;
}


int main() {
	char* reg_str = PATTERN;
	size_t max_gr = MAXGROUPS;
	regex_t regexCompiled;
	regmatch_t arr_gr[max_gr];
	regcomp(&regexCompiled, reg_str, REG_EXTENDED);



	char* sentence = (char*)malloc(BUFFER*sizeof(char));
	int flag = 0;
    	while (flag == 0){
        	sentence = read_sentence();
        	if(strcmp(sentence,"Fin.") == 0 ){
            		flag = 1;
        	}
		if(regexec(&regexCompiled, sentence, max_gr, arr_gr, 0) == 0){
			for (int i = arr_gr[3].rm_so; i< arr_gr[3].rm_eo; i++){
				printf("%c", sentence[i]);
			}
			printf(" - ");
			for (int j = arr_gr[6].rm_so; j< arr_gr[6].rm_eo; j++){
				printf("%c", sentence[j]);
			}
		}
		printf("\n");
	
    }
	free(sentence);
	regfree(&regexCompiled);
	return 0;
}
