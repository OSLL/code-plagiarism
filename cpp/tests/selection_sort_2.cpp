void selectionSort(int array[], int size)
{
    for (int i = 0; i < size - 1; i++) {
    /* устанавливаем начальное значение минимального индекса */
        int min_i = i;
    /* находим индекс минимального элемента */
        for (int j = i + 1; j < size; j++) {
            if (array[j] < array[min_i]) {
              min_i = j;
            }
        }
    /* меняем значения местами */
    int temp = array[i];
    array[i] = array[min_i];
    array[min_i] = temp;
}