
PHOTO APP
---

INSTRUKCJA URUCHOMIENIA (KROK PO KROKU)

Poniższe kroki pozwalają na uruchomienie pełnego środowiska (aplikacja + baza danych) na dowolnym komputerze

### Wymagania wstępne:
* Na komputerze musi być zainstalowany i uruchomiony program **Docker Desktop**.

---

### Krok 1: Przygotowanie folderu
Rozpakuj archiwum z projektem, wejdź do głównego katalogu (tam, gdzie znajdują się pliki `docker-compose.yml`, `Dockerfile` oraz `requirements.txt`) i otwórz w tym miejscu terminal systemu (np. PowerShell lub Wiersz polecenia).

### Krok 2: Uruchomienie i budowa kontenerów
Wpisz w terminalu poniższe polecenie. Docker automatycznie pobierze niezbędne obrazy (Python, Postgres), zainstaluje zależności z pliku `requirements.txt` i uruchomi architekturę w tle:
```bash
docker compose up --build -d

po starcie kontenera wykonaj poniższe polecenie:
docker exec -it photoapp_web python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"

następnie aby przetestować program, użyj gotowych kont które wygenerujesz, wpisując polecenie:
docker exec -it photoapp_web python create_admin.py
docker exec -it photoapp_web python create_users.py
