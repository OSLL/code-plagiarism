## Последовательность работы
1. Токенизируем исходный код двух сравниваемых программ;

2. Формируем множества N-gramm двух последовательностей токенов A и B. Величина N вычисляется из размера программ;

3. Вычисляем коэффициент Жаккара по формуле J(A, B) = |A ⋂ B| / |A ∪ B|. Также коэффициент сходства двух программ.

### Пример

1. Пусть есть две последовательности токенов, полученных из двух программ, причем в примере каждый токен представлен типом string:
    - INT_TYPE ID ASSIGN ID MATH_OP ID

    - INT_TYPE ID ASSIGN NUMERIC MATH_OP NUMERIC

2. Далее для каждой такой последовательности строим, к примеру, уникальные биграммы:
    - A = {(INT_TYPE, ID), (ID, ASSIGN), (ASSIGN, ID), (ID, MATH_OP), (MATH_OP, ID)}

    - B = {(INT_TYPE, ID), (ID, ASSIGN), (ASSIGN, NUMERIC), (NUMERIC, MATH_OP), (MATH_OP, NUMERIC)}
Вычисляем значение коэффициента Жаккара:
    J(A, B) = |{(INT_TYPE, ID), (ID, ASSIGN)}| 
                              / 
              |{(INT_TYPE, ID), (ID, ASSIGN), (ASSIGN, ID),
                (ID, MATH_OP), (MATH_OP, ID), (ASSIGN, NUMERIC),
                (NUMERIC, MATH_OP), (MATH_OP, NUMERIC)}|
            = 2 / 8 = 0.25

$$\frac{
    |\{(INT\_TYPE,\ ID), (ID,\ ASSIGN)\}|
}{
    |\{(INT\_TYPE,\ ID), (ID,\ ASSIGN), (ASSIGN,\ ID),
       (ID,\ MATH\_OP), (MATH\_OP,\ ID), (ASSIGN, NUMERIC),
       (NUMERIC,\ MATH\_OP), (MATH\_OP,\ NUMERIC)\}|
}$$

### Список литературы

1. [ИНФОРМАЦИОННАЯ СИСТЕМА «ПЛАГИАТ В ПРОГРАММАХ СТУДЕНТОВ»](https://pnu.edu.ru/media/vestnik/articles-2019/025-034_Вихтенко_Э._М._Карманов_Д._А._Син_Д._З..pdf).

2. [ВЫЯВЛЕНИЕ ПЛАГИАТА В ПРОГРАММНОМ КОДЕ C#](http://it-visnyk.kpi.ua/wp-content/uploads/2011/07/53_25.pdf).
