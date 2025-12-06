import os
import random
import shutil
import argparse

# Funkcja do podziału danych
def split_data(src_folder, dst_folder_training, dst_folder_validation, dst_folder_test, test_size=5, training_size=0.7, validation_size=0.3):
    # Pobranie listy plików w folderze źródłowym
    all_files = [f for f in os.listdir(src_folder) if os.path.isfile(os.path.join(src_folder, f))]
    
    # Losowe pomieszanie listy plików
    random.shuffle(all_files)
    
    # Podział na 70% do treningu i 30% do walidacji
    num_training = int(len(all_files) * training_size)
    num_validation = int(len(all_files) * validation_size)
    
    # Wybieramy pierwsze 5 zdjęć do testu
    test_files = all_files[:test_size]
    
    # Pozostałe zdjęcia (po wyjęciu testowych) dzielimy na treningowe i walidacyjne
    remaining_files = all_files[test_size:]
    
    training_files = remaining_files[:num_training]
    validation_files = remaining_files[num_training:num_training + num_validation]
    
    # Przenoszenie plików do odpowiednich folderów
    for file in test_files:
        shutil.move(os.path.join(src_folder, file), os.path.join(dst_folder_test, file))

    for file in training_files:
        shutil.move(os.path.join(src_folder, file), os.path.join(dst_folder_training, file))

    for file in validation_files:
        shutil.move(os.path.join(src_folder, file), os.path.join(dst_folder_validation, file))

    print(f"Podział zakończony:\n- {len(training_files)} plików w folderze treningowym")
    print(f"- {len(validation_files)} plików w folderze walidacyjnym")
    print(f"- {len(test_files)} plików w folderze testowym")

# Funkcja główna do parsowania argumentów
def main():
    parser = argparse.ArgumentParser(description="Podziel folder zdjęć na treningowy, walidacyjny i testowy.")
    
    # Argumenty do podania ścieżek
    parser.add_argument("src_folder", help="Ścieżka do folderu źródłowego z zdjęciami")
    parser.add_argument("dst_folder_training", help="Ścieżka do folderu dla treningu")
    parser.add_argument("dst_folder_validation", help="Ścieżka do folderu dla walidacji")
    parser.add_argument("dst_folder_test", help="Ścieżka do folderu dla testu")
    
    # Parsowanie argumentów
    args = parser.parse_args()
    
    # Tworzymy foldery docelowe, jeśli nie istnieją
    os.makedirs(args.dst_folder_training, exist_ok=True)
    os.makedirs(args.dst_folder_validation, exist_ok=True)
    os.makedirs(args.dst_folder_test, exist_ok=True)
    
    # Uruchamiamy funkcję podziału
    split_data(args.src_folder, args.dst_folder_training, args.dst_folder_validation, args.dst_folder_test)

# Uruchomienie skryptu
if __name__ == "__main__":
    main()
