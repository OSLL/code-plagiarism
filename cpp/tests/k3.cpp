#include <iostream>
#include <string>
#include <fstream>
#include <math.h>

class BaseMatrix
{
public:
    int matrixSize;
    int byteSize;

    char *matrix = NULL;

    virtual void input(std::istream &in, char *element){};
    virtual void output(std::ostream &out, char *element){};

    void fileOutput(std::string fileName);

    friend std::istream &operator>>(std::istream &in, BaseMatrix &matrixToIn);
    friend std::ostream &operator<<(std::ostream &out, BaseMatrix &matrixToOut);

    int findColMin(int columnIndex);

    void editElement(); // dich

    BaseMatrix operator=(const BaseMatrix &toCopyMatrix);
    BaseMatrix operator~();

    BaseMatrix(){};
    BaseMatrix(int);
    BaseMatrix(BaseMatrix &toCopyMatrix);
    ~BaseMatrix();
};

void BaseMatrix::fileOutput(std::string fileName)
{
    std::ofstream file(fileName.c_str());
    if (!file)
        std::cout << "\nОшибка записи в файл\n";
    else
    {
        for (int i = 0; i < this->matrixSize; i++)
        {
            for (int j = 0; j < this->matrixSize; j++)
                this->output(file, this->matrix + i * this->byteSize * this->matrixSize + j * this->byteSize);
            file << "\n";
        }
    }
    file.close();
};

std::istream &operator>>(std::istream &in, BaseMatrix &matrixToIn)
{
    for (int i = 0; i < matrixToIn.matrixSize; i++)
    {
        std::cout << "Enter the " << i + 1 << " of " << matrixToIn.matrixSize << " rows:\n";
        for (int j = 0; j < matrixToIn.matrixSize; j++)
            matrixToIn.input(in, matrixToIn.matrix + i * matrixToIn.byteSize * matrixToIn.matrixSize + j * matrixToIn.byteSize);
    }
    return in;
}

std::ostream &operator<<(std::ostream &out, BaseMatrix &matrixToOut)
{
    for (int i = 0; i < matrixToOut.matrixSize; i++)
    {
        for (int j = 0; j < matrixToOut.matrixSize; j++)
        {
            matrixToOut.output(out, matrixToOut.matrix + i * matrixToOut.byteSize * matrixToOut.matrixSize + j * matrixToOut.byteSize);
            std::cout << " ";
        }
        std::cout << "\n";
    }
    return out;
}

int BaseMatrix::findColMin(int columnIndex)
{
    char *min = new char[this->byteSize];
    min = this->matrix + columnIndex * this->byteSize;
    /*std::cout << min << std::endl
              << *min << std::endl
              << (int *)min << std::endl
              << *(int *)min << std::endl
              << "---" << *(int *)(this->matrix + 0 * this->matrixSize * this->byteSize + (columnIndex - 1) * this->byteSize) << std::endl
              << "---" << *(int *)(this->matrix + 1 * this->matrixSize * this->byteSize + (columnIndex - 1) * this->byteSize);
    */
    for (int i = 0; i < this->matrixSize; i++)
        if ((*(int *)(this->matrix + i * this->matrixSize * this->byteSize + columnIndex * this->byteSize)) < (*(int *)min))
            min = this->matrix + i * this->matrixSize * this->byteSize + columnIndex * this->byteSize;
    //matrixToIn.input(in, matrixToIn.matrix + i * matrixToIn.byteSize * matrixToIn.matrixSize + j * matrixToIn.byteSize);
    //std::cout << *(int *)min;
    return (*(int *)min);
}

void BaseMatrix::editElement()
{
    int i, j, value;
    while (true)
    {
        std::cout << "\nPosition of the element to edit (row and column from 1 to " << this->matrixSize << " for " << this->matrixSize << "x" << this->matrixSize << " matrix) is: ";
        std::cin >> i >> j;
        if (i > 0 && i <= this->matrixSize && j > 0 && j <= this->matrixSize)
            break;
        else
            std::cout << "Please enter a valid row and column values\n";
    }
    std::cout << "New element value: ";
    input(std::cin, this->matrix + (i - 1) * this->byteSize * this->matrixSize + (j - 1) * this->byteSize);
};

BaseMatrix BaseMatrix::operator=(const BaseMatrix &toCopyMatrix)
{
    if (this->matrixSize != toCopyMatrix.matrixSize)
    {
        if (this->matrix)
            delete this->matrix;
        this->byteSize = toCopyMatrix.byteSize;
        this->matrixSize = toCopyMatrix.matrixSize;
        this->matrix = new char[this->byteSize * this->matrixSize * this->matrixSize];
    }
    for (int i = 0; i < this->byteSize * this->matrixSize * this->matrixSize; i++)
        this->matrix[i] = toCopyMatrix.matrix[i];
    return (*this);
}

BaseMatrix BaseMatrix::operator~()
{
    char *zeroToReplace = new char[this->byteSize];
    zeroToReplace = {"\0"};
    int columnMin;
    for (int j = 0; j < this->matrixSize; j++)
    {
        columnMin = this->findColMin(j);
        for (int i = 0; i > this->matrixSize; i++)
        {
            if (columnMin == (*(int *)(this->matrix + i * this->matrixSize * this->byteSize + j * this->byteSize)))
                this->matrix = zeroToReplace;
        }
    }
    //min = this->matrix + i * this->matrixSize * this->byteSize
    //+ columnIndex * this->byteSize;
    return *this;
}

BaseMatrix::BaseMatrix(int matrixSize)
{
    this->byteSize = sizeof(int);
    this->matrixSize = matrixSize;
    this->matrix = new char[this->byteSize * this->matrixSize * this->matrixSize];
}

BaseMatrix::BaseMatrix(BaseMatrix &toCopyMatrix)
{
    this->byteSize = toCopyMatrix.byteSize;
    this->matrixSize = toCopyMatrix.matrixSize;
    this->matrix = new char[this->byteSize * this->matrixSize * this->matrixSize];
    for (int i = 0; i < this->byteSize * this->matrixSize * this->matrixSize; i++)
        this->matrix[i] = toCopyMatrix.matrix[i];
}

BaseMatrix::~BaseMatrix()
{
    delete this->matrix;
}

//------------------------------------------------------------------

class ChildMatrix : public BaseMatrix
{
public:
    void input(std::istream &in, char *element);
    void output(std::ostream &out, char *element);

    ChildMatrix(){};
    ChildMatrix(std::string fileName);
    ChildMatrix(BaseMatrix &toCopyMatrix) : BaseMatrix(toCopyMatrix){};
    ChildMatrix(int);
};

void ChildMatrix::input(std::istream &in, char *element)
{
    in >> *((int *)element);
}

void ChildMatrix::output(std::ostream &out, char *element)
{
    out << *((int *)element);
}

ChildMatrix::ChildMatrix(std::string fileName)
{
    std::string buffer;
    std::ifstream file(fileName.c_str());
    if (!file)
    {
        std::cout << "\nОшибка чтения файла\n";
    }
    else
    {
        while (file)
        {
            this->matrixSize += 1;
            file >> buffer;
        }
        matrixSize = sqrt(matrixSize);
        this->byteSize = sizeof(int);
        matrix = new char[this->byteSize * this->matrixSize * this->matrixSize];
        file.clear();
        file.seekg(0);
        for (int i = 0; i < this->matrixSize; i++)
        {
            for (int j = 0; j < this->matrixSize; j++)
                this->input(file, matrix + i * this->byteSize * this->matrixSize + j * this->byteSize);
        }
    }
    file.close();
}

ChildMatrix::ChildMatrix(int size) : BaseMatrix(size)
{
    std::cin >> *this;
}

int main()
{
    //setlocale(LC_CTYPE, "Russian");
    BaseMatrix *matrix, *utilityMatrix;
    unsigned int menuButton, matrixSize;
    do
    {
        std::cout << "Select input type please:\n"
                     "1 - File\n"
                     "2 - From the keyboard\n"
                     "Your choise: ";
        std::cin >> menuButton;
        if ((menuButton != 1) && (menuButton != 2))
            std::cout << "Please select the correct menu item to continue\n\n";
    } while ((menuButton != 1) && (menuButton != 2));
    if (menuButton == 1)
    {
        matrix = new ChildMatrix("input.txt");
    }
    else
    {
        std::cout << "Enter the size of the matrix: ";
        std::cin >> matrixSize;
        matrix = new ChildMatrix(matrixSize);
    }
    std::cout << "Matrix is:\n"
              << *matrix;

    while (true)
    {
        std::cout << "\nSelect one of the menu items please:\n"
                     "1 - Copy constructor\n"
                     "2 - Matrix assignment\n"
                     "3 - Edit the matrix\n"
                     "4 - 1\n"
                     "5 - 2\n"
                     "0 - Exit\n"
                     "Your choise: ";
        std::cin >> menuButton;
        switch (menuButton)
        {
        case 1:
            utilityMatrix = new ChildMatrix(*matrix);
            std::cout << "Matrix is:\n"
                      << *utilityMatrix;
            break;
        case 2:
            utilityMatrix = new ChildMatrix(matrix->matrixSize - 1);
            *utilityMatrix = *matrix;
            std::cout << "Matrix is:\n"
                      << *utilityMatrix;
            break;
        case 3:
            matrix->editElement();
            std::cout << "Matrix is:\n"
                      << *matrix;
            break;
        case 4:
            //utilityMatrix = new ChildMatrix(matrix->matrixSize);
            //*utilityMatrix = *matrix ~ *utilityMatrix;
            //~*matrix;
            std::cout << "Matrix is:\n"
                      << matrix->findColMin(1);
            //<< *(int *)(matrix->findColMin(1));
            break;
        case 5:
            break;
        case 0:
            return 0;
        }
    }
    system("pause");
}