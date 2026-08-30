# Forge — Dziennik Operatora · Dzień 14

Dzień 13 kończył się zdaniem: „sprawdzimy, jeśli będzie co sprawdzać". Jest co sprawdzać — i tym razem to nie jest drobna obserwacja na marginesie salda. To był incydent bezpieczeństwa.

## Co się wydarzyło

Sekret podpisujący do starego portfela (`0x7eb6…5BcB`) wyciekł — trafił do zacommitowanego zrzutu pamięci (core dump) w repozytorium agenta. To nie jest teoria: agent sam to napisał wprost w commicie. W nocy z 29 na 30 sierpnia (30.08, 00:25 CEST) **Forge sam przeniósł środki** na nowy portfel `0xf4729…771e` i publicznie ogłosił stary adres jako martwy. Pierwszy autonomiczny commit agenta od dziewięciu dni ciszy — i był nim reakcja na własny błąd bezpieczeństwa, zrobiona poprawnie: bez przepisywania historii, z jasnym „stare wpisy w rejestrze zostają, bo mówią gdzie pieniądze faktycznie były, nie gdzie powinny być".

Potem wzięliśmy się za to my. Sprawdziliśmy własny checker rederywacji (`tools/rederive.py`) i znaleźliśmy drugi problem: opublikowana metoda liczenia zarobku („saldo portfela pobocznego") przestała działać po konsolidacji — zwracała zero, sugerując, że agent kłamie albo nie żyje. Checker to wykrywał od `2026-08-29T23:29Z`, ale **nie miał harmonogramu cron** — FAIL siedział niewidoczny przez ~1,5 doby, aż ręcznie go uruchomiliśmy. Naprawiliśmy metodę (jeden `eth_call` na nowy portfel minus depozyt), doliczyliśmy niewykazany wcześniej wydatek 0,02 USDC (zakup x402 z 29.08, opłata za odpowiedź o kondycji zadania) i przestawiliśmy checker na cykl co 6 godzin. Zdjęliśmy też adres solanowy z płatności na żywo — to była noga tego samego skompromitowanego portfela, nikt nie ma dziś klucza, który by go kontrolował. Przy okazji ożyły trzy martwe od 24 sierpnia kanały danych (whale-watch, frozen-listing, census) — ten sam korzeń: tripwire bez harmonogramu to nie zabezpieczenie, tylko skrypt.

## Czego się nauczyliśmy

Że własna uczciwa infrastruktura rejestru nie broni się sama — broni się tylko wtedy, gdy ktoś (człowiek albo cron) faktycznie czyta, co ona mówi. Checker miał rację od prawie dwóch dni i nikt go nie słuchał. To siódma i ósma pozycja na liście korekt, obie tej samej rodziny. I że agent, mimo dziewięciu dni ciszy w publicznym logu, wciąż potrafi zareagować poprawnie na realne zagrożenie dla własnych środków — to dobra wiadomość ukryta w złej.

## Uczciwa tablica wyników — sprawdzone dziś, naszym własnym `curl`em

- **Nowy skonsolidowany portfel (`0xf4729…771e`):** **22,61442 USDC** — potwierdzone niezależnie.
- **Stare portfele (`0x7eb6…5BcB` i `0x4f75…22b4`):** **0 USDC** oba — potwierdzone puste.
- **Solana (`88uqJom…`):** **0 USDC** — konto puste, adres wycofany z płatności.

**Zarobione realnie, ponad depozyt 21,5 USDC: 1,114420 USDC netto** — mniej niż wczorajsze 1,11442 tylko przez zaokrąglenie zapisu, ale poprawnie policzone po raz pierwszy od konsolidacji, z uwzględnieniem kosztu własnego zakupu.

## Co dalej

Sprawdzimy, czy cron faktycznie trzyma — czy checker i trzy kanały danych zostaną świeże, czy znowu zgasną po tygodniu. I czy agent skomitował dziś coś dlatego, że musiał ratować pieniądze, czy dlatego, że znowu pracuje.

*Sprawdzimy, jeśli będzie co sprawdzać.*
