#include <iostream>
#include <fstream>
#include <iomanip>
#include <cstring>

class AnyMatrix {
public:
    AnyMatrix(int _dim, size_t _elem_size); 
    AnyMatrix(const AnyMatrix &matrix);
    virtual ~AnyMatrix();
    AnyMatrix& operator=(AnyMatrix& right); // перегрузка оператора =
    virtual void inputElem(std::istream& in, int raw, int col) = 0; 
    virtual void outputElem(std::ostream& out, int raw, int col) const = 0; 
	bool fileInput(std::string filename);
	bool fileOutput(std::string filename) const;
    friend std::ostream& operator<<(std::ostream& out, const AnyMatrix& matrix);
    friend std::istream& operator>>(std::istream& in,  AnyMatrix& matrix);

    // Методы для заданий по вариантам
    virtual int compare(const char* lhs, const char* rhs) const = 0; // Функция сравнения ячеек матрицы. Реализует производный класс.
    virtual void divide(const char* lhs, const char* rhs, char* result) const = 0;
    virtual bool isZero(const char* element) const = 0;
    int MaxRaw(int rawNum) const;
    int MaxCol(int colNum) const;
    int MinRaw(int rawNum) const;
    int MinCol(int colNum) const;
    
    //перегрузка операций по вариантам
    AnyMatrix* operator%(const AnyMatrix& rhs) const; // Доп задание 6
    AnyMatrix& operator~(); // Доп задание 15

protected:
    void readElemInBuffer(int i, int j, char* buffer) const;
    void writeElemFromBuffer(int i, int j, char* newElem);
    char** allocateMemory(int dim, size_t elem_size) const;
    void copyData(const AnyMatrix &data);
    void freeMemory();
    virtual AnyMatrix* getClone() const = 0;


protected:
    int dim = 0; // размерность матрицы 
    char** data = nullptr; 
    int elem_size; // размер одого элемента в байтах
};

// ***** ПУБЛИЧНЫЕ МЕТОДЫ AnyMatrix *************

AnyMatrix::AnyMatrix(int _dim, size_t _elem_size) { //  конструктор матрицы.
    dim = _dim;
    elem_size = _elem_size;
    data = allocateMemory(dim, elem_size); 
}

AnyMatrix::AnyMatrix(const AnyMatrix &matrix) { // конструктор копирования в инициализации
    data = allocateMemory(matrix.dim, matrix.elem_size);
    copyData(matrix);
}

AnyMatrix& AnyMatrix::operator=(AnyMatrix& matrix) { // перегрузка оператора = 
    if (this == &matrix) return *this; // если пытаемся скопировать сами себя, то возвращаем указатель на себя
    //freeMemory();
    //data = allocateMemory(matrix.dim, matrix.elem_size); // выделение памяти 
    copyData(matrix); // Копирование информации 
    return *this;
}

AnyMatrix::~AnyMatrix() { //деструктор 
    freeMemory();
}

void AnyMatrix::readElemInBuffer(int raw, int col, char* buffer) const { 
    // Копируем данные из ячейки в буфер. Предполагаем, что рахзмер буфера равен размеру ячейки (байт)
    // Пользуемся буфером, т.к. не AnyMatrix должен уметь работать с ячейками любого размера.
    memcpy(buffer, &data[raw][col*elem_size], elem_size);
}

void AnyMatrix::writeElemFromBuffer(int raw, int col, char* buffer) {
    // Аналогично чтению
    // Предполагается, что размер массива buffer равен elem_size
    memcpy(&data[raw][col*elem_size], buffer, elem_size);
}

int AnyMatrix::MaxRaw(int rawNum) const {
    char buffer_for_max[elem_size];
    char buffer_for_curr[elem_size];
    int max_index = 0;
    readElemInBuffer(rawNum, 0, buffer_for_max);

    for (int i = 1; i < dim; i++) {
        readElemInBuffer(rawNum, i, buffer_for_curr);
        if (compare(buffer_for_curr, buffer_for_max) >= 1) { // если левый больше, чем правый
            memcpy(buffer_for_max, buffer_for_curr, elem_size);
            max_index = i;
        }
    }
    return max_index;
}

int AnyMatrix::MaxCol(int colNum) const {
    char buffer_for_max[elem_size];
    char buffer_for_curr[elem_size];
    int max_index = 0;
    readElemInBuffer(0, colNum, buffer_for_max);

    for (int i = 1; i < dim; i++) {
        readElemInBuffer(i, colNum, buffer_for_curr);
        if (compare(buffer_for_curr, buffer_for_max) >= 1) { // если левый больше, чем правый
            memcpy(buffer_for_max, buffer_for_curr, elem_size);
            max_index = i;
        }
    }
    return max_index;
}

int AnyMatrix::MinRaw(int rawNum) const {
    char buffer_for_min[elem_size];
    char buffer_for_curr[elem_size];
    int min_index = 0;
    readElemInBuffer(rawNum, 0, buffer_for_min);

    for (int i = 1; i < dim; i++) {
        readElemInBuffer(rawNum, i, buffer_for_curr);
        if (compare(buffer_for_curr, buffer_for_min) <= -1) { // если левый больше, чем правый
            memcpy(buffer_for_min, buffer_for_curr, elem_size);
            min_index = i;
        }
    }
    return min_index;
}

int AnyMatrix::MinCol(int colNum) const {
    char buffer_for_min[elem_size];
    char buffer_for_curr[elem_size];
    int min_index = 0;
    readElemInBuffer(0, colNum, buffer_for_min);

    for (int i = 1; i < dim; i++) {
        readElemInBuffer(i, colNum, buffer_for_curr);
        if (compare(buffer_for_curr, buffer_for_min) <= -1) { // если левый меньше, чем правый
            memcpy(buffer_for_min, buffer_for_curr, elem_size);
            min_index = i;
        }
    }
    return min_index;
}

AnyMatrix* AnyMatrix::operator%(const AnyMatrix& rhs) const {
    AnyMatrix* returnMatrix = getClone();
    char max_elem[elem_size];
    char new_elem[elem_size];

    for (int raw_num = 0; raw_num < dim; raw_num++) {
        int max_col_index = rhs.MaxRaw(raw_num); // Ищем Индекс максимального элемента в строке
        rhs.readElemInBuffer(raw_num, max_col_index, (char*)&max_elem); // Получаем занчние этого макс. элемента
        memset(new_elem, 0, elem_size); // Обнуляем новую ячейку
        for (int col_num = 0; col_num < dim; col_num++) { // Делим строку в левой матрице на найдённый максимум во второй
            if (!isZero(max_elem)) // Если макс не ноль, находим частное. Иначе присваиваем ноль (далее)
                divide(&data[raw_num][col_num*elem_size], max_elem, new_elem);
            returnMatrix->writeElemFromBuffer(raw_num, col_num, new_elem);
        }
    }
    return returnMatrix;
}


AnyMatrix& AnyMatrix::operator~() {
    char min_elem[elem_size];
    char zero_elem[elem_size] = {'\0'};
    for (int col_num = 0; col_num < dim; col_num++) {
        int min_raw_index = MinCol(col_num);
        readElemInBuffer(min_raw_index, col_num, (char*)&min_elem);
        
        for (int raw_num = 0; raw_num < dim; raw_num++) {
            if (compare(min_elem, &data[raw_num][col_num*elem_size]) == 0)
                writeElemFromBuffer(raw_num, col_num, zero_elem);
        }
    }
    return *this;
}


// ***** ПРИВАТНЫЕ МЕТОДЫ AnyMatrix *************

char** AnyMatrix::allocateMemory(int dim, size_t elem_size) const { // выделение памяти для матрицы
    char** newData = new char*[dim]; // Создаем указатель на массив указателей и выделяем место под массив указателей на строки матрицы
    for (int i = 0; i < dim; i++) {
        newData[i] = new char[dim * elem_size]; // выделяем память под строки. кол-во элементов в строке умножаем на их вес
    }
    return newData;
}


void AnyMatrix::copyData(const AnyMatrix &source) { // копирование данных в матрицу 
    dim = source.dim;
    elem_size = source.elem_size;
    for (int i = 0; i < source.dim; i++)
        memcpy(data[i], source.data[i], elem_size*dim);
}

void AnyMatrix::freeMemory() { // очищает память
    for (int i = 0; i < dim; i++) {
        delete[] data[i]; // очишаем строки матрицы (с ячейками)
    }
    delete[] data; // Очищаем массив указателей на строки
}

std::istream& operator>>(std::istream& in, AnyMatrix& matrix) {
	for (int i = 0; i < matrix.dim; i++) {
        for (int j = 0; j < matrix.dim; j++) {
            matrix.inputElem(in, i, j); // Вызываем вирт. функцию чтения данных.
            // Т.к. функция виртуальная, то в нужная функция вызовется в момент выполнения программы.
        }
	}
    return in;
}

std::ostream& operator<<(std::ostream& out, const AnyMatrix& matrix) {
	for (int i = 0; i < matrix.dim; i++) {
        for (int j = 0; j < matrix.dim; j++) {
		    out << std::setw(2);
            matrix.outputElem(out, i, j); // Вызываем вирт. функцию вывода данных.
            // Т.к. функция виртуальная, то в нужная функция вызовется в момент выполнения программы (аналогично вводу).
        }
        out << std::endl;
	}
	return out;
}

bool AnyMatrix::fileInput(std::string filename) {
	std::ifstream fin(filename);
	if (!fin.is_open())
		return false;
	for (int i = 0; i < dim; i++) {
        for (int j = 0; j < dim; j++) {
            inputElem(fin, i, j);
        }
	}
    fin.close();
	return true;
}

int fileDim(std::string filename){ /////////////////////////////////////////////////
    std::ifstream fin(filename); ///////////////////////////////////////// 
	if (!fin.is_open()) /////////////////////////////////////////////////////
		return false;
    char symbol;
    int spaceInRaw=0;
    int symInRaw=0;
    while (!fin.eof()){
        fin.get(symbol);
        if (symbol == ' ') spaceInRaw++;
        if (symbol != '\n') symInRaw++;
        if (symbol == '\n') break;
    }
    fin.close();
    if (symInRaw-1 == 0) return 0;
    return spaceInRaw + 1;
}

bool AnyMatrix::fileOutput(std::string filename) const {
   	std::ofstream fout(filename);
	if (!fout.is_open())
		return false;
	for (int i = 0; i < dim; i++) {
        for (int j = 0; j < dim; j++) {
		    outputElem(fout, i, j);
            fout << " ";
        }
        fout << std::endl;
	}
	return true; 
}







class IntMatrix : public AnyMatrix {
public:
    IntMatrix(int dim); // Конструктор
    // Оператор присваивания создаётся автоматически.
    // Конструктор копирования создаётся автоматически.

    void inputElem(std::istream& in, int raw, int col) override; // Реализация метода чтения для матрицы целых чисел
    void outputElem(std::ostream& out, int raw, int col) const override; // Реализация метода вывода для матрицы целых чисел
    
    void fillMatrix(); // Для тестирования функицональности. Заполняет случайными числами от 0 до 10.
    // Функции для комфорта: вызывают виртуальные методы чтения и вывода ячеек матрицы.
    void writeElem(int i, int j, int elem); 
    int readElem(int i, int j) const;

    int compare(const char* lhs, const char* rhs) const override;
    bool isZero(const char* element) const override;
    void divide(const char* lhs, const char* rhs, char* result) const override;
    
    AnyMatrix* getClone() const override;
};



// ***** ПУБЛИЧНЫЕ МЕТОДЫ IntMatrix *************

IntMatrix::IntMatrix(int dim) : AnyMatrix(dim, sizeof(int)) {
    // Вызываем конструктор базвого класса, т.к. при наследовании объект создаётся как матрёшка.
    // Явно указываем размер типа int в байтах
}

// Реализация виртуальной функции ввода ячейки
void IntMatrix::inputElem(std::istream& in, int raw, int col) {
    int int_data;
    in >> int_data;
    writeElemFromBuffer(raw, col, (char*)&int_data);
}

// Реализация виртуальной функции вывода ячейки
void IntMatrix::outputElem(std::ostream& out, int raw, int col) const {
    int int_data;
    readElemInBuffer(raw, col, (char*)&int_data);
    out << int_data << " ";
}

void IntMatrix::writeElem(int raw, int col, int elem) {
    writeElemFromBuffer(raw, col, (char*)&elem);
}

int IntMatrix::readElem(int i, int j) const {
    int int_data;
    readElemInBuffer(i, j, (char*)&int_data);
    return int_data;
}

AnyMatrix* IntMatrix::getClone() const {
    return new IntMatrix(dim);
}


void IntMatrix::divide(const char* lhs, const char* rhs, char* result) const {
    int lhs_int, rhs_int, result_int;
    memcpy((char*)&lhs_int, lhs, elem_size);
    memcpy((char*)&rhs_int, rhs, elem_size);
    result_int = lhs_int / rhs_int;
    memcpy(result, (char*)&result_int, elem_size);
}





// ******** Реализаця вариантов

int IntMatrix::compare(const char* lhs, const char* rhs) const {
    int lhs_int, rhs_int;
    memcpy((char*)&lhs_int, lhs, elem_size);
    memcpy((char*)&rhs_int, rhs, elem_size);

    if (lhs_int > rhs_int)
        return 1;
    else if (lhs_int < rhs_int)
        return -1;
    else
        return 0;
}

bool IntMatrix::isZero(const char* element) const {
    int elem_int;
    memcpy((char*)&elem_int, element, elem_size);

    if (elem_int == 0)
        return true;
    else
        return false;
}

void IntMatrix::fillMatrix() {
    for (int i = 0; i < dim; i++)
        for (int j = 0; j < dim; j++)
            writeElem(i, j, rand() % 10);
}


int main() {
    IntMatrix matrix_1(3);
    // std::cin >> matrix_1;
    matrix_1.fillMatrix();
    std::cout << "Matrix 1:\n" << matrix_1 << std::endl;


    IntMatrix matrix_2(3);
    // std::cin >> matrix_2;
    matrix_2.fillMatrix();
    std::cout << "Matrix 2:\n" << matrix_2 << std::endl;

    IntMatrix matrix_3 = matrix_2; // вызываем конструктор копирования
    std::cout << "Matrix 3:\n" << matrix_3 << std::endl;


    IntMatrix matrix_4(fileDim("mat.txt"));
    matrix_4.fileInput("mat.txt");
    std::cout << "Matrix 4:\n" << matrix_4 << std::endl;

    AnyMatrix* result_10 = matrix_1 % matrix_2;
    std::cout << "Result of % operator:" << std::endl;
    std::cout << *result_10 << std::endl;
    
    std::cout << "Results of ~ operator:" << std::endl;
    std::cout << ~matrix_1 << std::endl;
    std::cout << ~matrix_2 << std::endl;

    delete(result_10);
}
