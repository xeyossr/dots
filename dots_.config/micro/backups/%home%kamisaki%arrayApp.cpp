Q#include <iostream>

std::string newLine;

int main() {
	std::cout << "Kac buyuklukte olcak bu ustad? >> ";
	int arraySize;
	std::cin >> arraySize;

	std::cin.ignore();
	
	std::string tersArray[arraySize];
	std::string myArray[arraySize];

	for (int i=0; i < arraySize; i++) {
		std::cout << "Array'e ekle:";
		std::string arrayEklenecek;
		std::getline(std::cin,arrayEklenecek);
		myArray[i] = arrayEklenecek;
		
	}

	for (int i=0; i < arraySize; i++) {
		if (i == arraySize - 1) {
			newLine += "\"" + myArray[i] + "\"";
			break;
		}
		
		newLine += "\"" + myArray[i] + "\", ";
	}	

	std::cout << "[" << newLine << "]\n";
	std::string newLineTers;
	
	for (int i=0; i < arraySize; i++) {
		tersArray[i] = myArray[arraySize-1 - i];
		newLineTers += "\"" + tersArray[i] + "\",";
	}

	std::cout << "== TERS ARRAY ==" << "\n";
	std::cout << "[" << newLineTers << "]\n";
	
	return 0;
}
