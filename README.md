# Tauron
Sterowanie pompą ciepła z uwzględnieniem taryfy dynamicznej

Elementy
  - Zczytanie ceny dnia następnego (web scapping)
  - Wyliczenie optymalnych przedziałów pracy pompy w uwzględnieniem:
    - prognozy pogody (temperatury) na zadaną lokalizację
      - => wyliczenie sumarycznego czasu pracy pompy
      - => uwzględnienie minimalnego czasu pracy pompy (np. pompa musi pracować minimum 2 godziny bez wyłączania)
  - Włączanie i wyłączanie pompy Sprsun poprzez Modbus
  - Aplikacja sterująca pracuje na RPi, główny język to Python
  - Prawdopodna integracja z Domoticz/Home Assistant
- Operowanie pompą przez ModBus nie powinno wyłączać możliwości sterowania jej przez aplikację
  - program typu TCP proxy, 2 wejścia TCP - EW11A, port dla aplikacji sterującej, 1 wyjście TCP do m2m.sprsun.com
