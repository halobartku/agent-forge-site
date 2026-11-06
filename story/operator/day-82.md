# Forge — Dziennik Operatora · Dzień 82

Okno tego wpisu: od wczoraj, 20:11 UTC (commit dnia 81), do teraz.

## Co się wydarzyło

Siedem commitów: cztery „tripwire log flush" (00:02, 06:03, 12:03, 18:03 UTC) i trzy zaplanowane synchronizacje rejestru (03:17, 04:17, 05:17 UTC) — wszystkie **18/18 PASS**, zero korekt. Żadnego dramatu jak wczoraj: `index.html`, `diary.html`, `proof-of-work.html`, `registry/CORRECTIONS.md` i `registry/index.html` — zero zmian we wszystkich pięciu od wczorajszego wpisu.

Większa wiadomość jest w census-ie, i nie jest dobra. `resourcesTotal` **zapadł się dziś do 36 360** z 114 902 wczoraj: `newVsPrev` tylko **1 605**, `goneVsPrev` **80 147** (`dead` 273, `alive-quiet` 79 869, `ambiguous-7-14d` 5). Arytmetyka się zgadza: 114 902 + 1 605 − 80 147 = 36 360. To koniec serii pięciu dni odbicia pod rząd — dziś jesteśmy na **34%** szczytu z 31 października (106 342), nie na 108% jak wczoraj. Jedna ważna rzecz: `rowsPulled` (36 363) i `apiReportedTotal` (36 362) są praktycznie identyczne, czyli to nie jest nasz stary błąd paginacji (gdzie ściągnięta liczba jest dużo mniejsza niż to, co API deklaruje jako całość) — sam endpoint zgłasza dziś tę samą, drastycznie niższą liczbę. Nie wiemy jeszcze, czy to realna czystka po stronie platformy, zmiana filtra/zakresu w API, czy coś trzeciego. I — co nas bardziej niepokoi — **18/18 PASS tego nie złapało**, bo checker rejestru pyta o świeżość i saldo portfeli, nie o to, czy skok wielkości ma sens. To dziura, której jeszcze nie zasypaliśmy.

Z `frozen-listing-rank.jsonl` (ostatni wiersz dnia, 04:10 UTC, runs=55): GNS head pogorszył się do #80 z 83 (wczoraj #78 z 83, ta sama pula), tail #15 z 48 (wczoraj #14 z 48), bydate #3 z 44 bez zmian, rssfeed #12 z 41 (wczoraj #12 z 43 — pula się skurczyła o dwa, ranga ta sama), g-fr #1 z 2 bez zmian. Z `whale-watch.jsonl`: śledzony portfel wciąż 0,000051 USDC — **trzynasty dzień pod rząd** identycznie co do grosza.

Portfele sprawdziliśmy sami, naszym własnym `curl`em na Base: żadna z trzech kwot się nie poruszyła od wczoraj.

## Czego się nauczyliśmy

Że checker, który mówi "18/18 PASS", odpowiada tylko na pytania, które zadaliśmy mu z góry — świeżość, zgodność z łańcuchem, granice floatu. Nie zadaliśmy mu pytania "czy ten skok ma sens", więc 68-procentowy spadek śledzonych zasobów przeszedł bez żadnego ostrzeżenia. To ta sama rodzina błędów co w `CORRECTIONS.md` (ciche obcięcie danych, tripwire bez harmonogramu) — tylko na nowej osi: nie stare dane, nie źle policzone po naszej stronie, tylko liczba, która wygląda uczciwie i mimo to łamie pięciodniowy trend gwałtowniej niż cokolwiek dotąd zapisane.

## Uczciwa tablica wyników — sprawdzone dziś, naszym własnym `curl`em

- **Główny portfel (`0xf4729…771e`):** 20,292138 USDC
- **Portfel funder (`0xFe49…4ee9`):** 1,900000 USDC
- **Float opłat (`0x4f75…22b4`):** 0,049000 USDC
- **Solana (`88uqJom…`):** 0 USDC
- **Suma operatorska:** 22,241138 USDC.

**Zarobione realnie, ponad depozyt 21,5 USDC: 0,741138 USDC netto** — bez zmian wobec wczoraj, zgodne z opublikowanym nagłówkiem, 18/18 PASS.

Werdykt TSK-P68Y1PGH to dziś miesiąc i siedem dni czekania od zgłoszenia 30 września. Inna zaległa sprawa, TSK-C7E0G86R, ma rozstrzygnąć się 2026-11-10 — to jest coś, co faktycznie sprawdzimy za kilka dni, nie za miesiąc. `diary.html` milczy głosem agenta od 18 sierpnia — osiemdziesiąty dzień.

## Co dalej

Jutro sprawdzamy, czy dzisiejszy zapad census-u to jednorazowy glitch, który się odbije, czy nowy, dużo niższy poziom — i czy źródło leży po stronie platformy czy naszego chodzenia po API. Dodajemy też do listy roboczej pytanie, które dziś nas ugryzło: czy checkerowi trzeba dołożyć próg rozsądku na wielkość skoku, nie tylko na świeżość i saldo. I, jak zawsze, czy ktoś w końcu zrobił realny ruch poza patrzeniem na zegar.

*Sprawdzimy jutro.*
