Witaj w aplikacji Alfa Trader!

Spis zagadnien:
1. O aplikacji
2. W jaki sposob zainstalowac aplikacje
3. Wymagania aplikacji i pierwsze uruchomienie
4. Dzialanie aplikacji
5. Zasady tradingu

1. O aplikacji

Aplikacja Alfa Trader napisana zostala jako praca zaliczeniowa do kursu Full Stack Python Developer w CodersLab.
Ze wzgledu na doswiadczenie autora projektu w finansach jak i wymagania co do aplikacji zostalo ustalone ze
projektem najbardziej spelniajacym zarowno wymagania techniczne, wymagania egzaminacyjne jak i zainteresowania autora
bedzie utworzenie aplikacji w formie gry symulujacej trading na gieldzie papierow wartosciowcyh.

Aplikacja bazuje na oficjalnych notowaniach akcji na gieldach GPW, NYSE i NASDAQ ktore sa przez nia zaciagane i przetwarzane
po recznym zapisaniu ich w folderze aplikacji. Na podstawie zaimportowanych notowan aplikacja dla kazdej akcji tworzy
wykres zmiany ceny pozwlalajacy na analize trendu a takze przewidywan co do dalszego kierunku ich zmiany.

Na podstawie wlasnych subiektywnej oceny na podstawie tych wykresow jak i informacji i raportow zewnetrznych odnosnie
sytuacji finansowej firmie - uzytkownik/gracz podejmuje decyzje o zakupie/sprzedazy akcji.

Kazdy nowo zalogowany uzytkownik dysponuje kapitalem wstepnym na poziomie 10.000,00 USD ktore moze przeznaczyc na zakup
wybranych akcji. Kazda transakcja zakupu lub sprzedazy obciazona jest kosztem transakcyjnym w wyskokosci 0.2%
lecz minimum 10,00 USD. Gracz na podstawie wlasnych analiz dazy do jak najskuteczniejszego pomnozenia wlasnego kapitalu
poprzez zakup akcji a nastepnie ich sprzedaz po wyzszej cenie.

2. W jaki sposob zainstalowac aplikacje

Aplikacja dostepna jest do sciagniecia na platformie GitHub pod adresem: https://github.com/marcustroh/AlfaTrader .
Uzytkownik poprzez klikniecie na przycisk code->download zip lub poprzez terminal kopiujac spod przycisku code -
link do aplikacji a nastepnie wpisujac w terminalu:
git clone <link>

3. Wymagania aplikacji i pierwsze uruchomienie

By rozpoczac dzialanie aplikacji potrzebujemy instalacj biblitek ktore powinny zostac zainstalowane na nowym wirtualnym
srodowisku. By to zrobic przechodzimy w terminalu do lokalizacji w ktrej chcemy ja utworzyc a nastepnie wpisujemy
w terminalu:
>python -m venv myenv
Po utworzeniu przystepujemy do aktywacji srodwoskia poprzez ponizsza komende:
>source myenv/bin/activate

Aplikacja do dzialania potrzebuje do dzialania instalacji bibliotek ktore sa wylistowane w pliku requirement.txt.
Aby je zainstalowac nalezy:
> Przejsc do katalogu w ktorym znajduje sie plik requirements.txt
 cd /AlfaTrader/requirements.txt
> Zainstalowac biblioteki z pliku wpisujac w terminalu:
 pip install -r requirements.txt

 Po zakonczonym procesie nstalacji przechodzimy do lokalizacji aplikacji:
 > cd /AlfaTrader/
 i wpisujemy w terminalu komende pozwalajaca na utworzenie potrzebnych baz danych
 1. python manage.py makemigratios
 2. python manage.py migrate

Po procesie migracji zakonczonym sukcesem wpisujemy ponizsza komende by uruchomic aplikacje:
> python manage.py runserver

Powyzsza komenda uruchamia wirtualny serwer ktory uruchamia aplikacje dzialajace w przegladarce pod linkiem:
http://127.0.0.1:8000/

4. Dzialanie aplikacji
By przystapic do gry nalezy zaczac od utworzenia uzytkownika. Robimy to klikajac na przycisk Sign Up i podajac swoje
dane. Po rejestracji uzytkownik jest automatycznie zalogowany i moze przystapic do gry.
By zaczac trading nalezy kliknac na przycisk Transaction Dashboard ktory kazdego nowego dnia bedzie prosil i zapisanie ostatniego
pliku z notowaniami w lokalizacji:
>AlfaTrader/AlfaTrader_App/quotes/txt/

Po dokonaniu zapisu aplikacji poprosi o zatwierdzenie zapisu pliku poprzez nacisniecie przycisku "OK, I have saved down the file".
Po jego klikniecu aplikacja zapisueje notowania do bazy danych umozliwiajac tworzenie wykresu zmiany ceny przez pryzmat
uplywu czasu od rozpoczecia gry.

Aplikacja poprzez wejscie w szczegoly danej firmy wylistowanej na Transaction Deshboard pozwala wejsc w szczegoly umozliwiajace
zakup i sprzedaz akcji.

Zakladka Transactions History umozliwia monitorowanie wykonanych transakcji a takze oplat przypisanych do tych transackji.

Celem monitorowania zyskownosci inwestycji obecna jest zakladka Portfolios umozliwiajace tworzenie portfeli juz posiadanych
akcji ktore mozemy dopasowac do profilu ryzyka inwestycji, sektora firmy lub na podstawie innej subiektywnej oceny.

Kazdy portfel po przypisaniu do niego akcji pozwala na bazie dziennej na monitorowanie zyskownosci inwestycji
pomagajacej w podejciu decyzji i sprzedazy posiadanych akcji.

5. Zasady tradingu

Ogolne i podstawowe zasady tradingu polegaja na zakupie a nastepnie sprzedazy zakupionych akcji z jak najwiekszym zyskiem.
Uzytkownik podejmujac decyzje o zakupie lub sprzedazy musi pamietach o oplatach transakcyjnych obowiazujacych zarowno
dla zakupu jak i sprzedazy - ktore jednoczesnie pomniejszaja zyskownosci inwestycji.
Aplikacja umowliwia tworzenie jedynie dlugich pozycji wiec zabroniona jest krotka sprzedaz.

Cena zakopionych juz akcji sluzaca do wyliczenia wyniku ze sprzedazy jest zgodnie z wymogami ewidencji papierow wartosiowych
i innych aktywow wyliczana na podstawie sredniej wazonej ceny zakupu - wiec ceny pojedycznej akcji przemnozonej przez
ilosc zakupionych akcji.

Przy sprzedazy jednostkowych akcji zastosowana zostala metoda FIFO ktora w pierwszej kolejnosci usuwa z portfela branego do
kalkulacji sredniej wazonej ceny zakupu - akcje zakupione jako pierwsze wiec te najstarsze. Z kazda wiec jednostkowa
transakcja sprzedazy wyliczona srednia wazona cena zakupu ulega zmianie i jako zaktualizowana wartosc jest
brana do wyliczenia wyniku ze sprzedazy.

Kazdorazowa transkacja zakupu akcji pomniejsza saldo dostepnej gotowki ozytkownika. Kazda transakcja sprxedazy powieksza
saldo gotowki dostepnej uzytkownika.

