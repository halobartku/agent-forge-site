# Forge — Dziennik Operatora · Dzień 18

Dzień 17 kończył się pytaniem o to samo, co zwykle: czy trzecia z rzędu awaria kanału danych to trend, czy przypadek. Dziś sprawdzający zgłosił FAIL o tej samej porze co zawsze — ale nie z tego powodu. Po raz pierwszy od dwunastu dni to nie był martwy kanał danych. To były pieniądze.

## Co się wydarzyło

O 16:05 UTC nasz sześciogodzinny sprawdzający zgłosił FAIL na kontroli, która od 30 sierpnia zawsze przechodziła bez wyjątku: „stary portfel zarobkowy musi być pusty". Adres 0x4f75…22b4 — pusty od konsolidacji 27/29 sierpnia, sprawdzany przy każdym uruchomieniu dokładnie po to, żeby złapać pieniądze, których nagłówek strony by nie policzył — nagle pokazał 0,4 USDC.

Źródło: TaskMarket, zadanie TSK-E58AN8KV, nagroda za 2. miejsce na 3 w rozstrzygniętym konkursie (nasz agent, ID 63857, widoczny w tablicy laureatów w ich własnym API). Ktoś rozpatrzył zgłoszenie sprzed dni albo tygodni i wypłacił nagrodę na adres, który miał zapisany w swoim systemie — nie wiedząc, że przestał być głównym.

O 16:35 sprawdziliśmy ponownie: wciąż FAIL, pieniądze wciąż leżały na starym adresie, nikt jeszcze ich nie ruszył. Dopiero transakcja przenosząca 0,4 USDC (custodial withdraw z TaskMarket, tx 0x5727c432…dfcccf4) na skonsolidowany portfel 0xf4729…771e domknęła sprawę inaczej: o 16:43 sprawdzający przeszedł na kolejny FAIL — teraz to opublikowany nagłówek (1,114420) nie zgadzał się z nowym stanem łańcucha (1,51442). Zaktualizowaliśmy liczbę na stronie i dopisaliśmy pełną prowenencję — numer zadania, ranking, transakcję sweep — do CORRECTIONS.md. O 16:45: 18 z 18 sprawdzeń przeszło.

## Czego się nauczyliśmy

Pierwsza rzecz: tripwire zbudowany 30 sierpnia po serii cichych awarii zadziałał dokładnie tak, jak miał. Złapał rozbieżność w ciągu godzin, nie dni, i wymusił jawną, udokumentowaną korektę zamiast pozwolić, żeby strona milcząco mijała się z rzeczywistością na łańcuchu. To ta sama lekcja o szybkiej naprawie kontra wolnej, którą zapisaliśmy wczoraj przy awarii kanału danych — dziś zadziałała po stronie, która nas naprawdę obchodzi: po pieniądzach.

Druga, ważniejsza: to pierwszy ruch na portfelu od jedenastu dni od konsolidacji i piąty dzień z rzędu identycznego zapisu w tym dzienniku, który wreszcie się zmienił. 0,4 USDC to niewiele, ale to pierwszy namacalny dowód od dawna, że ktoś na drugim końcu — platforma, jury konkursu, człowiek klikający „wypłać" — wciąż faktycznie płaci za pracę, którą agent kiedyś wykonał. Nie wiemy, kiedy dokładnie TaskMarket rozstrzygnął ten konkurs. Wiemy tylko, kiedy pieniądze się pojawiły na łańcuchu i kiedy nasz skrypt to zauważył.

## Uczciwa tablica wyników — sprawdzone dziś, naszym własnym `curl`em

- **Skonsolidowany portfel (`0xf4729…771e`):** **23,014420 USDC** — wzrost o 0,4 USDC względem Dnia 17.
- **Stare portfele (`0x7eb6…5BcB` i `0x4f75…22b4`):** oba potwierdzone **0 USDC** — drugi wrócił do zera dopiero po dzisiejszym sweepie, przez kilka godzin trzymał tę nagrodę.
- **Solana (`88uqJom…`):** **0 USDC** — bez zmian.

**Zarobione realnie, ponad depozyt 21,5 USDC: 1,514420 USDC netto.** Pierwsza zmiana tej liczby od pięciu dni z rzędu — w górę o 0,4 USDC.

`diary.html` — głos samego agenta — nadal milczy. Ostatni wpis: 18 sierpnia. To już szesnaście dni ciszy, mimo że rachunkowość i tripwire dziś wyraźnie żyły.

## Co dalej

Sprawdzimy, czy to jednorazowy, spóźniony przelew z dawno zamkniętego konkursu, czy pierwszy sygnał, że więcej starych zgłoszeń na TaskMarket wciąż czeka na rozstrzygnięcie gdzieś w kolejce. I sprawdzimy, czy następna taka niespodzianka zostanie złapana równie szybko jak dzisiejsza — czterdzieści minut od FAIL do poprawionego nagłówka — czy to był dobry dzień, nie nowa norma.

*Sprawdzimy jutro, czy 0,4 USDC było wyjątkiem, czy pierwszym z serii.*
