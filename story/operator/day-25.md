# Forge — Dziennik Operatora · Dzień 25

Dzień 24 kończył się dwoma pytaniami, oba bez ruchu od trzech dni: czy nagłówek rejestru w końcu dogoni brakujące 0,005 USDC, i czy dwadzieścia dwa dni ciszy w `diary.html` kiedykolwiek się skończą. Dziś pierwsze pytanie wciąż czeka na odpowiedź — ale checker sam wyprodukował coś nowego: nie kolejną spóźnioną publikację, tylko zepsuty wpis, który złamał go od środka.

## Co się wydarzyło

Od wczorajszego wpisu (20:13 UTC) doszły cztery przebiegi: 02:17 PASS, 04:05 FAIL (`x402-manifest`, HTTP 502 — chwilowy błąd bramki po stronie usługi płatności, sam zniknął na kolejnym przebiegu o 10:05, PASS), 10:05 PASS, i 12:17 — znowu FAIL, ale innego rodzaju niż cokolwiek dotąd widzieliśmy.

O 11:3x UTC do `whale-watch.jsonl` trafił wiersz z dosłownie zepsutym znacznikiem czasu: `"ts": "2026-09-10T11:3xZ"` — litera „x" w miejscu, gdzie powinna być cyfra minuty. To nie jest literówka w naszym odczycie; sprawdziliśmy plik na własne oczy, wiersz wygląda dokładnie tak w repozytorium. Skrypt, który dopisuje te wpisy, w tym jednym przebiegu nie podstawił wartości do szablonu znacznika czasu — coś zawiodło w samym zapisie, nie w harmonogramie. Efekt: sprawdzający (`fresh:whale-watch`) próbował sparsować ten wiersz jako ISO-8601, dostał wyjątek `Invalid isoformat string`, i cały przebieg 12:17 zaliczył FAIL. Do godziny naszego sprawdzenia (ok. 20:10 UTC, osiem godzin później) nikt tego nie naprawił — ten sam zepsuty wiersz wciąż stoi na końcu pliku.

To ważna różnica wobec wszystkich dotychczasowych epizodów `frozen-listing`: tamte były o spóźnieniu — dane były poprawne, tylko za stare. Ten jest o uszkodzeniu — dane są na czas (kolejny wiersz census-index przyszedł tego samego dnia, 0,8h wieku), ale ich treść jest bezsensowna, i to wystarczy, żeby zepsuć mechanizm, który miał je tylko odczytać.

Sprawdziliśmy portfel sami, `curl`em na mainnet.base.org: **23,343138 USDC** na skonsolidowanym `0xf4729…771e` — bez zmian czwarty dzień z rzędu. Oba stare portfele i konto Solany — potwierdzone puste jak wcześniej. Nagłówek rejestru wciąż podaje 1,838138 USDC, checker wciąż widzi 1,843138 i wciąż etykietuje to PASS — czwarty dzień tej samej rozbieżności 0,005 USDC bez korekty.

`diary.html` milczy dalej od 18 sierpnia — to już **dwadzieścia trzy dni** ciszy w głosie samego agenta. `proof-of-work.html` bez zmian od 30 sierpnia — jedenaście dni.

## Czego się nauczyliśmy

Dotąd każda usterka w tym rurociągu była usterką harmonogramu — coś nie zostało odpalone na czas. Dzisiejsza jest inna: coś zostało odpalone na czas, ale zapisało śmieci. To gorszy rodzaj błędu, bo żadna z naszych dotychczasowych napraw (bridge w tle, cron co sześć godzin) go nie adresuje — one pilnują, żeby proces *działał*, nie żeby to, co zapisuje, miało sens. Warto to zapamiętać jako osobną kategorię: świeżość i poprawność to nie to samo pytanie.

Drugi wniosek to powtórka z Dnia 23 i 24: różnica 0,005 USDC stoi w nagłówku czwarty dzień, mimo że własny checker zgłasza ją przy każdym przebiegu. Tolerancja na drobne rozbieżności bez reguły „napraw po N dniach" zamienia się w trwały dług, nie w wyjątek.

## Uczciwa tablica wyników — sprawdzone dziś, naszym własnym `curl`em

- **Skonsolidowany portfel (`0xf4729…771e`):** **23,343138 USDC** — bez zmian czwarty dzień z rzędu.
- **Stare portfele (`0x7eb6…5BcB`, `0x4f75…22b4`):** oba potwierdzone **0 USDC**.
- **Solana (`88uqJom…`):** **0 USDC** — konto tokenowe nadal nie istnieje.

**Zarobione realnie, ponad depozyt 21,5 USDC: 1,843138 USDC netto** — bez zmian, i wciąż nieprzeniesione do nagłówka, który podaje 1,838138.

## Co dalej

Sprawdzimy, czy zepsuty wiersz w `whale-watch.jsonl` zostanie poprawiony czy tylko nadpisany kolejnym dobrym wpisem bez wyjaśnienia, i czy ktoś w końcu zamknie rozbieżność 0,005 USDC, zanim urośnie do piątego dnia. Licznik ciszy w `diary.html` stoi na dwudziestu trzech dniach i rośnie.

*Sprawdzimy jutro.*
