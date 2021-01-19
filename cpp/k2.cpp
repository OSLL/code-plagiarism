#include <iostream>
#include <fstream>
#include <iomanip>
#include <cstring>
#include <bits/stdc++.h>

class base_matrix {
public:
    base_matrix(int _matrix_size, size_t _elem_size);
    base_matrix(const base_matrix& matrix);
    virtual ~base_matrix();
    virtual void input(std::istream& in, int row, int col) = 0;
    virtual void output(std::ostream& out, int row, int col) const = 0;
    bool input_file(std::string filename);
    bool output_file(std::string filename) const;
    virtual int comparesion(const char* lhs, const char* rhs) const = 0;
    base_matrix& operator=(base_matrix& right); // перегрузка оператора =
    friend std::istream& operator>>(std::istream& in, base_matrix& matrix);// перегрузка >>
    friend std::ostream& operator<<(std::ostream& out, const base_matrix& matrix);//  перегрузка <<
    /*
     *  true, если все диагональные элементы первой матрицы были бы
     * не равны соответствующим элементам второй матрицы
     */
    friend bool operator!=(const base_matrix& left, const base_matrix& right);
protected:
    int matrix_size = 0;
    char** data = nullptr;
    int element_size;
protected:
    char** memory_allocation(int dim, size_t elem_size) const;
    void copy(const base_matrix& data);

};

class derived_matrix : public base_matrix {
public:
    derived_matrix(int dim); 
    int comparesion(const char* lhs, const char* rhs) const override;
    void input(std::istream& in, int raw, int col) override; 
    void output(std::ostream& out, int raw, int col) const override; 
    void write_element(int i, int j, int elem);
    int read_element(int i, int j) const;
    /*
     * в результате выполнения операции -- в матрице удаляется строка и столбец,
     * на пересечении которых находится минимальный элемент матрицы
     */
    derived_matrix& operator--();
};

base_matrix::base_matrix(int _dim, size_t _elem_size) { //  конструктор матрицы.
    matrix_size = _dim;
    element_size = _elem_size;
    data = memory_allocation(matrix_size, element_size); 
}

base_matrix::base_matrix(const base_matrix &matrix) { // конструктор копирования в инициализации
    data = memory_allocation(matrix.matrix_size, matrix.element_size);
    copy(matrix);
}


base_matrix::~base_matrix() { //деструктор 
    for (int i = 0; i < matrix_size; i++) {
        delete[] data[i]; 
    }
    delete[] data; 
}

char** base_matrix::memory_allocation(int matrix_size, size_t elem_size) const { // выделение памяти для матрицы
    char** new_data = new char*[matrix_size];
    for (int i = 0; i < matrix_size; i++) {
        new_data[i] = new char[matrix_size * elem_size]; 
    }
    return new_data;
}

void base_matrix::input(std::istream& in, char** matrix, int row, int col)
{
    in >> matrix[row][col];
}

void base_matrix::output(std::ostream& out, char** matrix, int row, int col) const
{
    out << ((float*)matrix[row])[col] << " ";
}

void base_matrix::copy(char** left, char** right, int i, int j)
{
    left[i])[j] = right[i])[j];
}

base_matrix& base_matrix::operator=(base_matrix& matrix) { // перегрузка оператора = 
    if (this == &matrix) return *this;
    copy(matrix);
    return *this;
}


std::istream& operator>>(std::istream& in, base_matrix& matrix) { // перегрузка >>
	for (int i = 0; i < matrix.matrix_size; i++) {
        for (int j = 0; j < matrix.matrix_size; j++) {
            matrix.input(in, i, j); 
        }
	}
    return in;
}

std::ostream& operator<<(std::ostream& out, const base_matrix& matrix) {// перегрузка <<
	for (int i = 0; i < matrix.matrix_size; i++) {
        for (int j = 0; j < matrix.matrix_size; j++) {
		    out << std::setw(2);
            matrix.outputElem(out, i, j); 
        }
        out << std::endl;
	}
	return out;
}

bool base_matrix::input_file(std::string filename) {
	std::ifstream file(filename);
	if (!file.is_open())
		return false;
	for (int i = 0; i < matrix_size; i++) {
        for (int j = 0; j < matrix_size; j++) {
            input(file, i, j);
        }
	}
    file.close();
	return true;
}

int fileDim(std::string filename){ 
    std::ifstream file(filename); 
	if (!file.is_open()) 
		return false;
    char symbol;
    int space=0;
    int sum_elements=0;
    while (!file.eof()){
        file.get(symbol);
        if (symbol == ' ') 
            space++;
        if (symbol != '\n')
            sum_elements++;
        if (symbol == '\n') 
            break;
    }
    file.close();
    if (sum_elements-1 == 0) return 0;
    return space + 1;
}

bool base_matrix::output_file(std::string filename) const {
   	std::ofstream out(filename);
	if (!out.is_open())
		return false;
	for (int i = 0; i < matrix_size; i++) {
        for (int j = 0; j < matrix_size; j++) {
		    outputElem(out, i, j);
            out << " ";
        }
        out << std::endl;
	}
	return true; 
}


derived_matrix::derived_matrix(int dim) : base_matrix(dim, sizeof(int)) {//контруктор
   
}


void derived_matrix::write_element(std::istream& in, char** matrix, int row, int col)
{
    in >> ((int*)matrix[row])[col];
}

void base_matrix::copy(char** left, char** right, int row, int col)
{
    ((int*)left[row])[col] = ((int*)right[row])[col];
}

void derived_matrix::read_element(std::ostream& out, char** matrix, int i, int j) const
{
    out << ((int*)matrix[i])[j] << " ";
}

int IntMatrix::comparesion(const char* lhs, const char* rhs) const {
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


// индивидуальное задание

bool operator!=(const base_matrix& left, const base_matrix& right) { //перегрзка !=
    bool result = false;
    char left_elem[left.element_size];
    char right_elem[right.element_size];
    if (left.matrix_size == right.matrix_size) {
        for (int row_num = 0; row_num < left.matrix_size; row_num++) {
            if (left.comparison((int*)&left_elem, (int*)&right_elem) == 0) {
                result = true;
            }
            else {
                result = false;
                break;
            }
        }
    }
    return result;
}

derived_matrix& derived_matrix:: operator--() {
    if (matrix_size < 3) return *this;

    int min = INT_MAX;
    char cur_elem[element_size];
    int col = 0;
    int row = 0;

    for (int col_num = 0; col_num < matrix_size; col_num++) {
        for (int row_num = 0; row_num < matrix_size; row_num++) { 
            if ((int)*cur_elem < min) {
                min = (int)*cur_elem;
                col = col_num;
                row = row_num;
            }
        }
    }
    std::cout << "The smallest element is " << min << " in [" << row << ", " << col << "]" << std::endl;

    derived_matrix* new_matrix = new derived_matrix(matrix_size - 1);

    for (int row_num = 0; row_num < matrix_size; row_num++) {
        for (int col_num = 0; col_num < matrix_size; col_num++) {
            if (row_num < row) {
                int elem = read_element(row_num, col_num);
                if (col_num < col) new_matrix->write_element(row_num, col_num, elem);
                if (col_num > col) new_matrix->write_element(row_num, col_num - 1, elem);
            }
            if (row_num > row) {
                int elem = read_element(row_num, col_num);
                if (col_num < col) new_matrix->write_element(row_num - 1, col_num, elem);
                if (col_num > col) new_matrix->write_element(row_num - 1, col_num - 1, elem);
            }
        }
    }
    *this = *new_matrix;

    delete(new_matrix);

    return *this;
}

int main() {
    derived_matrix matrix_4(fileDim("mat.txt"));
    matrix_4.input_file("mat.txt");
    std::cout << "Matrix 4:\n" << matrix_4 << std::endl;

   
    derived_matrix matrix_3 = matrix_2; 
    std::cout << "Matrix 3:\n" << matrix_3 << std::endl;

  

    std::cout << "Results of -- operator:" << std::endl;
    std::cout << --matrix_1 << std::endl;
    std::cout << --matrix_2 << std::endl;

    std::cout << "Results of != operator:" << std::endl;
    std::cout << (matrix_1 != matrix_1) << std::endl;
    std::cout << (matrix_1 != matrix_2) << std::endl;
}
