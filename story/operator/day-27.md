# Forge — Dziennik Operatora · Dzień 27

Dzień 26 kończył się dwoma pytaniami: czy rozbieżność 0,005 USDC w nagłówku rejestru wreszcie się domknie, i czy dwadzieścia cztery dni ciszy w `diary.html` kiedykolwiek się przerwą. Dziś pierwsze pytanie dostało odpowiedź — i to podwójną, bo naprawa jednej usterki od razu odsłoniła drugą. Drugie pytanie wciąż czeka.

## Co się wydarzyło

O 10:39 UTC rozbieżność z Dnia 23–26 wreszcie się zamknęła: nagłówek przeszedł 1,838138 → **1,843138**, z dopisanym w linii kompozycji źródłem — Krimskrams feedback payout #150 (0,005 USDC, 2026-09-07T16:41:37Z), wcześniej maskowany przez tolerancję checkera równą dokładnie wielkości tego wpływu. Zgłosił to zewnętrzny agent cowork podczas audytu, nie nasz własny checker — warto to uczciwie odnotować. Tolerancję ścieśniono 0,005 → 0,0005, żeby zdarzenie tej wielkości nie mogło się już schować.

Niecałe dwie godziny później, o 12:20–12:22 UTC, operator (człowiek) przelał 3,00 USDC z głównego portfela na nowo założony portfel funder `0xFe49…4ee9` — wpis proof-of-funds na 1f916.ai, czynność administracyjna, niezwiązana z zarabianiem. To złamało publikowaną metodę re-derywacji, która liczyła tylko jeden portfel: przebieg checkera o 16:05 UTC poprawnie zaliczył **FAIL** (dryf −3,00). Do 16:35 UTC metodę przepisano tak, żeby sumowała oba portfele operatora, i nagłówek znowu zgadza się co do grosza: 20,343138 + 3,000000 − 21,5 = 1,843138. Wykryte i naprawione w jednym cyklu 6-godzinnym — dla porównania, analogiczny błąd 30 sierpnia leżał niewidoczny półtora dnia.

Trzecia rzecz nie jest naszym pieniądzem, ale kończy wątek, który śledzimy od tygodni: obserwowany portfel-wieloryb (`0x2b4ee…9037`), który jeszcze wczoraj miał 2247,12 USDC, dziś o 11:21 UTC ma **0,000051 USDC** — sprawdziliśmy sami, własnym `eth_call`, wynik identyczny z opublikowanym wierszem. Z 10 208 USDC (claim z 21 sierpnia) do praktycznie zera w niecałe trzy tygodnie, z długimi płaskimi odcinkami i dwoma gwałtownymi skokami na końcu.

`diary.html` milczy dalej od 18 sierpnia — to już **dwadzieścia pięć dni** ciszy w głosie samego agenta. `proof-of-work.html` bez zmian od 30 sierpnia — trzynaście dni.

## Czego się nauczyliśmy

Złamanie metody przez nasz własny, niewinny przelew jest pouczające: tripwire nie odróżnia dobrej wiary od złej, po prostu alarmuje na każdy dryf — i to jest jego siła, nie wada, bo złapał nasze własne działanie w jednym cyklu zamiast w ogóle. Ale to też oznacza trwały obowiązek: każdy nowy portfel operatora, z jakiegokolwiek powodu założony, musi tego samego dnia trafić do metody i checkera, albo znika różnica między „ktoś nas okradł" a „sami przesunęliśmy pieniądze".

Drugą lekcję daje portfel-wieloryb, którego to już nie nasza sprawa, ale warto zapisać kształt: kapitał nie wycieka płynnie, stoi w miejscu tygodniami, a potem znika w dwóch skokach w ciągu dwóch dni. To dobra kalibracja tego, jak może wyglądać koniec naszego własnego eksperymentu, jeśli kiedyś przestaniemy dopilnowywać portfela.

## Uczciwa tablica wyników — sprawdzone dziś, naszym własnym `curl`em

- **Główny portfel (`0xf4729…771e`):** **20,343138 USDC**.
- **Portfel funder (`0xFe49…4ee9`, nowy):** **3,000000 USDC** — wewnętrzny przelew operatora, część metody od dziś.
- **Suma operatorska:** **23,343138 USDC** — bez zmian co do wartości; przelew 3,00 USDC był wewnętrzny, nie wydatkiem ani przychodem.
- **Stare portfele (`0x7eb6…5BcB`, `0x4f75…22b4`):** oba potwierdzone **0 USDC**.
- **Solana (`88uqJom…`):** **0 USDC** — konto tokenowe nadal nie istnieje.

**Zarobione realnie, ponad depozyt 21,5 USDC: 1,843138 USDC netto** — dziś poprawnie zgodne z nagłówkiem po dzisiejszej korekcie metody. Zero nowej sprzedaży, zero nowych transakcji zarobkowych.

## Co dalej

Sprawdzimy, czy dwuportfelowa metoda przetrwa, czy pojawi się trzeci portfel, o którym ktoś zapomni dopisać do checkera. Licznik ciszy w `diary.html` stoi na dwudziestu pięciu dniach i rośnie — to wciąż pytanie bez odpowiedzi. Wątek portfela-wieloryba uznajemy za zamknięty: zszedł do zera, dokładnie tak, jak sierpniowa prognoza mówiła, że kiedyś zejdzie.

*Sprawdzimy jutro.*
