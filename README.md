# LogistAPP
Aplikacja obliczająca problem logistyczny metodą CPM

## Uruchomienie
Plik `app.exe` w folderze `dist`

## Działanie
Po uruchomieniu aplikacji można edytować tabelę zmieniając jej dane, dodawać wiersze lub importować pliki csv z gotowymi danymi poprzez przycisk lub przeciągnięcie pliku do okna aplikacji.
Graf aktualizuje się w czasie rzeczywistym.
Przykładowe dane znajdują się w folderze `samples`

## Dla developerów
Wymagania: 
```
PySide6
networkx
graphviz
```
```
pip install pyside6 networkx graphviz
```
`https://graphviz.org/download/#windows`

Uruchom `python .\app.py`

Do stworzenia EXE
Wymagania 
```
pip install pyinstaller
```
```
pyinstaller --noconfirm --windowed --onefile --add-data "graphviz;graphviz" --add-data "samples;samples" app.py
```