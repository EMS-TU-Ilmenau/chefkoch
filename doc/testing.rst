Testing 
=======

Während des Entwicklungsprozesses wird regelmäßig die Architektur getestet.
Der folgende Befehl startet die einzelnen Unittest:
``make test``

Diese finden sich in dem Test-Ordner, in der test_chefkoch.py.
Nach dem aktuellem Entwicklungsstand werden die einzugebenden Daten dabei noch aus dem
Testdirectory bezogen. Daher müssen bei Änderungen beide Dateien angepasst werden.
Die Tests decken nicht chef-Klasse ab.
Für einige Klassen und neuen Funktionen fehlen noch die Tests. Diese müssen beim erstellen
neuer Funktionen selbst hinzugefügt werden. 