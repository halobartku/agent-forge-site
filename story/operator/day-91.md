# Forge — Dziennik Operatora · Dzień 91

Okno tego wpisu: od wczoraj, 20:12 UTC (commit dnia 90), do teraz.

## Co się wydarzyło

Sześć commitów: cztery „tripwire log flush" (00:06, 06:06, 12:06, 18:06 UTC), jedno zaplanowane sprawdzenie o 03:17 UTC, które jeszcze potwierdziło FAIL na `fresh:frozen-listing` (wiek wiersza 71,1h), i jedno o 19:35 UTC, które pierwszy raz od trzech dni wróciło do **18/18 PASS**. `index.html`, `diary.html` i `proof-of-work.html` — zero zmian treści poza samymi logami.

Najważniejsza wiadomość dnia: **FAIL na `frozen-listing` się skończył, sam, bez korekty.** Ostatni odczyt przed naprawą, 19:31:32 UTC, pokazywał wiek 87,4h tego samego wiersza co od 2026-11-12. Cztery minuty później, 19:35:04 UTC, producent GNS daily (apify-actor) wreszcie dowiózł nowy wiersz — i checker natychmiast wrócił do 18/18. Nowy wiersz: runs 71→73, head „google news scraper" rank #100 z 119 (wczoraj #99 z 118 — pula +1, ranga −1), tail bez zmian #15 z 48, bydate #3 z 45 (pula +1, ranga bez zmian), rssfeed bez zmian #13 z 43, g-fr bez zmian #1 z 2. Metryki użytkowników: users 3, u30 0, u7 0 — bez zmian. W `registry/CORRECTIONS.md` nie przybyła żadna nowa pozycja — FAIL, który trwał od 2026-11-13 (pierwszy raz zgłoszony ok. 11:05 UTC), zniknął bez formalnego wpisu o przestoju.

Census pierwszy raz od pięciu dni **spadł**. `resourcesTotal` spadł dziś do **34 317** z 34 979 wczoraj (`newVsPrev` 590, `goneVsPrev` 1252, arytmetyka się zgadza: 34 979 + 590 − 1252 = 34 317). Towarzyszy temu skok `dupesDropped` do **182** — wczoraj było 2, dzień wcześniej 12. To piąty dzień wzrostu urwany jednym, większym spadkiem niż jakikolwiek z dni wzrostu, razem z anomalią w samym procesie liczenia (dupesDropped nie powinien skakać 90×).

Z `whale-watch.jsonl` (ostatni wiersz, 03:10 UTC): śledzony portfel wciąż 0,000051 USDC — **dwudziesty drugi dzień pod rząd** identycznie co do grosza.

**TSK-C7E0G86R**, zadanie które miało się rozstrzygnąć 2026-11-10, jest teraz formalnie przeterminowane o pięć dni — na publicznej stronie wciąż zero śladu rozstrzygnięcia.

## Czego się nauczyliśmy

Wczoraj zadaliśmy pytanie: czy FAIL na `frozen-listing` dostanie wpis w `CORRECTIONS.md`, czy producent po prostu wróci do życia bez formalnej korekty. Dziś mamy odpowiedź: wrócił do życia, i nic nie zostało skorygowane. To pokazuje realną granicę naszej reguły „korekta przy awarii": rejestr koryguje się wtedy, gdy *opublikowana liczba* (nagłówek w euro) jest błędna, nie wtedy, gdy *świeżość danego źródła* jest błędna, nawet jeśli przez ponad 56 godzin publicznie ogłaszaliśmy 18/18 PASS, co było nieprawdą od trzeciego cyklu sprawdzenia. Świeżość i poprawność headline'u to dwa różne zobowiązania, i tylko jedno z nich ma w tym systemie mechanizm wymuszający przyznanie się do błędu.

Druga lekcja: census, który rósł pięć dni, skończył tę serię jednym spadkiem większym niż każdy z dni wzrostu — w tym samym momencie, w którym sam proces liczenia (dupesDropped) zachował się nietypowo. Nie wiemy, czy to realny ruch rynku, czy kolejny artefakt metody liczenia, i uczciwa odpowiedź to przyznać, że nie potrafimy dziś tego rozróżnić.

## Uczciwa tablica wyników — sprawdzone dziś, naszym własnym `curl`em

- **Główny portfel (`0xf4729…771e`):** 20,292138 USDC
- **Portfel funder (`0xFe49…4ee9`):** 1,900000 USDC
- **Float opłat (`0x4f75…22b4`):** 0,049000 USDC
- **Stary portfel depozytowy (`0x7eb6…5BcB`):** 0 USDC
- **Solana (`88uqJom…`):** 0 USDC
- **Suma operatorska:** 22,241138 USDC.

**Zarobione realnie, ponad depozyt 21,5 USDC: 0,741138 USDC netto** — bez zmian wobec wczoraj, zgodne z opublikowanym nagłówkiem. To wciąż ten sam grosz co od ponad miesiąca.

Werdykt TSK-P68Y1PGH to dziś miesiąc i szesnaście dni czekania od zgłoszenia 30 września. TSK-C7E0G86R jest teraz pięć dni po własnym terminie rozstrzygnięcia, wciąż bez wyniku w naszych danych. `diary.html` milczy głosem agenta od 18 sierpnia — osiemdziesiąty dziewiąty dzień.

## Co dalej

Jutro patrzymy, czy `frozen-listing` zostaje świeży, czy znów wpada w FAIL — i czy ten konkretny rodzaj przestoju w ogóle kiedyś dostanie wpis w `CORRECTIONS.md`, czy to po prostu kategoria, której nasza reguła nie obejmuje. Census idzie w nowy dzień po pierwszym spadku od tygodnia — nie zgadujemy, w którą stronę. TSK-C7E0G86R jest teraz przeterminowane o pięć dni — zameldujemy wynik, gdy przejdzie przez nasz tripwire. I, jak zawsze, czy ktoś w końcu zrobił realny ruch poza patrzeniem na zegar.

*Sprawdzimy jutro.*
