# polish_ekstraklasa
This program extracts HTML element - table with all current results of matches in Polish Ekstraklasa (football league) as a string.
After extracting this string, the program gathers only necessary data: clubs names and all matches results thanks to RegEx.
When all of them are gathered, final table of Ekstraklasa is being prepered.
In order to do that, 6 rules from this webpage (https://en.wikipedia.org/wiki/2021%E2%80%9322_Ekstraklasa) are followed.
As a final step, two Excel file are created - one with matrix of all match results and another one with final table of Ekstraklasa.
Also chart with points achieved by given teams is created and shown.
