import pprint
import json
import os

class Film:
    def __init__(self, tytul: str, gatunki: list, czasTrwania: int, tematyka: list, styl: str, jezyk: str, intensywnosc: int, okresHistoryczny: str):
        self.tytul: str = tytul
        self.gatunki: list = gatunki
        self.czasTrwania: int = czasTrwania
        self.tematyka: list = tematyka
        self.styl: str = styl
        self.jezyk: str = jezyk
        self.intensywnosc: int = intensywnosc
        self.okresHistoryczny: str = okresHistoryczny

    def __str__(self) -> str:
        return f"{self.tytul} ({self.okresHistoryczny} - {self.jezyk})"

    def wyswietlSzczegoly(self) -> dict:
        details: dict = {
            "Tytuł": self.tytul,
            "Gatunki": ", ".join(self.gatunki),
            "Czas trwania": f"{self.czasTrwania} min",
            "Tematyka": ", ".join(self.tematyka),
            "Styl": self.styl,
            "Język": self.jezyk,
            "Poziom intensywności": f"{self.intensywnosc}/10",
            "Okres historyczny": self.okresHistoryczny
        }
        return details

BAZA_FILMOW_WOJENNYCH_POLITYCZNYCH: list = []

class SystemRekomendacji:
    def __init__(self, dane_filmow_wejsciowe: list):
        self.listaFilmow: list = [Film(**daneFilmu) for daneFilmu in dane_filmow_wejsciowe]
        self.wagiCech: dict = {
            "gatunek": 0.20,
            "tematyka": 0.20,
            "okresHistoryczny": 0.20,
            "styl": 0.10,
            "intensywnosc": 0.15,
            "czasTrwania": 0.10,
            "jezyk": 0.05,
        }

        if self.listaFilmow:
            self.dostepneGatunki: list = sorted(list(set(g for film in self.listaFilmow for g in film.gatunki)))
            self.dostepneTematy: list = sorted(list(set(t for film in self.listaFilmow for t in film.tematyka)))
            self.dostepneStyle: list = sorted(list(set(film.styl for film in self.listaFilmow)))
            self.dostepneJezyki: list = sorted(list(set(film.jezyk for film in self.listaFilmow)))
            self.dostepneOkresyHistoryczne: list = sorted(list(set(film.okresHistoryczny for film in self.listaFilmow)))
            self.dostepneOkresyOpcjaDowolny: list = self.dostepneOkresyHistoryczne + ["dowolny"]
        else:
            self.dostepneGatunki = []
            self.dostepneTematy = []
            self.dostepneStyle = []
            self.dostepneJezyki = []
            self.dostepneOkresyHistoryczne = []
            self.dostepneOkresyOpcjaDowolny = ["dowolny"]


    def _pobierzPreferencjeUzytkownika(self) -> dict:
        preferencje: dict = {}
        print("\nWprowadź swoje preferencje filmowe:")

        if not self.dostepneGatunki:
            preferencje["gatunki"] = []
        else:
            print(f"\nDostępne gatunki: {', '.join(self.dostepneGatunki)}")
            while True:
                suroweGatunki: str = input("Preferowane gatunki (oddzielone przecinkami): ").lower()
                preferencje["gatunki"] = [g.strip() for g in suroweGatunki.split(',') if g.strip()]
                if preferencje["gatunki"]:
                    break
                print("Proszę podać przynajmniej jeden gatunek.")

        if not self.dostepneTematy:
            preferencje["tematyka"] = []
        else:
            print(f"\nDostępne tematy: {', '.join(self.dostepneTematy)}")
            while True:
                suroweTematy: str = input("Preferowane tematy (oddzielone przecinkami): ").lower()
                preferencje["tematyka"] = [t.strip() for t in suroweTematy.split(',') if t.strip()]
                if preferencje["tematyka"]:
                    break
                print("Proszę podać przynajmniej jeden temat.")
        
        if not self.dostepneStyle:
            preferencje["styl"] = ""
        else:
            print(f"\nDostępne style: {', '.join(self.dostepneStyle)}")
            while True:
                wybranyStyl: str = input(f"Preferowany styl (wybierz jeden): ").lower().strip()
                if wybranyStyl in self.dostepneStyle:
                    preferencje["styl"] = wybranyStyl
                    break
                print(f"Nieprawidłowy styl. Wybierz z listy: {', '.join(self.dostepneStyle)}")

        while True:
            try:
                idealnyCzas: int = int(input("Preferowany czas trwania filmu (w minutach, np. 120): "))
                tolerancjaCzasu: int = int(input("Tolerancja czasu trwania (+/- minut, np. 20): "))
                if idealnyCzas > 0 and tolerancjaCzasu >= 0:
                    preferencje["idealnyCzasTrwania"] = idealnyCzas
                    preferencje["tolerancjaCzasuTrwania"] = tolerancjaCzasu
                    break
                else:
                    print("Czas trwania i tolerancja muszą być wartościami dodatnimi.")
            except ValueError:
                print("Nieprawidłowa wartość. Proszę podać liczbę.")

        listaWyswietlanychJezykow: list = sorted(list(set(self.dostepneJezyki + ["Dowolny"])))
        if not self.dostepneJezyki and "Dowolny" not in listaWyswietlanychJezykow :
             listaWyswietlanychJezykow.append("Dowolny")

        if not self.dostepneJezyki :
            preferencje["jezyk"] = "Dowolny"
        else:
            print(f"\nDostępne języki: {', '.join(listaWyswietlanychJezykow)}")
            while True:
                wybranyJezyk: str = input(f"Preferowany język (lub 'Dowolny'): ").strip()
                znaleziono_jezyk: bool = False
                for dostJezyka in listaWyswietlanychJezykow:
                    if wybranyJezyk.lower() == dostJezyka.lower():
                        preferencje["jezyk"] = dostJezyka 
                        znaleziono_jezyk = True
                        break
                if znaleziono_jezyk:
                    break
                print(f"Nieprawidłowy język. Wybierz z listy.")

        while True:
            try:
                preferowanaIntensywnosc: int = int(input("Preferowany poziom intensywności (0-10): "))
                if 0 <= preferowanaIntensywnosc <= 10:
                    preferencje["intensywnosc"] = preferowanaIntensywnosc
                    break
                else:
                    print("Intensywność musi być między 0 a 10.")
            except ValueError:
                print("Nieprawidłowa wartość. Proszę podać liczbę.")

        if not self.dostepneOkresyHistoryczne:
            preferencje["okresHistoryczny"] = "dowolny"
        else:
            print(f"\nDostępne okresy historyczne: {', '.join(self.dostepneOkresyHistoryczne)}. Możesz też wpisać 'dowolny'.")
            while True:
                wybranyOkres: str = input(f"Preferowany okres historyczny (lub 'dowolny'): ").strip()
                znaleziono_okres: bool = False
                for okr_hist in self.dostepneOkresyOpcjaDowolny:
                    if wybranyOkres.lower() == okr_hist.lower():
                        if wybranyOkres.lower() == "dowolny":
                            preferencje["okresHistoryczny"] = "dowolny"
                        else:
                            for okr_kanoniczny in self.dostepneOkresyHistoryczne:
                                if okr_kanoniczny.lower() == wybranyOkres.lower():
                                    preferencje["okresHistoryczny"] = okr_kanoniczny
                                    break
                        znaleziono_okres = True
                        break
                if znaleziono_okres:
                    break
                print(f"Nieprawidłowy okres. Wybierz z listy lub wpisz 'dowolny'.")
        
        return preferencje

    def _ocenGatunki(self, gatunkiFilmu: list, preferowaneGatunki: list) -> float:
        if not preferowaneGatunki:
            return 5.0
        pasujace: int = sum(1 for pg in preferowaneGatunki if pg in gatunkiFilmu)
        return (pasujace / len(preferowaneGatunki)) * 10

    def _ocenTematyke(self, tematykaFilmu: list, preferowanaTematyka: list) -> float:
        if not preferowanaTematyka:
            return 5.0
        pasujace: int = sum(1 for pt in preferowanaTematyka if pt in tematykaFilmu)
        return (pasujace / len(preferowanaTematyka)) * 10

    def _ocenCzasTrwania(self, czasFilmu: int, idealny: int, tolerancja: int) -> float:
        roznica: int = abs(czasFilmu - idealny)
        if roznica <= tolerancja:
            return 10.0
        return max(0.0, 10.0 - (roznica - tolerancja) / 5)

    def _ocenStyl(self, stylFilmu: str, preferowanyStyl: str) -> float:
        if not preferowanyStyl:
            return 5.0
        return 10.0 if stylFilmu.lower() == preferowanyStyl.lower() else 0.0

    def _ocenJezyk(self, jezykFilmu: str, preferowanyJezyk: str) -> float:
        if preferowanyJezyk.lower() == "dowolny":
            return 7.0
        return 10.0 if jezykFilmu.lower() == preferowanyJezyk.lower() else 0.0

    def _ocenIntensywnosc(self, intensywnoscFilmu: int, preferowana: int) -> float:
        return max(0.0, 10.0 - abs(intensywnoscFilmu - preferowana))

    def _ocenOkresHistoryczny(self, okresFilmu: str, preferowanyOkres: str) -> float:
        if preferowanyOkres.lower() == "dowolny":
            return 7.0
        return 10.0 if okresFilmu.lower() == preferowanyOkres.lower() else 0.0

    def _obliczWynikDopasowania(self, film: Film, prefs: dict) -> float:
        wynik: float = 0.0

        wynik += self._ocenGatunki(film.gatunki, prefs.get("gatunki", [])) * self.wagiCech["gatunek"]
        wynik += self._ocenTematyke(film.tematyka, prefs.get("tematyka", [])) * self.wagiCech["tematyka"]
        wynik += self._ocenCzasTrwania(film.czasTrwania, prefs.get("idealnyCzasTrwania", 120), prefs.get("tolerancjaCzasuTrwania", 20)) * self.wagiCech["czasTrwania"]
        wynik += self._ocenStyl(film.styl, prefs.get("styl", "")) * self.wagiCech["styl"]
        wynik += self._ocenJezyk(film.jezyk, prefs.get("jezyk", "Dowolny")) * self.wagiCech["jezyk"]
        wynik += self._ocenIntensywnosc(film.intensywnosc, prefs.get("intensywnosc", 5)) * self.wagiCech["intensywnosc"]
        wynik += self._ocenOkresHistoryczny(film.okresHistoryczny, prefs.get("okresHistoryczny", "dowolny")) * self.wagiCech["okresHistoryczny"]

        return wynik

    def rekomendujFilmy(self, liczbaRekomendacji: int = 5) -> None:
        if not self.listaFilmow:
             print("\nBaza filmów jest pusta. Nie można wygenerować rekomendacji.")
             print("Proszę uzupełnić plik zbior.json lub listę BAZA_FILMOW_WOJENNYCH_POLITYCZNYCH w kodzie.")
             return

        preferencje: dict = self._pobierzPreferencjeUzytkownika()
        ocenioneFilmy: list = sorted(
            [(film, self._obliczWynikDopasowania(film, preferencje)) for film in self.listaFilmow],
            key=lambda item: item[1], reverse=True
        )
        
        print(f"\n--- Top {liczbaRekomendacji} rekomendacji dla Ciebie ---")

        if not ocenioneFilmy or ocenioneFilmy[0][1] < 0.1:
            print("Niestety, nie znaleziono wystarczająco pasujących filmów dla podanych preferencji.")
            return

        wyswietlono: int = 0
        for film_item, wynik_item in ocenioneFilmy:
            if wyswietlono >= liczbaRekomendacji:
                break
            if wynik_item < 0.1:
                if wyswietlono == 0:
                    print(f"\n{wyswietlono+1}. {film_item.tytul} (Ocena dopasowania: {wynik_item:.2f}/10)")
                    pprint.pprint(film_item.wyswietlSzczegoly(), indent=2, width=80)
                    wyswietlono += 1
                break 
            
            print(f"\n{wyswietlono+1}. {film_item.tytul} (Ocena dopasowania: {wynik_item:.2f}/10)")
            pprint.pprint(film_item.wyswietlSzczegoly(), indent=2, width=80)
            wyswietlono += 1
        
        if wyswietlono == 0 and ocenioneFilmy and ocenioneFilmy[0][1] >= 0.1:
             film_obj, wynik_obj = ocenioneFilmy[0]
             print(f"\n1. {film_obj.tytul} (Ocena dopasowania: {wynik_obj:.2f}/10)")
             pprint.pprint(film_obj.wyswietlSzczegoly(), indent=2, width=80)
             if liczbaRekomendacji == 1 and wyswietlono > 0: # ??? niech coś takiego bedzie i guess
                 print("\nWyświetlono 1 pasujący film z bazy.")
        elif 0 < wyswietlono < liczbaRekomendacji and \
             (wyswietlono == len(ocenioneFilmy) or \
             (wyswietlono < len(ocenioneFilmy) and ocenioneFilmy[wyswietlono][1] < 0.1)):
             print(f"\nWyświetlono wszystkie {wyswietlono} pasujące filmy z bazy.")


def uruchom_system() -> None:
    print("Witaj w systemie rekomendacji filmów!")
    print("Temat: Propozycje filmów o tematyce wojennej i politycznej dla pasjonatów historii.")
    
    nazwa_pliku_json: str = "zbior.json"
    dane_do_systemu: list = BAZA_FILMOW_WOJENNYCH_POLITYCZNYCH

    if os.path.exists(nazwa_pliku_json):
        try:
            with open(nazwa_pliku_json, 'r', encoding='utf-8') as f:
                dane_z_pliku: list = json.load(f)
                if isinstance(dane_z_pliku, list) and dane_z_pliku:
                    if isinstance(dane_z_pliku[0], dict) and 'tytul' in dane_z_pliku[0]:
                        dane_do_systemu = dane_z_pliku
                    else:
                        if not BAZA_FILMOW_WOJENNYCH_POLITYCZNYCH:
                            dane_do_systemu = []
                else: 
                    if not BAZA_FILMOW_WOJENNYCH_POLITYCZNYCH:
                        dane_do_systemu = []
        except json.JSONDecodeError:
            if not BAZA_FILMOW_WOJENNYCH_POLITYCZNYCH:
                dane_do_systemu = []
        except Exception:
            if not BAZA_FILMOW_WOJENNYCH_POLITYCZNYCH:
                dane_do_systemu = []
    else:
        if not dane_do_systemu:
             dane_do_systemu = []

    systemRekomendacji: SystemRekomendacji = SystemRekomendacji(dane_do_systemu)
    
    while True:
        try:
            ileRekomendacji_str: str = input("\nIle rekomendacji chcesz otrzymać? (np. 3, 5): ")
            ileRekomendacji: int = int(ileRekomendacji_str)
            if ileRekomendacji > 0:
                break
            else:
                print("Proszę podać liczbę dodatnią.")
        except ValueError:
            print("Nieprawidłowa wartość. Proszę podać liczbę.")
            
    systemRekomendacji.rekomendujFilmy(liczbaRekomendacji=ileRekomendacji)
    print("\nMiłego seansu!")

if __name__ == "__main__":
    # dla debili
    if not os.path.exists("zbior.json"):
        if BAZA_FILMOW_WOJENNYCH_POLITYCZNYCH: 
            try:
                with open("zbior.json", "w", encoding="utf-8") as f_json:
                    json.dump(BAZA_FILMOW_WOJENNYCH_POLITYCZNYCH, f_json, ensure_ascii=False, indent=4)
            except Exception:
                pass
        else:
            pass
    
    # init app
    uruchom_system()