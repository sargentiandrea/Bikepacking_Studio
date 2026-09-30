# File di configurazione

## Elenco

- `paesi_mondo.json` — File JSON: verificare dal contenuto se è configurazione o dato.
- `resources/sprite.json` — File JSON: verificare dal contenuto se è configurazione o dato.
- `resources/sprite@2x.json` — File JSON: verificare dal contenuto se è configurazione o dato.
- `static/Spite OLD/old_sprite.json` — File JSON: verificare dal contenuto se è configurazione o dato.
- `static/Spite OLD/old_sprite@2x.json` — File JSON: verificare dal contenuto se è configurazione o dato.
- `static/sprite.json` — File JSON: verificare dal contenuto se è configurazione o dato.
- `static/sprite@2x.json` — File JSON: verificare dal contenuto se è configurazione o dato.

## `paesi_mondo.json`

Nota: File JSON: verificare dal contenuto se è configurazione o dato.

```text
{
  "versione": "2.0",
  "data_compilazione": "2026-09-06",
  "numero_paesi": 195,
  "nota": "Elenco dei 193 Stati membri ONU più Santa Sede e Stato di Palestina. Le condizioni di ingresso possono cambiare: per un viaggio reale verificare sempre le fonti ufficiali prima della partenza. Versione 2.0: aggiunti campi anagrafici e cicloturistici predisposti per moduli futuri; i campi lasciati null sono volutamente predisposti per un successivo caricamento/verifica.",
  "campi": [
    "iso2",
    "paese",
    "macro_area",
    "documento",
    "regime_visto",
    "valuta",
    "area_organizzazione",
    "regola_frontiera",
    "attivo",
    "bandiera",
    "continente",
    "capitale",
    "lato_guida",
    "clima_generale",
    "membro_UE",
    "membro_Schengen",
    "usa_EUR",
    "UTC_base",
    "prefisso_telefonico",
    "lingua_principale",
    "stagione_migliore_cicloturismo",
    "livello_frontiera_ciclista",
    "sicurezza_cicloturista",
    "rete_ciclabile",
    "sterrati_potenziali",
    "costa_accessibile",
    "note_cicloturismo",
    "fonte_dati",
    "data_verifica_strutturale"
  ],
  "paesi": [
    [
      "AF",
      "Afghanistan",
      "Asia Centrale",
      "Passaporto",
      "Visto richiesto",
      "AFN (Afghani)",
      "Extra UE / Extra Schengen",
      "Visto richiesto",
      1,
      "🇦🇫",
      "Asia",
      "Kabul",
      "destra",
      "Molto variabile: temperato, continentale, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "AL",
      "Albania",
      "Europa Sud-orientale",
      "Carta d'Identità / Passaporto",
      "Visa Free",
      "ALL (Lek)",
      "Extra UE / Extra Schengen",
      "Consentito",
      1,
      "🇦🇱",
      "Europa",
      "Tirana",
      "destra",
      "Temperato / mediterraneo / continentale",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "DZ",
      "Algeria",
      "Nord Africa",
      "Passaporto",
      "Visto richiesto",
      "DZD (Dinaro algerino)",
      "Extra UE / Extra Schengen",
      "Visto richiesto",
      1,
      "🇩🇿",
      "Africa",
      "Algeri",
      "destra",
      "Tropicale, subtropicale, desertico e mediterraneo",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "AD",
      "Andorra",
      "Europa Occidentale",
      "Carta d'Identità / Passaporto",
      "Visa Free (Schengen)",
      "EUR (Euro)",
      "Schengen / Extra UE",
      "Consentito",
      1,
      "🇦🇩",
      "Europa",
      "Andorra la Vella",
      "destra",
      "Temperato / mediterraneo / continentale",
      false,
      false,
      true,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "AO",
      "Angola",
      "Africa Meridionale",
      "Passaporto",
      "eVisa / esenzione condizionata",
      "AOA (Kwanza)",
      "Extra UE / Extra Schengen",
      "eVisa / condizioni d'ingresso",
      1,
      "🇦🇴",
      "Africa",
      "Luanda",
      "destra",
      "Tropicale, subtropicale, desertico e mediterraneo",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "AG",
      "Antigua e Barbuda",
      "Caraibi",
      "Passaporto",
      "Visa Free",
      "XCD (Dollaro dei Caraibi orientali)",
      "Extra UE / Extra Schengen",
      "Consentito",
      1,
      "🇦🇬",
      "Americhe",
      "Saint John's",
      "sinistra",
      "Molto variabile: polare, temperato, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "AR",
      "Argentina",
      "Sud America",
      "Carta d'Identità / Passaporto",
      "Visa Free",
      "ARS (Peso argentino)",
      "Extra UE / Extra Schengen",
      "Consentito",
      1,
      "🇦🇷",
      "Americhe",
      "Buenos Aires",
      "destra",
      "Molto variabile: polare, temperato, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "AM",
      "Armenia",
      "Caucaso",
      "Passaporto",
      "Visa Free",
      "AMD (Dram armeno)",
      "Extra UE / Extra Schengen",
      "Consentito",
      1,
      "🇦🇲",
      "Da classificare",
      "Erevan",
      "destra",
      null,
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "AU",
      "Australia",
      "Oceania",
      "Passaporto",
      "eVisitor / autorizzazione elettronica",
      "AUD (Dollaro australiano)",
      "Extra UE / Extra Schengen",
      "Autorizzazione elettronica",
      1,
      "🇦🇺",
      "Oceania",
      "Canberra",
      "sinistra",
      "Tropicale, subtropicale e temperato",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "AT",
      "Austria",
      "Europa Centrale",
      "Carta d'Identità / Passaporto",
      "Visa Free (Area Schengen)",
      "EUR (Euro)",
      "UE / Schengen",
      "Consentito (regole UE)",
      1,
      "🇦🇹",
      "Europa",
      "Vienna",
      "destra",
      "Temperato / mediterraneo / continentale",
      true,
      true,
      true,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "AZ",
      "Azerbaigian",
      "Caucaso",
      "Passaporto",
      "eVisa",
      "AZN (Manat azero)",
      "Extra UE / Extra Schengen",
      "eVisa",
      1,
      "🇦🇿",
      "Da classificare",
      "Baku",
      "destra",
      null,
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BS",
      "Bahamas",
      "Caraibi",
      "Passaporto",
      "Visa Free",
      "BSD (Dollaro bahamense)",
      "Extra UE / Extra Schengen",
      "Consentito",
      1,
      "🇧🇸",
      "Americhe",
      "Nassau",
      "sinistra",
      "Molto variabile: polare, temperato, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BH",
      "Bahrein",
      "Golfo",
      "Passaporto",
      "Visa on Arrival / eVisa",
      "BHD (Dinaro del Bahrein)",
      "Extra UE / Extra Schengen",
      "eVisa / visto all'arrivo",
      1,
      "🇧🇭",
      "Da classificare",
      "Manama",
      "destra",
      null,
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BD",
      "Bangladesh",
      "Asia Meridionale",
      "Passaporto",
      "Visa on Arrival / visto",
      "BDT (Taka)",
      "Extra UE / Extra Schengen",
      "Visto / condizioni d'ingresso",
      1,
      "🇧🇩",
      "Asia",
      "Dhaka",
      "sinistra",
      "Molto variabile: temperato, continentale, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BB",
      "Barbados",
      "Caraibi",
      "Passaporto",
      "Visa Free",
      "BBD (Dollaro di Barbados)",
      "Extra UE / Extra Schengen",
      "Consentito",
      1,
      "🇧🇧",
      "Americhe",
      "Bridgetown",
      "sinistra",
      "Molto variabile: polare, temperato, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BY",
      "Bielorussia",
      "Europa Orientale",
      "Passaporto",
      "Visa Free / condizioni speciali",
      "BYN (Rublo bielorusso)",
      "Extra UE / Extra Schengen",
      "Condizioni speciali",
      1,
      "🇧🇾",
      "Europa",
      "Minsk",
      "destra",
      "Temperato / mediterraneo / continentale",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BE",
      "Belgio",
      "Europa Occidentale",
      "Carta d'Identità / Passaporto",
      "Visa Free (Area Schengen)",
      "EUR (Euro)",
      "UE / Schengen",
      "Consentito (regole UE)",
      1,
      "🇧🇪",
      "Europa",
      "Bruxelles",
      "destra",
      "Temperato / mediterraneo / continentale",
      true,
      true,
      true,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BZ",
      "Belize",
      "America Centrale",
      "Passaporto",
      "Visa Free",
      "BZD (Dollaro beliziano)",
      "Extra UE / Extra Schengen",
      "Consentito",
      1,
      "🇧🇿",
      "Americhe",
      "Belmopan",
      "destra",
      "Molto variabile: polare, temperato, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BJ",
      "Benin",
      "Africa Occidentale",
      "Passaporto",
      "eVisa",
      "XOF (Franco CFA BCEAO)",
      "Extra UE / Extra Schengen",
      "eVisa",
      1,
      "🇧🇯",
      "Africa",
      "Porto-Novo",
      "destra",
      "Tropicale, subtropicale, desertico e mediterraneo",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BT",
      "Bhutan",
      "Asia Meridionale",
      "Passaporto",
      "Visto / autorizzazione",
      "BTN (Ngultrum)",
      "Extra UE / Extra Schengen",
      "Autorizzazione richiesta",
      1,
      "🇧🇹",
      "Asia",
      "Thimphu",
      "sinistra",
      "Molto variabile: temperato, continentale, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BO",
      "Bolivia",
      "Sud America",
      "Carta d'Identità / Passaporto",
      "Visa Free",
      "BOB (Boliviano)",
      "Extra UE / Extra Schengen",
      "Consentito",
      1,
      "🇧🇴",
      "Americhe",
      "Sucre / La Paz (sede di governo)",
      "destra",
      "Molto variabile: polare, temperato, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BA",
      "Bosnia ed Erzegovina",
      "Europa Sud-orientale",
      "Carta d'Identità / Passaporto",
      "Visa Free",
      "BAM (Marco convertibile)",
      "Extra UE / Extra Schengen",
      "Consentito",
      1,
      "🇧🇦",
      "Europa",
      "Sarajevo",
      "destra",
      "Temperato / mediterraneo / continentale",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BW",
      "Botswana",
      "Africa Meridionale",
      "Passaporto",
      "Visa Free",
      "BWP (Pula)",
      "Extra UE / Extra Schengen",
      "Consentito",
      1,
      "🇧🇼",
      "Africa",
      "Gaborone",
      "sinistra",
      "Tropicale, subtropicale, desertico e mediterraneo",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BR",
      "Brasile",
      "Sud America",
      "Carta d'Identità / Passaporto",
      "Visa Free",
      "BRL (Real brasiliano)",
      "Extra UE / Extra Schengen",
      "Consentito",
      1,
      "🇧🇷",
      "Americhe",
      "Brasília",
      "destra",
      "Molto variabile: polare, temperato, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BN",
      "Brunei",
      "Sud-est asiatico",
      "Passaporto",
      "Visa Free",
      "BND (Dollaro del Brunei)",
      "Extra UE / Extra Schengen",
      "Consentito",
      1,
      "🇧🇳",
      "Asia",
      "Bandar Seri Begawan",
      "sinistra",
      "Molto variabile: temperato, continentale, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BG",
      "Bulgaria",
      "Europa Sud-orientale",
      "Carta d'Identità / Passaporto",
      "Visa Free (Area Schengen)",
      "EUR (Euro)",
      "UE / Schengen",
      "Consentito (regole UE)",
      1,
      "🇧🇬",
      "Europa",
      "Sofia",
      "destra",
      "Temperato / mediterraneo / continentale",
      true,
      true,
      true,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BF",
      "Burkina Faso",
      "Africa Occidentale",
      "Passaporto",
      "eVisa / visto",
      "XOF (Franco CFA BCEAO)",
      "Extra UE / Extra Schengen",
      "Visto / eVisa",
      1,
      "🇧🇫",
      "Africa",
      "Ouagadougou",
      "destra",
      "Tropicale, subtropicale, desertico e mediterraneo",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "BI",
      "Burundi",
      "Africa Orientale",
      "Passaporto",
      "Visa on Arrival / eVisa",
      "BIF (Franco burundese)",
      "Extra UE / Extra Schengen",
      "Visto all'arrivo / eVisa",
      1,
      "🇧🇮",
      "Africa",
      "Gitega",
      "destra",
      "Tropicale, subtropicale, desertico e mediterraneo",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "CV",
      "Capo Verde",
      "Africa Occidentale",
      "Passaporto",
      "Visa Free / preregistrazione",
      "CVE (Escudo capoverdiano)",
      "Extra UE / Extra Schengen",
      "Preregistrazione / condizioni",
      1,
      "🇨🇻",
      "Africa",
      "Praia",
      "destra",
      "Tropicale, subtropicale, desertico e mediterraneo",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "KH",
      "Cambogia",
      "Sud-est asiatico",
      "Passaporto",
      "eVisa / Visa on Arrival",
      "KHR (Riel)",
      "Extra UE / Extra Schengen",
      "eVisa / visto all'arrivo",
      1,
      "🇰🇭",
      "Asia",
      "Phnom Penh",
      "destra",
      "Molto variabile: temperato, continentale, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "CM",
      "Camerun",
      "Africa Centrale",
      "Passaporto",
      "eVisa",
      "XAF (Franco CFA BEAC)",
      "Extra UE / Extra Schengen",
      "eVisa",
      1,
      "🇨🇲",
      "Africa",
      "Yaoundé",
      "destra",
      "Tropicale, subtropicale, desertico e mediterraneo",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "CA",
      "Canada",
      "Nord America",
      "Passaporto",
      "eTA",
      "CAD (Dollaro canadese)",
      "Extra UE / Extra Schengen",
      "Autorizzazione elettronica",
      1,
      "🇨🇦",
      "Americhe",
      "Ottawa",
      "destra",
      "Molto variabile: polare, temperato, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "CF",
      "Repubblica Centrafricana",
      "Africa Centrale",
      "Passaporto",
      "Visto richiesto",
      "XAF (Franco CFA BEAC)",
      "Extra UE / Extra Schengen",
      "Visto richiesto",
      1,
      "🇨🇫",
      "Africa",
      "Bangui",
      "destra",
      "Tropicale, subtropicale, desertico e mediterraneo",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "TD",
      "Ciad",
      "Africa Centrale",
      "Passaporto",
      "Visto richiesto",
      "XAF (Franco CFA BEAC)",
      "Extra UE / Extra Schengen",
      "Visto richiesto",
      1,
      "🇹🇩",
      "Africa",
      "N'Djamena",
      "destra",
      "Tropicale, subtropicale, desertico e mediterraneo",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "CL",
      "Cile",
      "Sud America",
      "Carta d'Identità / Passaporto",
      "Visa Free",
      "CLP (Peso cileno)",
      "Extra UE / Extra Schengen",
      "Consentito",
      1,
      "🇨🇱",
      "Americhe",
      "Santiago",
      "destra",
      "Molto variabile: polare, temperato, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      "2026-09-06"
    ],
    [
      "CN",
      "Cina",
      "Asia Orientale",
      "Passaporto",
      "Visto / esenzioni temporanee",
      "CNY (Yuan renminbi)",
      "Extra UE / Extra Schengen",
      "Verifica esenzione / visto",
      1,
      "🇨🇳",
      "Asia",
      "Pechino",
      "destra",
      "Molto variabile: temperato, continentale, tropicale e desertico",
      false,
      false,
      false,
      null,
      null,
      null,
      null,
      null,
      null,
      nul

[Contenuto abbreviato: file oltre il limite di lettura.]
```

## `resources/sprite.json`

Nota: File JSON: verificare dal contenuto se è configurazione o dato.

```text
{
  "ad": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 0,
    "iso_alpha2": "AD",
    "iso_alpha3": "AND",
    "iso_numeric": "020",
    "name_it": "Andorra",
    "name_en": "Andorra"
  },
  "ae": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 18,
    "iso_alpha2": "AE",
    "iso_alpha3": "ARE",
    "iso_numeric": "784",
    "name_it": "Emirati Arabi Uniti",
    "name_en": "United Arab Emirates"
  },
  "af": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 36,
    "iso_alpha2": "AF",
    "iso_alpha3": "AFG",
    "iso_numeric": "004",
    "name_it": "Afghanistan",
    "name_en": "Afghanistan"
  },
  "ag": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 54,
    "iso_alpha2": "AG",
    "iso_alpha3": "ATG",
    "iso_numeric": "028",
    "name_it": "Antigua e Barbuda",
    "name_en": "Antigua & Barbuda"
  },
  "ai": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 72,
    "iso_alpha2": "AI",
    "iso_alpha3": "AIA",
    "iso_numeric": "008",
    "name_it": "Anguilla",
    "name_en": "Anguilla"
  },
  "al": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 90,
    "iso_alpha2": "AL",
    "iso_alpha3": "ALB",
    "iso_numeric": "008",
    "name_it": "Albania",
    "name_en": "Albania"
  },
  "am": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 108,
    "iso_alpha2": "AM",
    "iso_alpha3": "ARM",
    "iso_numeric": "051",
    "name_it": "Armenia",
    "name_en": "Armenia"
  },
  "ao": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 126,
    "iso_alpha2": "AO",
    "iso_alpha3": "AGO",
    "iso_numeric": "024",
    "name_it": "Angola",
    "name_en": "Angola"
  },
  "aq": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 144,
    "iso_alpha2": "AQ",
    "iso_alpha3": "ATA",
    "iso_numeric": "010",
    "name_it": "Antartide",
    "name_en": "Antarctica"
  },
  "ar": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 162,
    "iso_alpha2": "AR",
    "iso_alpha3": "ARG",
    "iso_numeric": "032",
    "name_it": "Argentina",
    "name_en": "Argentina"
  },
  "arab": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 180,
    "iso_alpha2": "ARAB",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "ARAB",
    "name_en": "ARAB"
  },
  "as": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 198,
    "iso_alpha2": "AS",
    "iso_alpha3": "ASM",
    "iso_numeric": "016",
    "name_it": "Samoa Americane",
    "name_en": "American Samoa"
  },
  "asean": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 216,
    "iso_alpha2": "ASEAN",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "ASEAN",
    "name_en": "ASEAN"
  },
  "at": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 234,
    "iso_alpha2": "AT",
    "iso_alpha3": "AUT",
    "iso_numeric": "040",
    "name_it": "Austria",
    "name_en": "Austria"
  },
  "au": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 0,
    "iso_alpha2": "AU",
    "iso_alpha3": "AUS",
    "iso_numeric": "036",
    "name_it": "Australia",
    "name_en": "Australia"
  },
  "aw": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 18,
    "iso_alpha2": "AW",
    "iso_alpha3": "ABW",
    "iso_numeric": "053",
    "name_it": "Aruba",
    "name_en": "Aruba"
  },
  "ax": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 36,
    "iso_alpha2": "AX",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "AX",
    "name_en": "AX"
  },
  "az": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 54,
    "iso_alpha2": "AZ",
    "iso_alpha3": "AZE",
    "iso_numeric": "031",
    "name_it": "Azerbaigian",
    "name_en": "Azerbaijan"
  },
  "ba": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 72,
    "iso_alpha2": "BA",
    "iso_alpha3": "BIH",
    "iso_numeric": "070",
    "name_it": "Bosnia ed Erzegovina",
    "name_en": "Bosnia & Herzegovina"
  },
  "bb": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 90,
    "iso_alpha2": "BB",
    "iso_alpha3": "BRB",
    "iso_numeric": "052",
    "name_it": "Barbados",
    "name_en": "Barbados"
  },
  "bd": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 108,
    "iso_alpha2": "BD",
    "iso_alpha3": "BGD",
    "iso_numeric": "050",
    "name_it": "Bangladesh",
    "name_en": "Bangladesh"
  },
  "be": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 126,
    "iso_alpha2": "BE",
    "iso_alpha3": "BEL",
    "iso_numeric": "056",
    "name_it": "Belgio",
    "name_en": "Belgium"
  },
  "bf": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 144,
    "iso_alpha2": "BF",
    "iso_alpha3": "BFA",
    "iso_numeric": "854",
    "name_it": "Burkina Faso",
    "name_en": "Burkina Faso"
  },
  "bg": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 162,
    "iso_alpha2": "BG",
    "iso_alpha3": "BGR",
    "iso_numeric": "100",
    "name_it": "Bulgaria",
    "name_en": "Bulgaria"
  },
  "bh": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 180,
    "iso_alpha2": "BH",
    "iso_alpha3": "BHR",
    "iso_numeric": "048",
    "name_it": "Bahrein",
    "name_en": "Bahrain"
  },
  "bi": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 198,
    "iso_alpha2": "BI",
    "iso_alpha3": "BDI",
    "iso_numeric": "108",
    "name_it": "Burundi",
    "name_en": "Burundi"
  },
  "bj": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 216,
    "iso_alpha2": "BJ",
    "iso_alpha3": "BEN",
    "iso_numeric": "204",
    "name_it": "Benin",
    "name_en": "Benin"
  },
  "bl": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 234,
    "iso_alpha2": "BL",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "BL",
    "name_en": "BL"
  },
  "bm": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 0,
    "iso_alpha2": "BM",
    "iso_alpha3": "BMU",
    "iso_numeric": "060",
    "name_it": "Bermuda",
    "name_en": "Bermuda"
  },
  "bn": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 18,
    "iso_alpha2": "BN",
    "iso_alpha3": "BRN",
    "iso_numeric": "096",
    "name_it": "Brunei",
    "name_en": "Brunei"
  },
  "bo": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 36,
    "iso_alpha2": "BO",
    "iso_alpha3": "BOL",
    "iso_numeric": "068",
    "name_it": "Bolivia",
    "name_en": "Bolivia"
  },
  "bq": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 54,
    "iso_alpha2": "BQ",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "BQ",
    "name_en": "BQ"
  },
  "br": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 72,
    "iso_alpha2": "BR",
    "iso_alpha3": "BRA",
    "iso_numeric": "076",
    "name_it": "Brasile",
    "name_en": "Brazil"
  },
  "bs": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 90,
    "iso_alpha2": "BS",
    "iso_alpha3": "BHS",
    "iso_numeric": "044",
    "name_it": "Bahamas",
    "name_en": "Bahamas"
  },
  "bt": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 108,
    "iso_alpha2": "BT",
    "iso_alpha3": "BTN",
    "iso_numeric": "064",
    "name_it": "Bhutan",
    "name_en": "Bhutan"
  },
  "bv": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 126,
    "iso_alpha2": "BV",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "BV",
    "name_en": "BV"
  },
  "bw": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 144,
    "iso_alpha2": "BW",
    "iso_alpha3": "BWA",
    "iso_numeric": "072",
    "name_it": "Botswana",
    "name_en": "Botswana"
  },
  "by": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 162,
    "iso_alpha2": "BY",
    "iso_alpha3": "BLR",
    "iso_numeric": "112",
    "name_it": "Bielorussia",
    "name_en": "Belarus"
  },
  "bz": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 180,
    "iso_alpha2": "BZ",
    "iso_alpha3": "BLZ",
    "iso_numeric": "084",
    "name_it": "Belize",
    "name_en": "Belize"
  },
  "ca": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 198,
    "iso_alpha2": "CA",
    "iso_alpha3": "CAN",
    "iso_numeric": "124",
    "name_it": "Canada",
    "name_en": "Canada"
  },
  "cc": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 216,
    "iso_alpha2": "CC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "CC",
    "name_en": "CC"
  },
  "cd": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 234,
    "iso_alpha2": "CD",
    "iso_alpha3": "COD",
    "iso_numeric": "180",
    "name_it": "Congo-Kinshasa",
    "name_en": "Congo - Kinshasa"
  },
  "cefta": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 0,
    "iso_alpha2": "CEFTA",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "CEFTA",
    "name_en": "CEFTA"
  },
  "cf": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 18,
    "iso_alpha2": "CF",
    "iso_alpha3": "CAF",
    "iso_numeric": "140",
    "name_it": "Repubblica Centrafricana",
    "name_en": "Central African Republic"
  },
  "cg": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 36,
    "iso_alpha2": "CG",
    "iso_alpha3": "COG",
    "iso_numeric": "178",
    "name_it": "Congo-Brazzaville",
    "name_en": "Congo - Brazzaville"
  },
  "ch": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 54,
    "iso_alpha2": "CH",
    "iso_alpha3": "CHE",
    "iso_numeric": "756",
    "name_it": "Svizzera",
    "name_en": "Switzerland"
  },
  "ci": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 72,
    "iso_alpha2": "CI",
    "iso_alpha3": "CIV",
    "iso_numeric": "384",
    "name_it": "Costa d'Avorio",
    "name_en": "Côte d’Ivoire"
  },
  "ck": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 90,
    "iso_alpha2": "CK",
    "iso_alpha3": "COK",
    "iso_numeric": "184",
    "name_it": "Isole Cook",
    "name_en": "Cook Islands"
  },
  "cl": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 108,
    "iso_alpha2": "CL",
    "iso_alpha3": "CHL",
    "iso_numeric": "152",
    "name_it": "Cile",
    "name_en": "Chile"
  },
  "cm": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 126,
    "iso_alpha2": "CM",
    "iso_alpha3": "CMR",
    "iso_numeric": "120",
    "name_it": "Camerun",
    "name_en": "Cameroon"
  },
  "cn": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 144,
    "iso_alpha2": "CN",
    "iso_alpha3": "CHN",
    "iso_numeric": "156",
    "name_it": "Cina",
    "name_en": "China"
  },
  "co": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 162,
    "iso_alpha2": "CO",
    "iso_alpha3": "COL",
    "iso_numeric": "170",
    "name_it": "Colombia",
    "name_en": "Colombia"
  },
  "cp": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 180,
    "iso_alpha2": "CP",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "CP",
    "name_en": "CP"
  },
  "cr": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 198,
    "iso_alpha2": "CR",
    "iso_alpha3": "CRI",
    "iso_numeric": "188",
    "name_it": "Costa Rica",
    "name_en": "Costa Rica"
  },
  "cu": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 216,
    "iso_alpha2": "CU",
    "iso_alpha3": "CUB",
    "iso_numeric": "192",
    "name_it": "Cuba",
    "name_en": "Cuba"
  },
  "cv": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 234,
    "iso_alpha2": "CV",
    "iso_alpha3": "CPV",
    "iso_numeric": "132",
    "name_it": "Capo Verde",
    "name_en": "Cape Verde"
  },
  "cw": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 0,
    "iso_alpha2": "CW",
    "iso_alpha3": "CUW",
    "iso_numeric": "531",
    "name_it": "Curaçao",
    "name_en": "Curaçao"
  },
  "cx": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 18,
    "iso_alpha2": "CX",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "CX",
    "name_en": "CX"
  },
  "cy": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 36,
    "iso_alpha2": "CY",
    "iso_alpha3": "CYP",
    "iso_numeric": "196",
    "name_it": "Cipro",
    "name_en": "Cyprus"
  },
  "cz": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 54,
    "iso_alpha2": "CZ",
    "iso_alpha3": "CZE",
    "iso_numeric": "203",
    "name_it": "Cechia",
    "name_en": "Czechia"
  },
  "de": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 72,
    "iso_alpha2": "DE",
    "iso_alpha3": "DEU",
    "iso_numeric": "276",
    "name_it": "Germania",
    "name_en": "Germany"
  },
  "dg": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 90,
    "iso_alpha2": "DG",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "DG",
    "name_en": "DG"
  },
  "dj": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 108,
    "iso_alpha2": "DJ",
    "iso_alpha3": "DJI",
    "iso_numeric": "262",
    "name_it": "Gibuti",
    "name_en": "Djibouti"
  },
  "dk": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 126,
    "iso_alpha2": "DK",
    "iso_alpha3": "DNK",
    "iso_numeric": "208",
    "name_it": "Danimarca",
    "name_en": "Denmark"
  },
  "dm": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 144,
    "iso_alpha2": "DM",
    "iso_alpha3": "DMA",
    "iso_numeric": "212",
    "name_it": "Dominica",
    "name_en": "Dominica"
  },
  "do": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 162,
    "iso_alpha2": "DO",
    "iso_alpha3": "DOM",
    "iso_numeric": "214",
    "name_it": "Repubblica Dominicana",
    "name_en": "Dominican Republic"
  },
  "dz": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 180,
    "iso_alpha2": "DZ",
    "iso_alpha3": "DZA",
    "iso_numeric": "012",
    "name_it": "Algeria",
    "name_en": "Algeria"
  },
  "eac": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 198,
    "iso_alpha2": "EAC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "EAC",
    "name_en": "EAC"
  },
  "ec": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 216,
    "iso_alpha2": "EC",
    "iso_alpha3": "ECU",
    "iso_numeric": "218",
    "name_it": "Ecuador",
    "name_en": "Ecuador"
  },
  "ee": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 234,
    "iso_alpha2": "EE",
    "iso_alpha3": "EST",
    "iso_numeric": "233",
    "name_it": "Estonia",
    "name_en": "Estonia"
  },
  "eg": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 0,
    "iso_alpha2": "EG",
    "iso_alpha3": "EGY",
    "iso_numeric": "818",
    "name_it": "Egitto",
    "name_en": "Egypt"
  },
  "eh": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 18,
    "iso_alpha2": "EH",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "EH",
    "name_en": "EH"
  },
  "er": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 36,
    "iso_alpha2": "ER",
    "iso_alpha3": "ERI",
    "iso_numeric": "232",
    "name_it": "Eritrea",
    "name_en": "Eritrea"
  },
  "es": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 54,
    "iso_alpha2": "ES",
    "iso_alpha3": "ESP",
    "iso_numeric": "724",
    "name_it": "Spagna",
    "name_en": "Spain"
  },
  "es-ct": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 72,
    "iso_alpha2": "ES-CT",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "ES-CT",
    "name_en": "ES-CT"
  },
  "es-ga": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 90,
    "iso_alpha2": "ES-GA",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "ES-GA",
    "name_en": "ES-GA"
  },
  "es-pv": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 108,
    "iso_alpha2": "ES-PV",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "ES-PV",
    "name_en": "ES-PV"
  },
  "et": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 126,
    "iso_alpha2": "ET",
    "iso_alpha3": "ETH",
    "iso_numeric": "231",
    "name_it": "Etiopia",
    "name_en": "Ethiopia"
  },
  "eu": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 144,
    "iso_alpha2": "EU",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "EU",
    "name_en": "EU"
  },
  "fi": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 162,
    "iso_alpha2": "FI",
    "iso_alpha3": "FIN",
    "iso_numeric": "246",
    "name_it": "Finlandia",
    "name_en": "Finland"
  },
  "fj": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 180,
    "iso_alpha2": "FJ",
    "iso_alpha3": "FJI",
    "iso_numeric": "242",
    "name_it": "Figi",
    "name_en": "Fiji"
  },
  "fk": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 198,
    "iso_alpha2": "FK",
    "iso_alpha3": "FLK",
    "iso_numeric": "238",
    "name_it": "Isole Falkland",
    "name_en": "Falkland Islands"
  },
  "fm": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 216,
    "iso_alpha2": "FM",
    "iso_alpha3": "FSM",
    "iso_numeric": "583",
    "name_it": "Micronesia",
    "name_en": "Micronesia"
  },
  "fo": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 234,
    "iso_alpha2": "FO",
    "iso_alpha3": "FRO",
    "iso_numeric": "234",
    "name_it": "Isole Fær Øer",
    "name_en": "Faroe Islands"
  },
  "fr": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 0,
    "iso_alpha2": "FR",
    "iso_alpha3": "FRA",
    "iso_numeric": "250",
    "name_it": "Francia",
    "name_en": "France"
  },
  "ga": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 18,
    "iso_alpha2": "GA",
    "iso_alpha3": "GAB",
    "iso_numeric": "266",
    "name_it": "Gabon",
    "name_en": "Gabon"
  },
  "gb": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 36,
    "iso_alpha2": "GB",
    "iso_alpha3": "GBR",
    "iso_numeric": "826",
    "name_it": "Regno Unito",
    "name_en": "United Kingdom"
  },
  "gb-eng": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 54,
    "iso_alpha2": "GB-ENG",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "GB-ENG",
    "name_en": "GB-ENG"
  },
  "gb-nir": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 72,
    "iso_alpha2": "GB-NIR",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "GB-NIR",
    "name_en": "GB-NIR"
  },
  "gb-sct": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 90,
    "iso_alpha2": "GB-SCT",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "GB-SCT",
    "name_en": "GB-SCT"
  },
  "gb-wls": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 108,
    "iso_alpha2": "GB-WLS",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "GB-WLS",
    "name_en": "GB-WLS"
  },
  "gd": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 126,
    "iso_alpha2": "GD",
    "iso_alpha3": "GRD",
    "iso_numeric": "308",
    "name_it": "Grenada",
    "name_en": "Grenada"
  },
  "ge": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 144,
    "iso_alpha2": "GE",
    "iso_alpha3": "GEO",
    "iso_numeric": "268",
    "name_it": "Georgia",
    "name_en": "Georgia"
  },
  "gf": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 162,
    "iso_alpha2": "GF",
    "iso_alpha3": "GUF",
    "iso_numeric": "254",
    "name_it": "Guyana Francese",
    "name_en": "French Guiana"
  },
  "gg": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 180,
    "iso_alpha2": "GG",
    "iso_alpha3": "GGY",
    "iso_numeric": "831",
    "name_it": "Guernsey",
    "name_en": "Guernsey"
  },
  "gh": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 198,
    "iso_alpha2": "GH",
    "iso_alpha3": "GHA",
    "iso_numeric": "288",
    "name_it": "Ghana",
    "name_en": "Ghana"
  },
  "gi": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 216,
    "iso_alpha2": "GI",
    "iso_alpha3": "GIB",
    "iso_numeric": "292",
    "name_it": "Gibilterra",
    "name_en": "Gibraltar"
  },
  "gl": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 234,
    "iso_alpha2": "GL",
    "iso_alpha3": "GRL",
    "iso_numeric": "304",
    "name_it": "Groenlandia",
    "name_en": "Greenland"
  },
  "gm": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 0,
    "iso_alpha2": "GM",
    "iso_alpha3": "GMB",
    "iso_numeric": "270",
    "name_it": "Gambia",
    "name_en": "Gambia"
  },
  "gn": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 18,
    "iso_alpha2": "GN",
    "iso_alpha3": "GIN",
    "iso_numeric": "324",
    "name_it": "Guinea",
    "name_en": "Guinea"
  },
  "gp": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 36,
    "iso_alpha2": "GP",
    "iso_alpha3": "GLP",
    "iso_numeric": "312",
    "name_it": "Guadalupa",
    "name_en": "Guadeloupe"
  },
  "gq": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 54,
    "iso_alpha2": "GQ",
    "iso_alpha3": "GNQ",
    "iso_numeric": "226",
    "name_it": "Guinea Equatoriale",
    "name_en": "Equatorial Guinea"
  },
  "gr": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 72,
    "iso_alpha2": "GR",
    "iso_alpha3": "GRC",
    "iso_numeric": "300",
    "name_it": "Grecia",
    "name_en": "Greece"
  },
  "gs": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 90,
    "iso_alpha2": "GS",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "GS",
    "name_en": "GS"
  },
  "gt": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 108,
    "iso_alpha2": "GT",
    "iso_alpha3": "GTM",
    "iso_numeric": "320",
    "name_it": "Guatemala",
    "name_en": "Guatemala"
  },
  "gu": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 126,
    "iso_alpha2": "GU",
    "iso_alpha3": "GUM",
    "iso_numeric": "316",
    "name_it": "Guam",
    "name_en": "Guam"
  },
  "gw": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 144,
    "iso_alpha2": "GW",
    "iso_alpha3": "GNB",
    "iso_numeric": "624",
    "name_it": "Guinea-Bissau",
    "name_en": "Guinea-Bissau"
  },
  "gy": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 162,
    "iso_alpha2": "GY",
    "iso_alpha3": "GUY",
    "iso_numeric": "328",
    "name_it": "Guyana",
    "name_en": "Guyana"
  },
  "hk": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 180,
    "iso_alpha2": "HK",
    "iso_alpha3": "HKG",
    "iso_numeric": "344",
    "name_it": "Hong Kong",
    "name_en": "Hong Kong SAR China"
  },
  "hm": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 198,
    "iso_alpha2": "HM",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "HM",
    "name_en": "HM"
  },
  "hn": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 216,
    "iso_alpha2": "HN",
    "iso_alpha3": "HND",
    "iso_numeric": "340",
    "name_it": "Honduras",
    "name_en": "Honduras"
  },
  "hr": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 234,
    "iso_alpha2": "HR",
    "iso_alpha3": "HRV",
    "iso_numeric": "191",
    "name_it": "Croazia",
    "name_en": "Croatia"
  },
  "ht": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 0,
    "iso_alpha2": "HT",
    "iso_alpha3": "HTI",
    "iso_numeric": "332",
    "name_it": "Haiti",
    "name_en": "Haiti"
  },
  "hu": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 0,
    "iso_alpha2": "HU",
    "iso_alpha3": "HUN",
    "iso_numeric": "348",
    "name_it": "Ungheria",
    "name_en": "Hungary"
  },
  "ic": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 0,
    "iso_alpha2": "IC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "IC",
    "name_en": "IC"
  },
  "id": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 0,
    "iso_alpha2": "ID",
    "iso_alpha3": "IDN",
    "iso_numeric": "360",
    "name_it": "Indonesia",
    "name_en": "Indonesia"
  },
  "ie": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 0,
    "iso_alpha2": "IE",
    "iso_alpha3": "IRL",
    "iso_numeric": "372",
    "name_it": "Irlanda",
    "name_en": "Ireland"
  },
  "il": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 0,
    "iso_alpha2": "IL",
    "iso_alpha3": "ISR",
    "iso_numeric": "376",
    "name_it": "Israele",
    "name_en": "Israel"
  },
  "im": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 0,
    "iso_alpha2": "IM",
    "iso_alpha3": "IMN",
    "iso_numeric": "833",
    "name_it": "Isola di Man",
    "name_en": "Isle of Man"
  },
  "in": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 0,
    "iso_alpha2": "IN",
    "iso_alpha3": "IND",
    "iso_numeric": "356",
    "name_it": "India",
    "name_en": "India"
  },
  "io": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 0,
    "iso_alpha2": "IO",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "IO",
    "name_en": "IO"
  },
  "iq": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 0,
    "iso_alpha2": "IQ",
    "iso_alpha3": "IRQ",
    "iso_numeric": "368",
    "name_it": "Iraq",
    "name_en": "Iraq"
  },
  "ir": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 0,
    "iso_alpha2": "IR",
    "iso_alpha3": "IRN",
    "iso_numeric": "364",
    "name_it": "Iran",
    "name_en": "Iran"
  },
  "is": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 0,
    "iso_alpha2": "IS",
    "iso_alpha3": "ISL",
    "iso_numeric": "352",
    "name_it": "Islanda",
    "name_en": "Iceland"
  },
  "it": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 0,
    "iso_alpha2": "IT",
    "iso_alpha3": "ITA",
    "iso_numeric": "380",
    "name_it": "Italia",
    "name_en": "Italy"
  },
  "je": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 18,
    "iso_alpha2": "JE",
    "iso_alpha3": "JEY",
    "iso_numeric": "832",
    "name_it": "Jersey",
    "name_en": "Jersey"
  },
  "jm": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 36,
    "iso_alpha2": "JM",
    "iso_alpha3": "JAM",
    "iso_numeric": "388",
    "name_it": "Giamaica",
    "name_en": "Jamaica"
  },
  "jo": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 54,
    "iso_alpha2": "JO",
    "iso_alpha3": "JOR",
    "iso_numeric": "400",
    "name_it": "Giordania",
    "name_en": "Jordan"
  },
  "jp": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 72,
    "iso_alpha2": "JP",
    "iso_alpha3": "JPN",
    "iso_numeric": "392",
    "name_it": "Giappone",
    "name_en": "Japan"
  },
  "ke": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 90,
    "iso_alpha2": "KE",
    "iso_alpha3": "KEN",
    "iso_numeric": "404",
    "name_it": "Kenya",
    "name_en": "Kenya"
  },
  "kg": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 108,
    "iso_alpha2": "KG",
    "iso_alpha3": "KGZ",
    "iso_numeric": "417",
    "name_it": "Kirghizistan",
    "name_en": "Kyrgyzstan"
  },
  "kh": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 126,
    "iso_alpha2": "KH",
    "iso_alpha3": "KHM",
    "iso_numeric": "116",
    "name_it": "Cambogia",
    "name_en": "Cambodia"
  },
  "ki": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 144,
    "iso_alpha2": "KI",
    "iso_alpha3": "KIR",
    "iso_numeric": "296",
    "name_it": "Kiribati",
    "name_en": "Kiribati"
  },
  "km": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 162,
    "iso_alpha2": "KM",
    "iso_alpha3": "COM",
    "iso_numeric": "174",
    "name_it": "Comore",
    "name_en": "Comoros"
  },
  "kn": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 180,
    "iso_alpha2": "KN",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "KN",
    "name_en": "KN"
  },
  "kp": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 198,
    "iso_alpha2": "KP",
    "iso_alpha3": "PRK",
    "iso_numeric": "408",
    "name_it": "Corea del Nord",
    "name_en": "North Korea"
  },
  "kr": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 216,
    "iso_alpha2": "KR",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "KR",
    "name_en": "KR"
  },
  "kw": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 234,
    "iso_alpha2": "KW",
    "iso_alpha3": "KWT",
    "iso_numeric": "414",
    "name_it": "Kuwait",
    "name_en": "Kuwait"
  },
  "ky": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 18,
    "iso_alpha2": "KY",
    "iso_alpha3": "CYM",
    "iso_numeric": "136",
    "name_it": "Isole Cayman",
    "name_en": "Cayman Islands"
  },
  "kz": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 18,
    "iso_alpha2": "KZ",
    "iso_alpha3": "KAZ",
    "iso_numeric": "398",
    "name_it": "Kazakistan",
    "name_en": "Kazakhstan"
  },
  "la": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 18,
    "iso_alpha2": "LA",
    "iso_alpha3": "LAO",
    "iso_numeric": "418",
    "name_it": "Laos",
    "name_en": "Laos"
  },
  "lb": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 18,
    "iso_alpha2": "LB",
    "iso_alpha3": "LBN",
    "iso_numeric": "422",
    "name_it": "Libano",
    "name_en": "Lebanon"
  },
  "lc": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 18,
    "iso_alpha2": "LC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "LC",
    "name_en": "LC"
  },
  "li": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 18,
    "iso_alpha2": "LI",
    "iso_alpha3": "LIE",
    "iso_numeric": "438",
    "name_it": "Liechtenstein",
    "name_en": "Liechtenstein"
  },
  "lk": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 18,
    "iso_alpha2": "LK",
    "iso_alpha3": "LKA",
    "iso_numeric": "144",
    "name_it": "Sri Lanka",
    "name_en": "Sri Lanka"
  },
  "lr": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 18,
    "iso_alpha2": "LR",
    "iso_alpha3": "LBR",
    "iso_numeric": "430",
    "name_it": "Liberia",
    "name_en": "Liberia"
  },
  "ls": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 18,
    "iso_alpha2": "LS",
    "iso_alpha3": "LSO",
    "iso_numeric": "426",
    "name_it": "Lesotho",
    "name_en": "Lesotho"
  },
  "lt": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 18,
    "iso_alpha2": "LT",
    "iso_alpha3": "LTU",
    "iso_numeric": "440",
    "name_it": "Lituania",
    "name_en": "Lithuania"
  },
  "lu": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 18,
    "iso_alpha2": "LU",
    "iso_alpha3": "LUX",
    "iso_numeric": "442",
    "name_it": "Lussemburgo",
    "name_en": "Luxembourg"
  },
  "lv": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 18,
    "iso_alpha2": "LV",
    "iso_alpha3": "LVA",
    "iso_numeric": "428",
    "name_it": "Lettonia",
    "name_en": "Latvia"
  },
  "ly": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 36,
    "iso_alpha2": "LY",
    "iso_alpha3": "LBY",
    "iso_numeric": "434",
    "name_it": "Libia",
    "name_en": "Libya"
  },
  "ma": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 54,
    "iso_alpha2": "MA",
    "iso_alpha3": "MAR",
    "iso_numeric": "504",
    "name_it": "Marocco",
    "name_en": "Morocco"
  },
  "mc": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 72,
    "iso_alpha2": "MC",
    "iso_alpha3": "MCO",
    "iso_numeric": "492",
    "name_it": "Monaco",
    "name_en": "Monaco"
  },
  "md": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 90,
    "iso_alpha2": "MD",
    "iso_alpha3": "MDA",
    "iso_numeric": "498",
    "name_it": "Moldavia",
    "name_en": "Moldova"
  },
  "me": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 108,
    "iso_alpha2": "ME",
    "iso_alpha3": "MNE",
    "iso_numeric": "499",
    "name_it": "Montenegro",
    "name_en": "Montenegro"
  },
  "mf": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 126,
    "iso_alpha2": "MF",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "MF",
    "name_en": "MF"
  },
  "mg": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 144,
    "iso_alpha2": "MG",
    "iso_alpha3": "MDG",
    "iso_numeric": "450",
    "name_it": "Madagascar",
    "name_en": "Madagascar"
  },
  "mh": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 162,
    "iso_alpha2": "MH",
    "iso_alpha3": "MHL",
    "iso_numeric": "584",
    "name_it": "Isole Marshall",
    "name_en": "Marshall Islands"
  },
  "mk": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 180,
    "iso_alpha2": "MK",
    "iso_alpha3": "MKD",
    "iso_numeric": "807",
    "name_it": "Macedonia del Nord",
    "name_en": "North Macedonia"
  },
  "ml": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 198,
    "iso_alpha2": "ML",
    "iso_alpha3": "MLI",
    "iso_numeric": "466",
    "name_it": "Mali",
    "name_en": "Mali"
  },
  "mm": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 216,
    "iso_alpha2": "MM",
    "iso_alpha3": "MMR",
    "iso_numeric": "104",
    "name_it": "Myanmar",
    "name_en": "Myanmar (Burma)"
  },
  "mn": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 234,
    "iso_alpha2": "MN",
    "iso_alpha3": "MNG",
    "iso_numeric": "496",
    "name_it": "Mongolia",
    "name_en": "Mongolia"
  },
  "mo": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 36,
    "iso_alpha2": "MO",
    "iso_alpha3": "MAC",
    "iso_numeric": "446",
    "name_it": "Macao",
    "name_en": "Macao SAR China"
  },
  "mp": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 36,
    "iso_alpha2": "MP",
    "iso_alpha3": "MNP",
    "iso_numeric": "580",
    "name_it": "Isole Marianne Settentrionali",
    "name_en": "Northern Mariana Islands"
  },
  "mq": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 36,
    "iso_alpha2": "MQ",
    "iso_alpha3": "MTQ",
    "iso_numeric": "474",
    "name_it": "Martinica",
    "name_en": "Martinique"
  },
  "mr": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 36,
    "iso_alpha2": "MR",
    "iso_alpha3": "MRT",
    "iso_numeric": "478",
    "name_it": "Mauritania",
    "name_en": "Mauritania"
  },
  "ms": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 36,
    "iso_alpha2": "MS",
    "iso_alpha3": "MSR",
    "iso_numeric": "500",
    "name_it": "Montserrat",
    "name_en": "Montserrat"
  },
  "mt": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 36,
    "iso_alpha2": "MT",
    "iso_alpha3": "MLT",
    "iso_numeric": "470",
    "name_it": "Malta",
    "name_en": "Malta"
  },
  "mu": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 36,
    "iso_alpha2": "MU",
    "iso_alpha3": "MUS",
    "iso_numeric": "480",
    "name_it": "Mauritius",
    "name_en": "Mauritius"
  },
  "mv": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 36,
    "iso_alpha2": "MV",
    "iso_alpha3": "MDV",
    "iso_numeric": "462",
    "name_it": "Maldive",
    "name_en": "Maldives"
  },
  "mw": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 36,
    "iso_alpha2": "MW",
    "iso_alpha3": "MWI",
    "iso_numeric": "454",
    "name_it": "Malawi",
    "name_en": "Malawi"
  },
  "mx": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 36,
    "iso_alpha2": "MX",
    "iso_alpha3": "MEX",
    "iso_numeric": "484",
    "name_it": "Messico",
    "name_en": "Mexico"
  },
  "my": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 36,
    "iso_alpha2": "MY",
    "iso_alpha3": "MYS",
    "iso_numeric": "458",
    "name_it": "Malesia",
    "name_en": "Malaysia"
  },
  "mz": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 54,
    "iso_alpha2": "MZ",
    "iso_alpha3": "MOZ",
    "iso_numeric": "508",
    "name_it": "Mozambico",
    "name_en": "Mozambique"
  },
  "na": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 72,
    "iso_alpha2": "NA",
    "iso_alpha3": "NAM",
    "iso_numeric": "516",
    "name_it": "Namibia",
    "name_en": "Namibia"
  },
  "nc": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 90,
    "iso_alpha2": "NC",
    "iso_alpha3": "NCL",
    "iso_numeric": "540",
    "name_it": "Nuova Caledonia",
    "name_en": "New Caledonia"
  },
  "ne": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 108,
    "iso_alpha2": "NE",
    "iso_alpha3": "NER",
    "iso_numeric": "562",
    "name_it": "Niger",
    "name_en": "Niger"
  },
  "nf": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 126,
    "iso_alpha2": "NF",
    "iso_alpha3": "NFK",
    "iso_numeric": "574",
    "name_it": "Isola Norfolk",
    "name_en": "Norfolk Island"
  },
  "ng": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 144,
    "iso_alpha2": "NG",
    "iso_alpha3": "NGA",
    "iso_numeric": "566",
    "name_it": "Nigeria",
    "name_en": "Nigeria"
  },
  "ni": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 162,
    "iso_alpha2": "NI",
    "iso_alpha3": "NIC",
    "iso_numeric": "558",
    "name_it": "Nicaragua",
    "name_en": "Nicaragua"
  },
  "nl": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 180,
    "iso_alpha2": "NL",
    "iso_alpha3": "NLD",
    "iso_numeric": "528",
    "name_it": "Paesi Bassi",
    "name_en": "Netherlands"
  },
  "no": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 198,
    "iso_alpha2": "NO",
    "iso_alpha3": "NOR",
    "iso_numeric": "578",
    "name_it": "Norvegia",
    "name_en": "Norway"
  },
  "np": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 216,
    "iso_alpha2": "NP",
    "iso_alpha3": "NPL",
    "iso_numeric": "524",
    "name_it": "Nepal",
    "name_en": "Nepal"
  },
  "nr": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 234,
    "iso_alpha2": "NR",
    "iso_alpha3": "NRU",
    "iso_numeric": "520",
    "name_it": "Nauru",
    "name_en": "Nauru"
  },
  "nu": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 54,
    "iso_alpha2": "NU",
    "iso_alpha3": "NIU",
    "iso_numeric": "570",
    "name_it": "Niue",
    "name_en": "Niue"
  },
  "nz": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 54,
    "iso_alpha2": "NZ",
    "iso_alpha3": "NZL",
    "iso_numeric": "554",
    "name_it": "Nuova Zelanda",
    "name_en": "New Zealand"
  },
  "om": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 54,
    "iso_alpha2": "OM",
    "iso_alpha3": "OMN",
    "iso_numeric": "512",
    "name_it": "Oman",
    "name_en": "Oman"
  },
  "pa": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 54,
    "iso_alpha2": "PA",
    "iso_alpha3": "PAN",
    "iso_numeric": "591",
    "name_it": "Panama",
    "name_en": "Panama"
  },
  "pc": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 54,
    "iso_alpha2": "PC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "PC",
    "name_en": "PC"
  },
  "pe": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 54,
    "iso_alpha2": "PE",
    "iso_alpha3": "PER",
    "iso_numeric": "604",
    "name_it": "Perù",
    "name_en": "Peru"
  },
  "pf": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 54,
    "iso_alpha2": "PF",
    "iso_alpha3": "PYF",
    "iso_numeric": "258",
    "name_it": "Polinesia Francese",
    "name_en": "French Polynesia"
  },
  "pg": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 54,
    "iso_alpha2": "PG",
    "iso_alpha3": "PNG",
    "iso_numeric": "598",
    "name_it": "Papua Nuova Guinea",
    "name_en": "Papua New Guinea"
  },
  "ph": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 54,
    "iso_alpha2": "PH",
    "iso_alpha3": "PHL",
    "iso_numeric": "608",
    "name_it": "Filippine",
    "name_en": "Philippines"
  },
  "pk": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 54,
    "iso_alpha2": "PK",
    "iso_alpha3": "PAK",
    "iso_numeric": "586",
    "name_it": "Pakistan",
    "name_en": "Pakistan"
  },
  "pl": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 72,
    "iso_alpha2": "PL",
    "iso_alpha3": "POL",
    "iso_numeric": "616",
    "name_it": "Polonia",
    "name_en": "Poland"
  },
  "pm": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 90,
    "iso_alpha2": "PM",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "PM",
    "name_en": "PM"
  },
  "pn": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 108,
    "iso_alpha2": "PN",
    "iso_alpha3": "PCN",
    "iso_numeric": "612",
    "name_it": "Isole Pitcairn",
    "name_en": "Pitcairn Islands"
  },
  "pr": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 126,
    "iso_alpha2": "PR",
    "iso_alpha3": "PRI",
    "iso_numeric": "630",
    "name_it": "Porto Rico",
    "name_en": "Puerto Rico"
  },
  "ps": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 144,
    "iso_alpha2": "PS",
    "iso_alpha3": "PSE",
    "iso_numeric": "275",
    "name_it": "Palestina",
    "name_en": "Palestinian Territories"
  },
  "pt": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 162,
    "iso_alpha2": "PT",
    "iso_alpha3": "PRT",
    "iso_numeric": "620",
    "name_it": "Portogallo",
    "name_en": "Portugal"
  },
  "pw": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 180,
    "iso_alpha2": "PW",
    "iso_alpha3": "PLW",
    "iso_numeric": "585",
    "name_it": "Palau",
    "name_en": "Palau"
  },
  "py": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 198,
    "iso_alpha2": "PY",
    "iso_alpha3": "PRY",
    "iso_numeric": "600",
    "name_it": "Paraguay",
    "name_en": "Paraguay"
  },
  "qa": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 216,
    "iso_alpha2": "QA",
    "iso_alpha3": "QAT",
    "iso_numeric": "634",
    "name_it": "Qatar",
    "name_en": "Qatar"
  },
  "re": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 234,
    "iso_alpha2": "RE",
    "iso_alpha3": "REU",
    "iso_numeric": "638",
    "name_it": "Réunion",
    "name_en": "Réunion"
  },
  "ro": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 72,
    "iso_alpha2": "RO",
    "iso_alpha3": "ROU",
    "iso_numeric": "642",
    "name_it": "Romania",
    "name_en": "Romania"
  },
  "rs": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 72,
    "iso_alpha2": "RS",
    "iso_alpha3": "SRB",
    "iso_numeric": "688",
    "name_it": "Serbia",
    "name_en": "Serbia"
  },
  "ru": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 72,
    "iso_alpha2": "RU",
    "iso_alpha3": "RUS",
    "iso_numeric": "643",
    "name_it": "Russia",
    "name_en": "Russia"
  },
  "rw": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 72,
    "iso_alpha2": "RW",
    "iso_alpha3": "RWA",
    "iso_numeric": "646",
    "name_it": "Ruanda",
    "name_en": "Ruanda"
  },
  "sa": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 72,
    "iso_alpha2": "SA",
    "iso_alpha3": "SAU",
    "iso_numeric": "682",
    "name_it": "Arabia Saudita",
    "name_en": "Saudi Arabia"
  },
  "sb": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 72,
    "iso_alpha2": "SB",
    "iso_alpha3": "SLB",
    "iso_numeric": "090",
    "name_it": "Isole Salomone",
    "name_en": "Solomon Islands"
  },
  "sc": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 72,
    "iso_alpha2": "SC",
    "iso_alpha3": "SYC",
    "iso_numeric": "690",
    "name_it": "Seychelles",
    "name_en": "Seychelles"
  },
  "sd": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 72,
    "iso_alpha2": "SD",
    "iso_alpha3": "SDN",
    "iso_numeric": "729",
    "name_it": "Sudan",
    "name_en": "Sudan"
  },
  "se": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 72,
    "iso_alpha2": "SE",
    "iso_alpha3": "SWE",
    "iso_numeric": "752",
    "name_it": "Svezia",
    "name_en": "Sweden"
  },
  "sg": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 90,
    "iso_alpha2": "SG",
    "iso_alpha3": "SGP",
    "iso_numeric": "702",
    "name_it": "Singapore",
    "name_en": "Singapore"
  },
  "sh": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 108,
    "iso_alpha2": "SH",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "SH",
    "name_en": "SH"
  },
  "sh-ac": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 126,
    "iso_alpha2": "SH-AC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "SH-AC",
    "name_en": "SH-AC"
  },
  "sh-hl": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 144,
    "iso_alpha2": "SH-HL",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "SH-HL",
    "name_en": "SH-HL"
  },
  "sh-ta": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 162,
    "iso_alpha2": "SH-TA",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "SH-TA",
    "name_en": "SH-TA"
  },
  "si": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 180,
    "iso_alpha2": "SI",
    "iso_alpha3": "SVN",
    "iso_numeric": "705",
    "name_it": "Slovenia",
    "name_en": "Slovenia"
  },
  "sj": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 198,
    "iso_alpha2": "SJ",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "SJ",
    "name_en": "SJ"
  },
  "sk": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 216,
    "iso_alpha2": "SK",
    "iso_alpha3": "SVK",
    "iso_numeric": "703",
    "name_it": "Slovacchia",
    "name_en": "Slovakia"
  },
  "sl": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 234,
    "iso_alpha2": "SL",
    "iso_alpha3": "SLE",
    "iso_numeric": "694",
    "name_it": "Sierra Leone",
    "name_en": "Sierra Leone"
  },
  "sm": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 90,
    "iso_alpha2": "SM",
    "iso_alpha3": "SMR",
    "iso_numeric": "674",
    "name_it": "San Marino",
    "name_en": "San Marino"
  },
  "sn": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 90,
    "iso_alpha2": "SN",
    "iso_alpha3": "SEN",
    "iso_numeric": "686",
    "name_it": "Senegal",
    "name_en": "Senegal"
  },
  "so": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 90,
    "iso_alpha2": "SO",
    "iso_alpha3": "SOM",
    "iso_numeric": "706",
    "name_it": "Somalia",
    "name_en": "Somalia"
  },
  "sr": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 90,
    "iso_alpha2": "SR",
    "iso_alpha3": "SUR",
    "iso_numeric": "740",
    "name_it": "Suriname",
    "name_en": "Suriname"
  },
  "ss": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 90,
    "iso_alpha2": "SS",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "SS",
    "name_en": "SS"
  },
  "st": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 90,
    "iso_alpha2": "ST",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "ST",
    "name_en": "ST"
  },
  "sv": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 90,
    "iso_alpha2": "SV",
    "iso_alpha3": "SLV",
    "iso_numeric": "222",
    "name_it": "El Salvador",
    "name_en": "El Salvador"
  },
  "sx": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 90,
    "iso_alpha2": "SX",
    "iso_alpha3": "SXM",
    "iso_numeric": "534",
    "name_it": "Sint Maarten",
    "name_en": "Sint Maarten"
  },
  "sy": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 108,
    "iso_alpha2": "SY",
    "iso_alpha3": "SYR",
    "iso_numeric": "760",
    "name_it": "Siria",
    "name_en": "Syria"
  },
  "sz": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 126,
    "iso_alpha2": "SZ",
    "iso_alpha3": "SWZ",
    "iso_numeric": "748",
    "name_it": "Eswatini",
    "name_en": "Eswatini"
  },
  "tc": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 144,
    "iso_alpha2": "TC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "TC",
    "name_en": "TC"
  },
  "td": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 162,
    "iso_alpha2": "TD",
    "iso_alpha3": "TCD",
    "iso_numeric": "148",
    "name_it": "Ciad",
    "name_en": "Chad"
  },
  "tf": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 180,
    "iso_alpha2": "TF",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "TF",
    "name_en": "TF"
  },
  "tg": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 198,
    "iso_alpha2": "TG",
    "iso_alpha3": "TGO",
    "iso_numeric": "768",
    "name_it": "Togo",
    "name_en": "Togo"
  },
  "th": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 216,
    "iso_alpha2": "TH",
    "iso_alpha3": "THA",
    "iso_numeric": "764",
    "name_it": "Thailandia",
    "name_en": "Thailand"
  },
  "tj": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 234,
    "iso_alpha2": "TJ",
    "iso_alpha3": "TJK",
    "iso_numeric": "762",
    "name_it": "Tagikistan",
    "name_en": "Tajikistan"
  },
  "tk": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 108,
    "iso_alpha2": "TK",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "TK",
    "name_en": "TK"
  },
  "tl": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 108,
    "iso_alpha2": "TL",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "TL",
    "name_en": "TL"
  },
  "tm": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 108,
    "iso_alpha2": "TM",
    "iso_alpha3": "TKM",
    "iso_numeric": "795",
    "name_it": "Turkmenistan",
    "name_en": "Turkmenistan"
  },
  "tn": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 108,
    "iso_alpha2": "TN",
    "iso_alpha3": "TUN",
    "iso_numeric": "788",
    "name_it": "Tunisia",
    "name_en": "Tunisia"
  },
  "to": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 108,
    "iso_alpha2": "TO",
    "iso_alpha3": "TON",
    "iso_numeric": "776",
    "name_it": "Tonga",
    "name_en": "Tonga"
  },
  "tr": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 108,
    "iso_alpha2": "TR",
    "iso_alpha3": "TUR",
    "iso_numeric": "792",
    "name_it": "Turchia",
    "name_en": "Turkey"
  },
  "tt": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 108,
    "iso_alpha2": "TT",
    "iso_alpha3": "TTO",
    "iso_numeric": "780",
    "name_it": "Trinidad e Tobago",
    "name_en": "Trinidad & Tobago"
  },
  "tv": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 126,
    "iso_alpha2": "TV",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "TV",
    "name_en": "TV"
  },
  "tw": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 144,
    "iso_alpha2": "TW",
    "iso_alpha3": "TWN",
    "iso_numeric": "158",
    "name_it": "Taiwan",
    "name_en": "Taiwan"
  },
  "tz": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 162,
    "iso_alpha2": "TZ",
    "iso_alpha3": "TZA",
    "iso_numeric": "834",
    "name_it": "Tanzania",
    "name_en": "Tanzania"
  },
  "ua": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 180,
    "iso_alpha2": "UA",
    "iso_alpha3": "UKR",
    "iso_numeric": "804",
    "name_it": "Ucraina",
    "name_en": "Ukraine"
  },
  "ug": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 198,
    "iso_alpha2": "UG",
    "iso_alpha3": "UGA",
    "iso_numeric": "800",
    "name_it": "Uganda",
    "name_en": "Uganda"
  },
  "um": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 216,
    "iso_alpha2": "UM",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "UM",
    "name_en": "UM"
  },
  "un": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 234,
    "iso_alpha2": "UN",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "UN",
    "name_en": "UN"
  },
  "us": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 126,
    "iso_alpha2": "US",
    "iso_alpha3": "USA",
    "iso_numeric": "840",
    "name_it": "Stati Uniti",
    "name_en": "United States"
  },
  "uy": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 126,
    "iso_alpha2": "UY",
    "iso_alpha3": "URY",
    "iso_numeric": "858",
    "name_it": "Uruguay",
    "name_en": "Uruguay"
  },
  "uz": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 126,
    "iso_alpha2": "UZ",
    "iso_alpha3": "UZB",
    "iso_numeric": "860",
    "name_it": "Uzbekistan",
    "name_en": "Uzbekistan"
  },
  "va": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 126,
    "iso_alpha2": "VA",
    "iso_alpha3": "VAT",
    "iso_numeric": "336",
    "name_it": "Città del Vaticano",
    "name_en": "Vatican City"
  },
  "vc": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 126,
    "iso_alpha2": "VC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "VC",
    "name_en": "VC"
  },
  "ve": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 126,
    "iso_alpha2": "VE",
    "iso_alpha3": "VEN",
    "iso_numeric": "862",
    "name_it": "Venezuela",
    "name_en": "Venezuela"
  },
  "vg": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 144,
    "iso_alpha2": "VG",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "VG",
    "name_en": "VG"
  },
  "vi": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 162,
    "iso_alpha2": "VI",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "VI",
    "name_en": "VI"
  },
  "vn": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 180,
    "iso_alpha2": "VN",
    "iso_alpha3": "VNM",
    "iso_numeric": "704",
    "name_it": "Vietnam",
    "name_en": "Vietnam"
  },
  "vu": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 198,
    "iso_alpha2": "VU",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "VU",
    "name_en": "VU"
  },
  "wf": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 216,
    "iso_alpha2": "WF",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "WF",
    "name_en": "WF"
  },
  "ws": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 234,
    "iso_alpha2": "WS",
    "iso_alpha3": "WSM",
    "iso_numeric": "882",
    "name_it": "Samoa",
    "name_en": "Samoa"
  },
  "xk": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 144,
    "iso_alpha2": "XK",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "XK",
    "name_en": "XK"
  },
  "xx": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 144,
    "iso_alpha2": "XX",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "XX",
    "name_en": "XX"
  },
  "ye": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 144,
    "iso_alpha2": "YE",
    "iso_alpha3": "YEM",
    "iso_numeric": "887",
    "name_it": "Yemen",
    "name_en": "Yemen"
  },
  "yt": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 144,
    "iso_alpha2": "YT",
    "iso_alpha3": "MYT",
    "iso_numeric": "175",
    "name_it": "Mayotte",
    "name_en": "Mayotte"
  },
  "za": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 144,
    "iso_alpha2": "ZA",
    "iso_alpha3": "ZAF",
    "iso_numeric": "710",
    "name_it": "Sudafrica",
    "name_en": "South Africa"
  },
  "zm": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 162,
    "iso_alpha2": "ZM",
    "iso_alpha3": "ZMB",
    "iso_numeric": "894",
    "name_it": "Zambia",
    "name_en": "Zambia"
  },
  "zw": {
    "height": 18,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 180,
    "iso_alpha2": "ZW",
    "iso_alpha3": "ZWE",
    "iso_numeric": "716",
    "name_it": "Zimbabwe",
    "name_en": "Zimbabwe"
  }
}
```

## `resources/sprite@2x.json`

Nota: File JSON: verificare dal contenuto se è configurazione o dato.

```text
{
  "ad": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 0,
    "iso_alpha2": "AD",
    "iso_alpha3": "AND",
    "iso_numeric": "020",
    "name_it": "Andorra",
    "name_en": "Andorra"
  },
  "ae": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 36,
    "iso_alpha2": "AE",
    "iso_alpha3": "ARE",
    "iso_numeric": "784",
    "name_it": "Emirati Arabi Uniti",
    "name_en": "United Arab Emirates"
  },
  "af": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 72,
    "iso_alpha2": "AF",
    "iso_alpha3": "AFG",
    "iso_numeric": "004",
    "name_it": "Afghanistan",
    "name_en": "Afghanistan"
  },
  "ag": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 108,
    "iso_alpha2": "AG",
    "iso_alpha3": "ATG",
    "iso_numeric": "028",
    "name_it": "Antigua e Barbuda",
    "name_en": "Antigua & Barbuda"
  },
  "ai": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 144,
    "iso_alpha2": "AI",
    "iso_alpha3": "AIA",
    "iso_numeric": "008",
    "name_it": "Anguilla",
    "name_en": "Anguilla"
  },
  "al": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 180,
    "iso_alpha2": "AL",
    "iso_alpha3": "ALB",
    "iso_numeric": "008",
    "name_it": "Albania",
    "name_en": "Albania"
  },
  "am": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 216,
    "iso_alpha2": "AM",
    "iso_alpha3": "ARM",
    "iso_numeric": "051",
    "name_it": "Armenia",
    "name_en": "Armenia"
  },
  "ao": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 252,
    "iso_alpha2": "AO",
    "iso_alpha3": "AGO",
    "iso_numeric": "024",
    "name_it": "Angola",
    "name_en": "Angola"
  },
  "aq": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 288,
    "iso_alpha2": "AQ",
    "iso_alpha3": "ATA",
    "iso_numeric": "010",
    "name_it": "Antartide",
    "name_en": "Antarctica"
  },
  "ar": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 324,
    "iso_alpha2": "AR",
    "iso_alpha3": "ARG",
    "iso_numeric": "032",
    "name_it": "Argentina",
    "name_en": "Argentina"
  },
  "arab": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 360,
    "iso_alpha2": "ARAB",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "ARAB",
    "name_en": "ARAB"
  },
  "as": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 396,
    "iso_alpha2": "AS",
    "iso_alpha3": "ASM",
    "iso_numeric": "016",
    "name_it": "Samoa Americane",
    "name_en": "American Samoa"
  },
  "asean": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 432,
    "iso_alpha2": "ASEAN",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "ASEAN",
    "name_en": "ASEAN"
  },
  "at": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 468,
    "iso_alpha2": "AT",
    "iso_alpha3": "AUT",
    "iso_numeric": "040",
    "name_it": "Austria",
    "name_en": "Austria"
  },
  "au": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 0,
    "iso_alpha2": "AU",
    "iso_alpha3": "AUS",
    "iso_numeric": "036",
    "name_it": "Australia",
    "name_en": "Australia"
  },
  "aw": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 36,
    "iso_alpha2": "AW",
    "iso_alpha3": "ABW",
    "iso_numeric": "053",
    "name_it": "Aruba",
    "name_en": "Aruba"
  },
  "ax": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 72,
    "iso_alpha2": "AX",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "AX",
    "name_en": "AX"
  },
  "az": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 108,
    "iso_alpha2": "AZ",
    "iso_alpha3": "AZE",
    "iso_numeric": "031",
    "name_it": "Azerbaigian",
    "name_en": "Azerbaijan"
  },
  "ba": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 144,
    "iso_alpha2": "BA",
    "iso_alpha3": "BIH",
    "iso_numeric": "070",
    "name_it": "Bosnia ed Erzegovina",
    "name_en": "Bosnia & Herzegovina"
  },
  "bb": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 180,
    "iso_alpha2": "BB",
    "iso_alpha3": "BRB",
    "iso_numeric": "052",
    "name_it": "Barbados",
    "name_en": "Barbados"
  },
  "bd": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 216,
    "iso_alpha2": "BD",
    "iso_alpha3": "BGD",
    "iso_numeric": "050",
    "name_it": "Bangladesh",
    "name_en": "Bangladesh"
  },
  "be": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 252,
    "iso_alpha2": "BE",
    "iso_alpha3": "BEL",
    "iso_numeric": "056",
    "name_it": "Belgio",
    "name_en": "Belgium"
  },
  "bf": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 288,
    "iso_alpha2": "BF",
    "iso_alpha3": "BFA",
    "iso_numeric": "854",
    "name_it": "Burkina Faso",
    "name_en": "Burkina Faso"
  },
  "bg": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 324,
    "iso_alpha2": "BG",
    "iso_alpha3": "BGR",
    "iso_numeric": "100",
    "name_it": "Bulgaria",
    "name_en": "Bulgaria"
  },
  "bh": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 360,
    "iso_alpha2": "BH",
    "iso_alpha3": "BHR",
    "iso_numeric": "048",
    "name_it": "Bahrein",
    "name_en": "Bahrain"
  },
  "bi": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 396,
    "iso_alpha2": "BI",
    "iso_alpha3": "BDI",
    "iso_numeric": "108",
    "name_it": "Burundi",
    "name_en": "Burundi"
  },
  "bj": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 432,
    "iso_alpha2": "BJ",
    "iso_alpha3": "BEN",
    "iso_numeric": "204",
    "name_it": "Benin",
    "name_en": "Benin"
  },
  "bl": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 468,
    "iso_alpha2": "BL",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "BL",
    "name_en": "BL"
  },
  "bm": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 0,
    "iso_alpha2": "BM",
    "iso_alpha3": "BMU",
    "iso_numeric": "060",
    "name_it": "Bermuda",
    "name_en": "Bermuda"
  },
  "bn": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 36,
    "iso_alpha2": "BN",
    "iso_alpha3": "BRN",
    "iso_numeric": "096",
    "name_it": "Brunei",
    "name_en": "Brunei"
  },
  "bo": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 72,
    "iso_alpha2": "BO",
    "iso_alpha3": "BOL",
    "iso_numeric": "068",
    "name_it": "Bolivia",
    "name_en": "Bolivia"
  },
  "bq": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 108,
    "iso_alpha2": "BQ",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "BQ",
    "name_en": "BQ"
  },
  "br": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 144,
    "iso_alpha2": "BR",
    "iso_alpha3": "BRA",
    "iso_numeric": "076",
    "name_it": "Brasile",
    "name_en": "Brazil"
  },
  "bs": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 180,
    "iso_alpha2": "BS",
    "iso_alpha3": "BHS",
    "iso_numeric": "044",
    "name_it": "Bahamas",
    "name_en": "Bahamas"
  },
  "bt": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 216,
    "iso_alpha2": "BT",
    "iso_alpha3": "BTN",
    "iso_numeric": "064",
    "name_it": "Bhutan",
    "name_en": "Bhutan"
  },
  "bv": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 252,
    "iso_alpha2": "BV",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "BV",
    "name_en": "BV"
  },
  "bw": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 288,
    "iso_alpha2": "BW",
    "iso_alpha3": "BWA",
    "iso_numeric": "072",
    "name_it": "Botswana",
    "name_en": "Botswana"
  },
  "by": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 324,
    "iso_alpha2": "BY",
    "iso_alpha3": "BLR",
    "iso_numeric": "112",
    "name_it": "Bielorussia",
    "name_en": "Belarus"
  },
  "bz": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 360,
    "iso_alpha2": "BZ",
    "iso_alpha3": "BLZ",
    "iso_numeric": "084",
    "name_it": "Belize",
    "name_en": "Belize"
  },
  "ca": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 396,
    "iso_alpha2": "CA",
    "iso_alpha3": "CAN",
    "iso_numeric": "124",
    "name_it": "Canada",
    "name_en": "Canada"
  },
  "cc": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 432,
    "iso_alpha2": "CC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "CC",
    "name_en": "CC"
  },
  "cd": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 468,
    "iso_alpha2": "CD",
    "iso_alpha3": "COD",
    "iso_numeric": "180",
    "name_it": "Congo-Kinshasa",
    "name_en": "Congo - Kinshasa"
  },
  "cefta": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 0,
    "iso_alpha2": "CEFTA",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "CEFTA",
    "name_en": "CEFTA"
  },
  "cf": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 36,
    "iso_alpha2": "CF",
    "iso_alpha3": "CAF",
    "iso_numeric": "140",
    "name_it": "Repubblica Centrafricana",
    "name_en": "Central African Republic"
  },
  "cg": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 72,
    "iso_alpha2": "CG",
    "iso_alpha3": "COG",
    "iso_numeric": "178",
    "name_it": "Congo-Brazzaville",
    "name_en": "Congo - Brazzaville"
  },
  "ch": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 108,
    "iso_alpha2": "CH",
    "iso_alpha3": "CHE",
    "iso_numeric": "756",
    "name_it": "Svizzera",
    "name_en": "Switzerland"
  },
  "ci": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 144,
    "iso_alpha2": "CI",
    "iso_alpha3": "CIV",
    "iso_numeric": "384",
    "name_it": "Costa d'Avorio",
    "name_en": "Côte d’Ivoire"
  },
  "ck": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 180,
    "iso_alpha2": "CK",
    "iso_alpha3": "COK",
    "iso_numeric": "184",
    "name_it": "Isole Cook",
    "name_en": "Cook Islands"
  },
  "cl": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 216,
    "iso_alpha2": "CL",
    "iso_alpha3": "CHL",
    "iso_numeric": "152",
    "name_it": "Cile",
    "name_en": "Chile"
  },
  "cm": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 252,
    "iso_alpha2": "CM",
    "iso_alpha3": "CMR",
    "iso_numeric": "120",
    "name_it": "Camerun",
    "name_en": "Cameroon"
  },
  "cn": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 288,
    "iso_alpha2": "CN",
    "iso_alpha3": "CHN",
    "iso_numeric": "156",
    "name_it": "Cina",
    "name_en": "China"
  },
  "co": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 324,
    "iso_alpha2": "CO",
    "iso_alpha3": "COL",
    "iso_numeric": "170",
    "name_it": "Colombia",
    "name_en": "Colombia"
  },
  "cp": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 360,
    "iso_alpha2": "CP",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "CP",
    "name_en": "CP"
  },
  "cr": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 396,
    "iso_alpha2": "CR",
    "iso_alpha3": "CRI",
    "iso_numeric": "188",
    "name_it": "Costa Rica",
    "name_en": "Costa Rica"
  },
  "cu": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 432,
    "iso_alpha2": "CU",
    "iso_alpha3": "CUB",
    "iso_numeric": "192",
    "name_it": "Cuba",
    "name_en": "Cuba"
  },
  "cv": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 468,
    "iso_alpha2": "CV",
    "iso_alpha3": "CPV",
    "iso_numeric": "132",
    "name_it": "Capo Verde",
    "name_en": "Cape Verde"
  },
  "cw": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 0,
    "iso_alpha2": "CW",
    "iso_alpha3": "CUW",
    "iso_numeric": "531",
    "name_it": "Curaçao",
    "name_en": "Curaçao"
  },
  "cx": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 36,
    "iso_alpha2": "CX",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "CX",
    "name_en": "CX"
  },
  "cy": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 72,
    "iso_alpha2": "CY",
    "iso_alpha3": "CYP",
    "iso_numeric": "196",
    "name_it": "Cipro",
    "name_en": "Cyprus"
  },
  "cz": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 108,
    "iso_alpha2": "CZ",
    "iso_alpha3": "CZE",
    "iso_numeric": "203",
    "name_it": "Cechia",
    "name_en": "Czechia"
  },
  "de": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 144,
    "iso_alpha2": "DE",
    "iso_alpha3": "DEU",
    "iso_numeric": "276",
    "name_it": "Germania",
    "name_en": "Germany"
  },
  "dg": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 180,
    "iso_alpha2": "DG",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "DG",
    "name_en": "DG"
  },
  "dj": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 216,
    "iso_alpha2": "DJ",
    "iso_alpha3": "DJI",
    "iso_numeric": "262",
    "name_it": "Gibuti",
    "name_en": "Djibouti"
  },
  "dk": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 252,
    "iso_alpha2": "DK",
    "iso_alpha3": "DNK",
    "iso_numeric": "208",
    "name_it": "Danimarca",
    "name_en": "Denmark"
  },
  "dm": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 288,
    "iso_alpha2": "DM",
    "iso_alpha3": "DMA",
    "iso_numeric": "212",
    "name_it": "Dominica",
    "name_en": "Dominica"
  },
  "do": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 324,
    "iso_alpha2": "DO",
    "iso_alpha3": "DOM",
    "iso_numeric": "214",
    "name_it": "Repubblica Dominicana",
    "name_en": "Dominican Republic"
  },
  "dz": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 360,
    "iso_alpha2": "DZ",
    "iso_alpha3": "DZA",
    "iso_numeric": "012",
    "name_it": "Algeria",
    "name_en": "Algeria"
  },
  "eac": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 396,
    "iso_alpha2": "EAC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "EAC",
    "name_en": "EAC"
  },
  "ec": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 432,
    "iso_alpha2": "EC",
    "iso_alpha3": "ECU",
    "iso_numeric": "218",
    "name_it": "Ecuador",
    "name_en": "Ecuador"
  },
  "ee": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 468,
    "iso_alpha2": "EE",
    "iso_alpha3": "EST",
    "iso_numeric": "233",
    "name_it": "Estonia",
    "name_en": "Estonia"
  },
  "eg": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 0,
    "iso_alpha2": "EG",
    "iso_alpha3": "EGY",
    "iso_numeric": "818",
    "name_it": "Egitto",
    "name_en": "Egypt"
  },
  "eh": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 36,
    "iso_alpha2": "EH",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "EH",
    "name_en": "EH"
  },
  "er": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 72,
    "iso_alpha2": "ER",
    "iso_alpha3": "ERI",
    "iso_numeric": "232",
    "name_it": "Eritrea",
    "name_en": "Eritrea"
  },
  "es": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 108,
    "iso_alpha2": "ES",
    "iso_alpha3": "ESP",
    "iso_numeric": "724",
    "name_it": "Spagna",
    "name_en": "Spain"
  },
  "es-ct": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 144,
    "iso_alpha2": "ES-CT",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "ES-CT",
    "name_en": "ES-CT"
  },
  "es-ga": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 180,
    "iso_alpha2": "ES-GA",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "ES-GA",
    "name_en": "ES-GA"
  },
  "es-pv": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 216,
    "iso_alpha2": "ES-PV",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "ES-PV",
    "name_en": "ES-PV"
  },
  "et": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 252,
    "iso_alpha2": "ET",
    "iso_alpha3": "ETH",
    "iso_numeric": "231",
    "name_it": "Etiopia",
    "name_en": "Ethiopia"
  },
  "eu": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 288,
    "iso_alpha2": "EU",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "EU",
    "name_en": "EU"
  },
  "fi": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 324,
    "iso_alpha2": "FI",
    "iso_alpha3": "FIN",
    "iso_numeric": "246",
    "name_it": "Finlandia",
    "name_en": "Finland"
  },
  "fj": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 360,
    "iso_alpha2": "FJ",
    "iso_alpha3": "FJI",
    "iso_numeric": "242",
    "name_it": "Figi",
    "name_en": "Fiji"
  },
  "fk": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 396,
    "iso_alpha2": "FK",
    "iso_alpha3": "FLK",
    "iso_numeric": "238",
    "name_it": "Isole Falkland",
    "name_en": "Falkland Islands"
  },
  "fm": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 432,
    "iso_alpha2": "FM",
    "iso_alpha3": "FSM",
    "iso_numeric": "583",
    "name_it": "Micronesia",
    "name_en": "Micronesia"
  },
  "fo": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 468,
    "iso_alpha2": "FO",
    "iso_alpha3": "FRO",
    "iso_numeric": "234",
    "name_it": "Isole Fær Øer",
    "name_en": "Faroe Islands"
  },
  "fr": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 0,
    "iso_alpha2": "FR",
    "iso_alpha3": "FRA",
    "iso_numeric": "250",
    "name_it": "Francia",
    "name_en": "France"
  },
  "ga": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 36,
    "iso_alpha2": "GA",
    "iso_alpha3": "GAB",
    "iso_numeric": "266",
    "name_it": "Gabon",
    "name_en": "Gabon"
  },
  "gb": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 72,
    "iso_alpha2": "GB",
    "iso_alpha3": "GBR",
    "iso_numeric": "826",
    "name_it": "Regno Unito",
    "name_en": "United Kingdom"
  },
  "gb-eng": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 108,
    "iso_alpha2": "GB-ENG",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "GB-ENG",
    "name_en": "GB-ENG"
  },
  "gb-nir": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 144,
    "iso_alpha2": "GB-NIR",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "GB-NIR",
    "name_en": "GB-NIR"
  },
  "gb-sct": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 180,
    "iso_alpha2": "GB-SCT",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "GB-SCT",
    "name_en": "GB-SCT"
  },
  "gb-wls": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 216,
    "iso_alpha2": "GB-WLS",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "GB-WLS",
    "name_en": "GB-WLS"
  },
  "gd": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 252,
    "iso_alpha2": "GD",
    "iso_alpha3": "GRD",
    "iso_numeric": "308",
    "name_it": "Grenada",
    "name_en": "Grenada"
  },
  "ge": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 288,
    "iso_alpha2": "GE",
    "iso_alpha3": "GEO",
    "iso_numeric": "268",
    "name_it": "Georgia",
    "name_en": "Georgia"
  },
  "gf": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 324,
    "iso_alpha2": "GF",
    "iso_alpha3": "GUF",
    "iso_numeric": "254",
    "name_it": "Guyana Francese",
    "name_en": "French Guiana"
  },
  "gg": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 360,
    "iso_alpha2": "GG",
    "iso_alpha3": "GGY",
    "iso_numeric": "831",
    "name_it": "Guernsey",
    "name_en": "Guernsey"
  },
  "gh": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 396,
    "iso_alpha2": "GH",
    "iso_alpha3": "GHA",
    "iso_numeric": "288",
    "name_it": "Ghana",
    "name_en": "Ghana"
  },
  "gi": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 432,
    "iso_alpha2": "GI",
    "iso_alpha3": "GIB",
    "iso_numeric": "292",
    "name_it": "Gibilterra",
    "name_en": "Gibraltar"
  },
  "gl": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 468,
    "iso_alpha2": "GL",
    "iso_alpha3": "GRL",
    "iso_numeric": "304",
    "name_it": "Groenlandia",
    "name_en": "Greenland"
  },
  "gm": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 0,
    "iso_alpha2": "GM",
    "iso_alpha3": "GMB",
    "iso_numeric": "270",
    "name_it": "Gambia",
    "name_en": "Gambia"
  },
  "gn": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 36,
    "iso_alpha2": "GN",
    "iso_alpha3": "GIN",
    "iso_numeric": "324",
    "name_it": "Guinea",
    "name_en": "Guinea"
  },
  "gp": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 72,
    "iso_alpha2": "GP",
    "iso_alpha3": "GLP",
    "iso_numeric": "312",
    "name_it": "Guadalupa",
    "name_en": "Guadeloupe"
  },
  "gq": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 108,
    "iso_alpha2": "GQ",
    "iso_alpha3": "GNQ",
    "iso_numeric": "226",
    "name_it": "Guinea Equatoriale",
    "name_en": "Equatorial Guinea"
  },
  "gr": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 144,
    "iso_alpha2": "GR",
    "iso_alpha3": "GRC",
    "iso_numeric": "300",
    "name_it": "Grecia",
    "name_en": "Greece"
  },
  "gs": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 180,
    "iso_alpha2": "GS",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "GS",
    "name_en": "GS"
  },
  "gt": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 216,
    "iso_alpha2": "GT",
    "iso_alpha3": "GTM",
    "iso_numeric": "320",
    "name_it": "Guatemala",
    "name_en": "Guatemala"
  },
  "gu": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 252,
    "iso_alpha2": "GU",
    "iso_alpha3": "GUM",
    "iso_numeric": "316",
    "name_it": "Guam",
    "name_en": "Guam"
  },
  "gw": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 288,
    "iso_alpha2": "GW",
    "iso_alpha3": "GNB",
    "iso_numeric": "624",
    "name_it": "Guinea-Bissau",
    "name_en": "Guinea-Bissau"
  },
  "gy": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 324,
    "iso_alpha2": "GY",
    "iso_alpha3": "GUY",
    "iso_numeric": "328",
    "name_it": "Guyana",
    "name_en": "Guyana"
  },
  "hk": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 360,
    "iso_alpha2": "HK",
    "iso_alpha3": "HKG",
    "iso_numeric": "344",
    "name_it": "Hong Kong",
    "name_en": "Hong Kong SAR China"
  },
  "hm": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 396,
    "iso_alpha2": "HM",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "HM",
    "name_en": "HM"
  },
  "hn": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 432,
    "iso_alpha2": "HN",
    "iso_alpha3": "HND",
    "iso_numeric": "340",
    "name_it": "Honduras",
    "name_en": "Honduras"
  },
  "hr": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 468,
    "iso_alpha2": "HR",
    "iso_alpha3": "HRV",
    "iso_numeric": "191",
    "name_it": "Croazia",
    "name_en": "Croatia"
  },
  "ht": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 0,
    "iso_alpha2": "HT",
    "iso_alpha3": "HTI",
    "iso_numeric": "332",
    "name_it": "Haiti",
    "name_en": "Haiti"
  },
  "hu": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 0,
    "iso_alpha2": "HU",
    "iso_alpha3": "HUN",
    "iso_numeric": "348",
    "name_it": "Ungheria",
    "name_en": "Hungary"
  },
  "ic": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 0,
    "iso_alpha2": "IC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "IC",
    "name_en": "IC"
  },
  "id": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 0,
    "iso_alpha2": "ID",
    "iso_alpha3": "IDN",
    "iso_numeric": "360",
    "name_it": "Indonesia",
    "name_en": "Indonesia"
  },
  "ie": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 0,
    "iso_alpha2": "IE",
    "iso_alpha3": "IRL",
    "iso_numeric": "372",
    "name_it": "Irlanda",
    "name_en": "Ireland"
  },
  "il": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 0,
    "iso_alpha2": "IL",
    "iso_alpha3": "ISR",
    "iso_numeric": "376",
    "name_it": "Israele",
    "name_en": "Israel"
  },
  "im": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 0,
    "iso_alpha2": "IM",
    "iso_alpha3": "IMN",
    "iso_numeric": "833",
    "name_it": "Isola di Man",
    "name_en": "Isle of Man"
  },
  "in": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 0,
    "iso_alpha2": "IN",
    "iso_alpha3": "IND",
    "iso_numeric": "356",
    "name_it": "India",
    "name_en": "India"
  },
  "io": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 0,
    "iso_alpha2": "IO",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "IO",
    "name_en": "IO"
  },
  "iq": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 0,
    "iso_alpha2": "IQ",
    "iso_alpha3": "IRQ",
    "iso_numeric": "368",
    "name_it": "Iraq",
    "name_en": "Iraq"
  },
  "ir": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 0,
    "iso_alpha2": "IR",
    "iso_alpha3": "IRN",
    "iso_numeric": "364",
    "name_it": "Iran",
    "name_en": "Iran"
  },
  "is": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 0,
    "iso_alpha2": "IS",
    "iso_alpha3": "ISL",
    "iso_numeric": "352",
    "name_it": "Islanda",
    "name_en": "Iceland"
  },
  "it": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 0,
    "iso_alpha2": "IT",
    "iso_alpha3": "ITA",
    "iso_numeric": "380",
    "name_it": "Italia",
    "name_en": "Italy"
  },
  "je": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 36,
    "iso_alpha2": "JE",
    "iso_alpha3": "JEY",
    "iso_numeric": "832",
    "name_it": "Jersey",
    "name_en": "Jersey"
  },
  "jm": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 72,
    "iso_alpha2": "JM",
    "iso_alpha3": "JAM",
    "iso_numeric": "388",
    "name_it": "Giamaica",
    "name_en": "Jamaica"
  },
  "jo": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 108,
    "iso_alpha2": "JO",
    "iso_alpha3": "JOR",
    "iso_numeric": "400",
    "name_it": "Giordania",
    "name_en": "Jordan"
  },
  "jp": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 144,
    "iso_alpha2": "JP",
    "iso_alpha3": "JPN",
    "iso_numeric": "392",
    "name_it": "Giappone",
    "name_en": "Japan"
  },
  "ke": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 180,
    "iso_alpha2": "KE",
    "iso_alpha3": "KEN",
    "iso_numeric": "404",
    "name_it": "Kenya",
    "name_en": "Kenya"
  },
  "kg": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 216,
    "iso_alpha2": "KG",
    "iso_alpha3": "KGZ",
    "iso_numeric": "417",
    "name_it": "Kirghizistan",
    "name_en": "Kyrgyzstan"
  },
  "kh": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 252,
    "iso_alpha2": "KH",
    "iso_alpha3": "KHM",
    "iso_numeric": "116",
    "name_it": "Cambogia",
    "name_en": "Cambodia"
  },
  "ki": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 288,
    "iso_alpha2": "KI",
    "iso_alpha3": "KIR",
    "iso_numeric": "296",
    "name_it": "Kiribati",
    "name_en": "Kiribati"
  },
  "km": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 324,
    "iso_alpha2": "KM",
    "iso_alpha3": "COM",
    "iso_numeric": "174",
    "name_it": "Comore",
    "name_en": "Comoros"
  },
  "kn": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 360,
    "iso_alpha2": "KN",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "KN",
    "name_en": "KN"
  },
  "kp": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 396,
    "iso_alpha2": "KP",
    "iso_alpha3": "PRK",
    "iso_numeric": "408",
    "name_it": "Corea del Nord",
    "name_en": "North Korea"
  },
  "kr": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 432,
    "iso_alpha2": "KR",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "KR",
    "name_en": "KR"
  },
  "kw": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 468,
    "iso_alpha2": "KW",
    "iso_alpha3": "KWT",
    "iso_numeric": "414",
    "name_it": "Kuwait",
    "name_en": "Kuwait"
  },
  "ky": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 36,
    "iso_alpha2": "KY",
    "iso_alpha3": "CYM",
    "iso_numeric": "136",
    "name_it": "Isole Cayman",
    "name_en": "Cayman Islands"
  },
  "kz": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 36,
    "iso_alpha2": "KZ",
    "iso_alpha3": "KAZ",
    "iso_numeric": "398",
    "name_it": "Kazakistan",
    "name_en": "Kazakhstan"
  },
  "la": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 36,
    "iso_alpha2": "LA",
    "iso_alpha3": "LAO",
    "iso_numeric": "418",
    "name_it": "Laos",
    "name_en": "Laos"
  },
  "lb": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 36,
    "iso_alpha2": "LB",
    "iso_alpha3": "LBN",
    "iso_numeric": "422",
    "name_it": "Libano",
    "name_en": "Lebanon"
  },
  "lc": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 36,
    "iso_alpha2": "LC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "LC",
    "name_en": "LC"
  },
  "li": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 36,
    "iso_alpha2": "LI",
    "iso_alpha3": "LIE",
    "iso_numeric": "438",
    "name_it": "Liechtenstein",
    "name_en": "Liechtenstein"
  },
  "lk": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 36,
    "iso_alpha2": "LK",
    "iso_alpha3": "LKA",
    "iso_numeric": "144",
    "name_it": "Sri Lanka",
    "name_en": "Sri Lanka"
  },
  "lr": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 36,
    "iso_alpha2": "LR",
    "iso_alpha3": "LBR",
    "iso_numeric": "430",
    "name_it": "Liberia",
    "name_en": "Liberia"
  },
  "ls": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 36,
    "iso_alpha2": "LS",
    "iso_alpha3": "LSO",
    "iso_numeric": "426",
    "name_it": "Lesotho",
    "name_en": "Lesotho"
  },
  "lt": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 36,
    "iso_alpha2": "LT",
    "iso_alpha3": "LTU",
    "iso_numeric": "440",
    "name_it": "Lituania",
    "name_en": "Lithuania"
  },
  "lu": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 36,
    "iso_alpha2": "LU",
    "iso_alpha3": "LUX",
    "iso_numeric": "442",
    "name_it": "Lussemburgo",
    "name_en": "Luxembourg"
  },
  "lv": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 36,
    "iso_alpha2": "LV",
    "iso_alpha3": "LVA",
    "iso_numeric": "428",
    "name_it": "Lettonia",
    "name_en": "Latvia"
  },
  "ly": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 72,
    "iso_alpha2": "LY",
    "iso_alpha3": "LBY",
    "iso_numeric": "434",
    "name_it": "Libia",
    "name_en": "Libya"
  },
  "ma": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 108,
    "iso_alpha2": "MA",
    "iso_alpha3": "MAR",
    "iso_numeric": "504",
    "name_it": "Marocco",
    "name_en": "Morocco"
  },
  "mc": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 144,
    "iso_alpha2": "MC",
    "iso_alpha3": "MCO",
    "iso_numeric": "492",
    "name_it": "Monaco",
    "name_en": "Monaco"
  },
  "md": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 180,
    "iso_alpha2": "MD",
    "iso_alpha3": "MDA",
    "iso_numeric": "498",
    "name_it": "Moldavia",
    "name_en": "Moldova"
  },
  "me": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 216,
    "iso_alpha2": "ME",
    "iso_alpha3": "MNE",
    "iso_numeric": "499",
    "name_it": "Montenegro",
    "name_en": "Montenegro"
  },
  "mf": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 252,
    "iso_alpha2": "MF",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "MF",
    "name_en": "MF"
  },
  "mg": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 288,
    "iso_alpha2": "MG",
    "iso_alpha3": "MDG",
    "iso_numeric": "450",
    "name_it": "Madagascar",
    "name_en": "Madagascar"
  },
  "mh": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 324,
    "iso_alpha2": "MH",
    "iso_alpha3": "MHL",
    "iso_numeric": "584",
    "name_it": "Isole Marshall",
    "name_en": "Marshall Islands"
  },
  "mk": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 360,
    "iso_alpha2": "MK",
    "iso_alpha3": "MKD",
    "iso_numeric": "807",
    "name_it": "Macedonia del Nord",
    "name_en": "North Macedonia"
  },
  "ml": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 396,
    "iso_alpha2": "ML",
    "iso_alpha3": "MLI",
    "iso_numeric": "466",
    "name_it": "Mali",
    "name_en": "Mali"
  },
  "mm": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 432,
    "iso_alpha2": "MM",
    "iso_alpha3": "MMR",
    "iso_numeric": "104",
    "name_it": "Myanmar",
    "name_en": "Myanmar (Burma)"
  },
  "mn": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 468,
    "iso_alpha2": "MN",
    "iso_alpha3": "MNG",
    "iso_numeric": "496",
    "name_it": "Mongolia",
    "name_en": "Mongolia"
  },
  "mo": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 72,
    "iso_alpha2": "MO",
    "iso_alpha3": "MAC",
    "iso_numeric": "446",
    "name_it": "Macao",
    "name_en": "Macao SAR China"
  },
  "mp": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 72,
    "iso_alpha2": "MP",
    "iso_alpha3": "MNP",
    "iso_numeric": "580",
    "name_it": "Isole Marianne Settentrionali",
    "name_en": "Northern Mariana Islands"
  },
  "mq": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 72,
    "iso_alpha2": "MQ",
    "iso_alpha3": "MTQ",
    "iso_numeric": "474",
    "name_it": "Martinica",
    "name_en": "Martinique"
  },
  "mr": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 72,
    "iso_alpha2": "MR",
    "iso_alpha3": "MRT",
    "iso_numeric": "478",
    "name_it": "Mauritania",
    "name_en": "Mauritania"
  },
  "ms": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 72,
    "iso_alpha2": "MS",
    "iso_alpha3": "MSR",
    "iso_numeric": "500",
    "name_it": "Montserrat",
    "name_en": "Montserrat"
  },
  "mt": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 72,
    "iso_alpha2": "MT",
    "iso_alpha3": "MLT",
    "iso_numeric": "470",
    "name_it": "Malta",
    "name_en": "Malta"
  },
  "mu": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 72,
    "iso_alpha2": "MU",
    "iso_alpha3": "MUS",
    "iso_numeric": "480",
    "name_it": "Mauritius",
    "name_en": "Mauritius"
  },
  "mv": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 72,
    "iso_alpha2": "MV",
    "iso_alpha3": "MDV",
    "iso_numeric": "462",
    "name_it": "Maldive",
    "name_en": "Maldives"
  },
  "mw": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 72,
    "iso_alpha2": "MW",
    "iso_alpha3": "MWI",
    "iso_numeric": "454",
    "name_it": "Malawi",
    "name_en": "Malawi"
  },
  "mx": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 72,
    "iso_alpha2": "MX",
    "iso_alpha3": "MEX",
    "iso_numeric": "484",
    "name_it": "Messico",
    "name_en": "Mexico"
  },
  "my": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 72,
    "iso_alpha2": "MY",
    "iso_alpha3": "MYS",
    "iso_numeric": "458",
    "name_it": "Malesia",
    "name_en": "Malaysia"
  },
  "mz": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 108,
    "iso_alpha2": "MZ",
    "iso_alpha3": "MOZ",
    "iso_numeric": "508",
    "name_it": "Mozambico",
    "name_en": "Mozambique"
  },
  "na": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 144,
    "iso_alpha2": "NA",
    "iso_alpha3": "NAM",
    "iso_numeric": "516",
    "name_it": "Namibia",
    "name_en": "Namibia"
  },
  "nc": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 180,
    "iso_alpha2": "NC",
    "iso_alpha3": "NCL",
    "iso_numeric": "540",
    "name_it": "Nuova Caledonia",
    "name_en": "New Caledonia"
  },
  "ne": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 216,
    "iso_alpha2": "NE",
    "iso_alpha3": "NER",
    "iso_numeric": "562",
    "name_it": "Niger",
    "name_en": "Niger"
  },
  "nf": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 252,
    "iso_alpha2": "NF",
    "iso_alpha3": "NFK",
    "iso_numeric": "574",
    "name_it": "Isola Norfolk",
    "name_en": "Norfolk Island"
  },
  "ng": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 288,
    "iso_alpha2": "NG",
    "iso_alpha3": "NGA",
    "iso_numeric": "566",
    "name_it": "Nigeria",
    "name_en": "Nigeria"
  },
  "ni": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 324,
    "iso_alpha2": "NI",
    "iso_alpha3": "NIC",
    "iso_numeric": "558",
    "name_it": "Nicaragua",
    "name_en": "Nicaragua"
  },
  "nl": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 360,
    "iso_alpha2": "NL",
    "iso_alpha3": "NLD",
    "iso_numeric": "528",
    "name_it": "Paesi Bassi",
    "name_en": "Netherlands"
  },
  "no": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 396,
    "iso_alpha2": "NO",
    "iso_alpha3": "NOR",
    "iso_numeric": "578",
    "name_it": "Norvegia",
    "name_en": "Norway"
  },
  "np": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 432,
    "iso_alpha2": "NP",
    "iso_alpha3": "NPL",
    "iso_numeric": "524",
    "name_it": "Nepal",
    "name_en": "Nepal"
  },
  "nr": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 468,
    "iso_alpha2": "NR",
    "iso_alpha3": "NRU",
    "iso_numeric": "520",
    "name_it": "Nauru",
    "name_en": "Nauru"
  },
  "nu": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 108,
    "iso_alpha2": "NU",
    "iso_alpha3": "NIU",
    "iso_numeric": "570",
    "name_it": "Niue",
    "name_en": "Niue"
  },
  "nz": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 108,
    "iso_alpha2": "NZ",
    "iso_alpha3": "NZL",
    "iso_numeric": "554",
    "name_it": "Nuova Zelanda",
    "name_en": "New Zealand"
  },
  "om": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 108,
    "iso_alpha2": "OM",
    "iso_alpha3": "OMN",
    "iso_numeric": "512",
    "name_it": "Oman",
    "name_en": "Oman"
  },
  "pa": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 108,
    "iso_alpha2": "PA",
    "iso_alpha3": "PAN",
    "iso_numeric": "591",
    "name_it": "Panama",
    "name_en": "Panama"
  },
  "pc": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 108,
    "iso_alpha2": "PC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "PC",
    "name_en": "PC"
  },
  "pe": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 108,
    "iso_alpha2": "PE",
    "iso_alpha3": "PER",
    "iso_numeric": "604",
    "name_it": "Perù",
    "name_en": "Peru"
  },
  "pf": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 108,
    "iso_alpha2": "PF",
    "iso_alpha3": "PYF",
    "iso_numeric": "258",
    "name_it": "Polinesia Francese",
    "name_en": "French Polynesia"
  },
  "pg": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 108,
    "iso_alpha2": "PG",
    "iso_alpha3": "PNG",
    "iso_numeric": "598",
    "name_it": "Papua Nuova Guinea",
    "name_en": "Papua New Guinea"
  },
  "ph": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 108,
    "iso_alpha2": "PH",
    "iso_alpha3": "PHL",
    "iso_numeric": "608",
    "name_it": "Filippine",
    "name_en": "Philippines"
  },
  "pk": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 108,
    "iso_alpha2": "PK",
    "iso_alpha3": "PAK",
    "iso_numeric": "586",
    "name_it": "Pakistan",
    "name_en": "Pakistan"
  },
  "pl": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 144,
    "iso_alpha2": "PL",
    "iso_alpha3": "POL",
    "iso_numeric": "616",
    "name_it": "Polonia",
    "name_en": "Poland"
  },
  "pm": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 180,
    "iso_alpha2": "PM",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "PM",
    "name_en": "PM"
  },
  "pn": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 216,
    "iso_alpha2": "PN",
    "iso_alpha3": "PCN",
    "iso_numeric": "612",
    "name_it": "Isole Pitcairn",
    "name_en": "Pitcairn Islands"
  },
  "pr": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 252,
    "iso_alpha2": "PR",
    "iso_alpha3": "PRI",
    "iso_numeric": "630",
    "name_it": "Porto Rico",
    "name_en": "Puerto Rico"
  },
  "ps": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 288,
    "iso_alpha2": "PS",
    "iso_alpha3": "PSE",
    "iso_numeric": "275",
    "name_it": "Palestina",
    "name_en": "Palestinian Territories"
  },
  "pt": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 324,
    "iso_alpha2": "PT",
    "iso_alpha3": "PRT",
    "iso_numeric": "620",
    "name_it": "Portogallo",
    "name_en": "Portugal"
  },
  "pw": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 360,
    "iso_alpha2": "PW",
    "iso_alpha3": "PLW",
    "iso_numeric": "585",
    "name_it": "Palau",
    "name_en": "Palau"
  },
  "py": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 396,
    "iso_alpha2": "PY",
    "iso_alpha3": "PRY",
    "iso_numeric": "600",
    "name_it": "Paraguay",
    "name_en": "Paraguay"
  },
  "qa": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 432,
    "iso_alpha2": "QA",
    "iso_alpha3": "QAT",
    "iso_numeric": "634",
    "name_it": "Qatar",
    "name_en": "Qatar"
  },
  "re": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 468,
    "iso_alpha2": "RE",
    "iso_alpha3": "REU",
    "iso_numeric": "638",
    "name_it": "Réunion",
    "name_en": "Réunion"
  },
  "ro": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 144,
    "iso_alpha2": "RO",
    "iso_alpha3": "ROU",
    "iso_numeric": "642",
    "name_it": "Romania",
    "name_en": "Romania"
  },
  "rs": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 144,
    "iso_alpha2": "RS",
    "iso_alpha3": "SRB",
    "iso_numeric": "688",
    "name_it": "Serbia",
    "name_en": "Serbia"
  },
  "ru": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 144,
    "iso_alpha2": "RU",
    "iso_alpha3": "RUS",
    "iso_numeric": "643",
    "name_it": "Russia",
    "name_en": "Russia"
  },
  "rw": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 144,
    "iso_alpha2": "RW",
    "iso_alpha3": "RWA",
    "iso_numeric": "646",
    "name_it": "Ruanda",
    "name_en": "Ruanda"
  },
  "sa": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 144,
    "iso_alpha2": "SA",
    "iso_alpha3": "SAU",
    "iso_numeric": "682",
    "name_it": "Arabia Saudita",
    "name_en": "Saudi Arabia"
  },
  "sb": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 144,
    "iso_alpha2": "SB",
    "iso_alpha3": "SLB",
    "iso_numeric": "090",
    "name_it": "Isole Salomone",
    "name_en": "Solomon Islands"
  },
  "sc": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 144,
    "iso_alpha2": "SC",
    "iso_alpha3": "SYC",
    "iso_numeric": "690",
    "name_it": "Seychelles",
    "name_en": "Seychelles"
  },
  "sd": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 144,
    "iso_alpha2": "SD",
    "iso_alpha3": "SDN",
    "iso_numeric": "729",
    "name_it": "Sudan",
    "name_en": "Sudan"
  },
  "se": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 144,
    "iso_alpha2": "SE",
    "iso_alpha3": "SWE",
    "iso_numeric": "752",
    "name_it": "Svezia",
    "name_en": "Sweden"
  },
  "sg": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 180,
    "iso_alpha2": "SG",
    "iso_alpha3": "SGP",
    "iso_numeric": "702",
    "name_it": "Singapore",
    "name_en": "Singapore"
  },
  "sh": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 216,
    "iso_alpha2": "SH",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "SH",
    "name_en": "SH"
  },
  "sh-ac": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 252,
    "iso_alpha2": "SH-AC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "SH-AC",
    "name_en": "SH-AC"
  },
  "sh-hl": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 288,
    "iso_alpha2": "SH-HL",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "SH-HL",
    "name_en": "SH-HL"
  },
  "sh-ta": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 324,
    "iso_alpha2": "SH-TA",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "SH-TA",
    "name_en": "SH-TA"
  },
  "si": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 360,
    "iso_alpha2": "SI",
    "iso_alpha3": "SVN",
    "iso_numeric": "705",
    "name_it": "Slovenia",
    "name_en": "Slovenia"
  },
  "sj": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 396,
    "iso_alpha2": "SJ",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "SJ",
    "name_en": "SJ"
  },
  "sk": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 432,
    "iso_alpha2": "SK",
    "iso_alpha3": "SVK",
    "iso_numeric": "703",
    "name_it": "Slovacchia",
    "name_en": "Slovakia"
  },
  "sl": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 468,
    "iso_alpha2": "SL",
    "iso_alpha3": "SLE",
    "iso_numeric": "694",
    "name_it": "Sierra Leone",
    "name_en": "Sierra Leone"
  },
  "sm": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 180,
    "iso_alpha2": "SM",
    "iso_alpha3": "SMR",
    "iso_numeric": "674",
    "name_it": "San Marino",
    "name_en": "San Marino"
  },
  "sn": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 180,
    "iso_alpha2": "SN",
    "iso_alpha3": "SEN",
    "iso_numeric": "686",
    "name_it": "Senegal",
    "name_en": "Senegal"
  },
  "so": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 180,
    "iso_alpha2": "SO",
    "iso_alpha3": "SOM",
    "iso_numeric": "706",
    "name_it": "Somalia",
    "name_en": "Somalia"
  },
  "sr": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 180,
    "iso_alpha2": "SR",
    "iso_alpha3": "SUR",
    "iso_numeric": "740",
    "name_it": "Suriname",
    "name_en": "Suriname"
  },
  "ss": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 180,
    "iso_alpha2": "SS",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "SS",
    "name_en": "SS"
  },
  "st": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 180,
    "iso_alpha2": "ST",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "ST",
    "name_en": "ST"
  },
  "sv": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 180,
    "iso_alpha2": "SV",
    "iso_alpha3": "SLV",
    "iso_numeric": "222",
    "name_it": "El Salvador",
    "name_en": "El Salvador"
  },
  "sx": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 180,
    "iso_alpha2": "SX",
    "iso_alpha3": "SXM",
    "iso_numeric": "534",
    "name_it": "Sint Maarten",
    "name_en": "Sint Maarten"
  },
  "sy": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 216,
    "iso_alpha2": "SY",
    "iso_alpha3": "SYR",
    "iso_numeric": "760",
    "name_it": "Siria",
    "name_en": "Syria"
  },
  "sz": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 252,
    "iso_alpha2": "SZ",
    "iso_alpha3": "SWZ",
    "iso_numeric": "748",
    "name_it": "Eswatini",
    "name_en": "Eswatini"
  },
  "tc": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 288,
    "iso_alpha2": "TC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "TC",
    "name_en": "TC"
  },
  "td": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 324,
    "iso_alpha2": "TD",
    "iso_alpha3": "TCD",
    "iso_numeric": "148",
    "name_it": "Ciad",
    "name_en": "Chad"
  },
  "tf": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 360,
    "iso_alpha2": "TF",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "TF",
    "name_en": "TF"
  },
  "tg": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 396,
    "iso_alpha2": "TG",
    "iso_alpha3": "TGO",
    "iso_numeric": "768",
    "name_it": "Togo",
    "name_en": "Togo"
  },
  "th": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 432,
    "iso_alpha2": "TH",
    "iso_alpha3": "THA",
    "iso_numeric": "764",
    "name_it": "Thailandia",
    "name_en": "Thailand"
  },
  "tj": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 468,
    "iso_alpha2": "TJ",
    "iso_alpha3": "TJK",
    "iso_numeric": "762",
    "name_it": "Tagikistan",
    "name_en": "Tajikistan"
  },
  "tk": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 216,
    "iso_alpha2": "TK",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "TK",
    "name_en": "TK"
  },
  "tl": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 216,
    "iso_alpha2": "TL",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "TL",
    "name_en": "TL"
  },
  "tm": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 216,
    "iso_alpha2": "TM",
    "iso_alpha3": "TKM",
    "iso_numeric": "795",
    "name_it": "Turkmenistan",
    "name_en": "Turkmenistan"
  },
  "tn": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 216,
    "iso_alpha2": "TN",
    "iso_alpha3": "TUN",
    "iso_numeric": "788",
    "name_it": "Tunisia",
    "name_en": "Tunisia"
  },
  "to": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 216,
    "iso_alpha2": "TO",
    "iso_alpha3": "TON",
    "iso_numeric": "776",
    "name_it": "Tonga",
    "name_en": "Tonga"
  },
  "tr": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 216,
    "iso_alpha2": "TR",
    "iso_alpha3": "TUR",
    "iso_numeric": "792",
    "name_it": "Turchia",
    "name_en": "Turkey"
  },
  "tt": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 216,
    "iso_alpha2": "TT",
    "iso_alpha3": "TTO",
    "iso_numeric": "780",
    "name_it": "Trinidad e Tobago",
    "name_en": "Trinidad & Tobago"
  },
  "tv": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 252,
    "iso_alpha2": "TV",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "TV",
    "name_en": "TV"
  },
  "tw": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 288,
    "iso_alpha2": "TW",
    "iso_alpha3": "TWN",
    "iso_numeric": "158",
    "name_it": "Taiwan",
    "name_en": "Taiwan"
  },
  "tz": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 324,
    "iso_alpha2": "TZ",
    "iso_alpha3": "TZA",
    "iso_numeric": "834",
    "name_it": "Tanzania",
    "name_en": "Tanzania"
  },
  "ua": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 360,
    "iso_alpha2": "UA",
    "iso_alpha3": "UKR",
    "iso_numeric": "804",
    "name_it": "Ucraina",
    "name_en": "Ukraine"
  },
  "ug": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 396,
    "iso_alpha2": "UG",
    "iso_alpha3": "UGA",
    "iso_numeric": "800",
    "name_it": "Uganda",
    "name_en": "Uganda"
  },
  "um": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 432,
    "iso_alpha2": "UM",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "UM",
    "name_en": "UM"
  },
  "un": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 468,
    "iso_alpha2": "UN",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "UN",
    "name_en": "UN"
  },
  "us": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 252,
    "iso_alpha2": "US",
    "iso_alpha3": "USA",
    "iso_numeric": "840",
    "name_it": "Stati Uniti",
    "name_en": "United States"
  },
  "uy": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 252,
    "iso_alpha2": "UY",
    "iso_alpha3": "URY",
    "iso_numeric": "858",
    "name_it": "Uruguay",
    "name_en": "Uruguay"
  },
  "uz": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 252,
    "iso_alpha2": "UZ",
    "iso_alpha3": "UZB",
    "iso_numeric": "860",
    "name_it": "Uzbekistan",
    "name_en": "Uzbekistan"
  },
  "va": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 252,
    "iso_alpha2": "VA",
    "iso_alpha3": "VAT",
    "iso_numeric": "336",
    "name_it": "Città del Vaticano",
    "name_en": "Vatican City"
  },
  "vc": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 252,
    "iso_alpha2": "VC",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "VC",
    "name_en": "VC"
  },
  "ve": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 252,
    "iso_alpha2": "VE",
    "iso_alpha3": "VEN",
    "iso_numeric": "862",
    "name_it": "Venezuela",
    "name_en": "Venezuela"
  },
  "vg": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 288,
    "iso_alpha2": "VG",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "VG",
    "name_en": "VG"
  },
  "vi": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 324,
    "iso_alpha2": "VI",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "VI",
    "name_en": "VI"
  },
  "vn": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 360,
    "iso_alpha2": "VN",
    "iso_alpha3": "VNM",
    "iso_numeric": "704",
    "name_it": "Vietnam",
    "name_en": "Vietnam"
  },
  "vu": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 396,
    "iso_alpha2": "VU",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "VU",
    "name_en": "VU"
  },
  "wf": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 432,
    "iso_alpha2": "WF",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "WF",
    "name_en": "WF"
  },
  "ws": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 468,
    "iso_alpha2": "WS",
    "iso_alpha3": "WSM",
    "iso_numeric": "882",
    "name_it": "Samoa",
    "name_en": "Samoa"
  },
  "xk": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 288,
    "iso_alpha2": "XK",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "XK",
    "name_en": "XK"
  },
  "xx": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 288,
    "iso_alpha2": "XX",
    "iso_alpha3": "UNKNOWN",
    "iso_numeric": "UNKNOWN",
    "name_it": "XX",
    "name_en": "XX"
  },
  "ye": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 288,
    "iso_alpha2": "YE",
    "iso_alpha3": "YEM",
    "iso_numeric": "887",
    "name_it": "Yemen",
    "name_en": "Yemen"
  },
  "yt": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 288,
    "iso_alpha2": "YT",
    "iso_alpha3": "MYT",
    "iso_numeric": "175",
    "name_it": "Mayotte",
    "name_en": "Mayotte"
  },
  "za": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 288,
    "iso_alpha2": "ZA",
    "iso_alpha3": "ZAF",
    "iso_numeric": "710",
    "name_it": "Sudafrica",
    "name_en": "South Africa"
  },
  "zm": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 324,
    "iso_alpha2": "ZM",
    "iso_alpha3": "ZMB",
    "iso_numeric": "894",
    "name_it": "Zambia",
    "name_en": "Zambia"
  },
  "zw": {
    "height": 36,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 360,
    "iso_alpha2": "ZW",
    "iso_alpha3": "ZWE",
    "iso_numeric": "716",
    "name_it": "Zimbabwe",
    "name_en": "Zimbabwe"
  }
}
```

## `static/Spite OLD/old_sprite.json`

Nota: File JSON: verificare dal contenuto se è configurazione o dato.

```text
{
  "aerialway": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 147,
    "y": 190
  },
  "aerialway_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 252,
    "y": 169
  },
  "airfield": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 166,
    "y": 190
  },
  "airfield_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 267,
    "y": 169
  },
  "airport": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 185,
    "y": 190
  },
  "airport_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 438,
    "y": 211
  },
  "alcohol_shop": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 64,
    "y": 0
  },
  "alcohol_shop_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 455,
    "y": 211
  },
  "american_football": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 85,
    "y": 0
  },
  "american_football_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 472,
    "y": 211
  },
  "amusement_park": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 106,
    "y": 0
  },
  "amusement_park_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 489,
    "y": 211
  },
  "aquarium": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "aquarium_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 246,
    "y": 230
  },
  "arrow": {
    "height": 7,
    "pixelRatio": 1,
    "width": 10,
    "x": 72,
    "y": 249
  },
  "art_gallery": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 21,
    "y": 64
  },
  "art_gallery_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 263,
    "y": 230
  },
  "attraction": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 42,
    "y": 64
  },
  "attraction_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 280,
    "y": 230
  },
  "bakery": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 64
  },
  "bakery_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 297,
    "y": 230
  },
  "bank": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 64
  },
  "bank_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 314,
    "y": 230
  },
  "bar": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 105,
    "y": 64
  },
  "bar_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 331,
    "y": 230
  },
  "baseball": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 85
  },
  "baseball_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 348,
    "y": 230
  },
  "basketball": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 21,
    "y": 85
  },
  "basketball_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 365,
    "y": 230
  },
  "beer": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 42,
    "y": 85
  },
  "beer_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 382,
    "y": 230
  },
  "bicycle": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 85
  },
  "bicycle_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 399,
    "y": 230
  },
  "bicycle_rental": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 85
  },
  "bicycle_rental_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 416,
    "y": 230
  },
  "building": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 204,
    "y": 190
  },
  "building_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 282,
    "y": 169
  },
  "bus": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 223,
    "y": 190
  },
  "bus_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 297,
    "y": 169
  },
  "butcher": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 105,
    "y": 85
  },
  "butcher_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 433,
    "y": 230
  },
  "cafe": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 106
  },
  "cafe_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 450,
    "y": 230
  },
  "campsite": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 21,
    "y": 106
  },
  "campsite_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 467,
    "y": 230
  },
  "car": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 211
  },
  "car_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 312,
    "y": 169
  },
  "castle": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 42,
    "y": 106
  },
  "castle_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 484,
    "y": 230
  },
  "cemetery": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 106
  },
  "cemetery_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 252,
    "y": 64
  },
  "cinema": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 106
  },
  "cinema_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 269,
    "y": 64
  },
  "circle": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 19,
    "y": 211
  },
  "circle_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 327,
    "y": 169
  },
  "circle_11_black": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 286,
    "y": 64
  },
  "circle_stroked": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 38,
    "y": 211
  },
  "circle_stroked_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 342,
    "y": 169
  },
  "clothing_store": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 105,
    "y": 106
  },
  "clothing_store_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 303,
    "y": 64
  },
  "college": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 126,
    "y": 64
  },
  "college_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 64
  },
  "commercial": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 57,
    "y": 211
  },
  "commercial_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 357,
    "y": 169
  },
  "cricket": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 147,
    "y": 64
  },
  "cricket_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 337,
    "y": 64
  },
  "cross": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 76,
    "y": 211
  },
  "cross_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 372,
    "y": 169
  },
  "dam": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 95,
    "y": 211
  },
  "dam_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 387,
    "y": 169
  },
  "danger": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 168,
    "y": 64
  },
  "danger_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 354,
    "y": 64
  },
  "default_1": {
    "height": 18,
    "pixelRatio": 1,
    "width": 18,
    "x": 228,
    "y": 230
  },
  "default_2": {
    "height": 18,
    "pixelRatio": 1,
    "width": 25,
    "x": 247,
    "y": 211
  },
  "default_3": {
    "height": 18,
    "pixelRatio": 1,
    "width": 32,
    "x": 272,
    "y": 211
  },
  "default_4": {
    "height": 18,
    "pixelRatio": 1,
    "width": 39,
    "x": 304,
    "y": 211
  },
  "default_5": {
    "height": 18,
    "pixelRatio": 1,
    "width": 45,
    "x": 343,
    "y": 211
  },
  "default_6": {
    "height": 18,
    "pixelRatio": 1,
    "width": 50,
    "x": 388,
    "y": 211
  },
  "dentist": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 64
  },
  "dentist_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 371,
    "y": 64
  },
  "doctors": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 210,
    "y": 64
  },
  "doctors_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 388,
    "y": 64
  },
  "dog_park": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 126,
    "y": 127
  },
  "dog_park_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 405,
    "y": 64
  },
  "dot_10": {
    "height": 10,
    "pixelRatio": 1,
    "width": 10,
    "x": 53,
    "y": 249
  },
  "dot_11": {
    "height": 11,
    "pixelRatio": 1,
    "width": 11,
    "x": 42,
    "y": 249
  },
  "dot_9": {
    "height": 9,
    "pixelRatio": 1,
    "width": 9,
    "x": 63,
    "y": 249
  },
  "drinking_water": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 126,
    "y": 85
  },
  "drinking_water_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 422,
    "y": 64
  },
  "embassy": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 147,
    "y": 85
  },
  "embassy_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 439,
    "y": 64
  },
  "entrance": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 114,
    "y": 211
  },
  "entrance_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 402,
    "y": 169
  },
  "fast_food": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 168,
    "y": 85
  },
  "fast_food_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 456,
    "y": 64
  },
  "ferry": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 133,
    "y": 211
  },
  "ferry_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 417,
    "y": 169
  },
  "fire_station": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 85
  },
  "fire_station_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 473,
    "y": 64
  },
  "florist": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 210,
    "y": 85
  },
  "fuel": {
    "height": 21,
    "pixelRatio": 1,
    "width": 15,
    "x": 152,
    "y": 211
  },
  "fuel_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 432,
    "y": 169
  },
  "furniture": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 231,
    "y": 85
  },
  "furniture_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  },
  "garden": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 126,
    "y": 106
  },
  "garden_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 490,
    "y": 64
  },
  "gift": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 147,
    "y": 106
  },
  "gift_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 252,
    "y": 85
  },
  "golf": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 168,
    "y": 106
  },
  "golf_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 269,
    "y": 85
  },
  "grocery": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 106
  },
  "grocery_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 286,
    "y": 85
  },
  "hairdresser": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 210,
    "y": 106
  },
  "hairdresser_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 303,
    "y": 85
  },
  "harbor": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 171,
    "y": 211
  },
  "harbor_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 447,
    "y": 169
  },
  "heart": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 231,
    "y": 106
  },
  "heart_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 85
  },
  "heliport": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 190,
    "y": 211
  },
  "heliport_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 462,
    "y": 169
  },
  "hospital": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 127,
    "y": 0
  },
  "hospital_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 337,
    "y": 85
  },
  "ice_cream": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 148,
    "y": 0
  },
  "ice_cream_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 354,
    "y": 85
  },
  "industry": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 209,
    "y": 211
  },
  "industry_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 477,
    "y": 169
  },
  "information": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 169,
    "y": 0
  },
  "information_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 371,
    "y": 85
  },
  "laundry": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 190,
    "y": 0
  },
  "laundry_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 388,
    "y": 85
  },
  "library": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 211,
    "y": 0
  },
  "library_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 405,
    "y": 85
  },
  "lighthouse": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 232,
    "y": 0
  },
  "lighthouse_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 422,
    "y": 85
  },
  "lodging": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 127
  },
  "lodging_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 439,
    "y": 85
  },
  "marker": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 228,
    "y": 211
  },
  "marker_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 492,
    "y": 169
  },
  "monument": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 21,
    "y": 127
  },
  "monument_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 456,
    "y": 85
  },
  "mountain": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 42,
    "y": 127
  },
  "mountain_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 473,
    "y": 85
  },
  "museum": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 127
  },
  "museum_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 490,
    "y": 85
  },
  "music": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 127
  },
  "music_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 252,
    "y": 106
  },
  "oneway": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 105,
    "y": 127
  },
  "park": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 126,
    "y": 127
  },
  "park_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 269,
    "y": 106
  },
  "parking": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 230
  },
  "parking_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 242,
    "y": 190
  },
  "parking_garage": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 19,
    "y": 230
  },
  "parking_garage_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 257,
    "y": 190
  },
  "pedestrian_polygon": {
    "height": 64,
    "pixelRatio": 1,
    "width": 64,
    "x": 0,
    "y": 0
  },
  "pharmacy": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 147,
    "y": 127
  },
  "pharmacy_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 286,
    "y": 106
  },
  "picnic_site": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 168,
    "y": 127
  },
  "picnic_site_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 303,
    "y": 106
  },
  "pitch": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "pitch_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 106
  },
  "place_of_worship": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 210,
    "y": 127
  },
  "place_of_worship_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 337,
    "y": 106
  },
  "playground": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 231,
    "y": 127
  },
  "playground_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 354,
    "y": 106
  },
  "police": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 148
  },
  "police_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 371,
    "y": 106
  },
  "post": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 21,
    "y": 148
  },
  "post_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 388,
    "y": 106
  },
  "prison": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 42,
    "y": 148
  },
  "prison_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 405,
    "y": 106
  },
  "railway": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 38,
    "y": 230
  },
  "railway_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 272,
    "y": 190
  },
  "railway_light": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 57,
    "y": 230
  },
  "railway_light_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 287,
    "y": 190
  },
  "railway_metro": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 76,
    "y": 230
  },
  "railway_metro_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 302,
    "y": 190
  },
  "ranger_station": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 148
  },
  "ranger_station_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 422,
    "y": 106
  },
  "religious_christian": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 148
  },
  "religious_christian_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 439,
    "y": 106
  },
  "religious_jewish": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 105,
    "y": 148
  },
  "religious_jewish_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 456,
    "y": 106
  },
  "religious_muslim": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 126,
    "y": 148
  },
  "religious_muslim_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 473,
    "y": 106
  },
  "restaurant": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 147,
    "y": 148
  },
  "restaurant_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 490,
    "y": 106
  },
  "road_1": {
    "height": 14,
    "pixelRatio": 1,
    "width": 14,
    "x": 498,
    "y": 148
  },
  "road_2": {
    "height": 14,
    "pixelRatio": 1,
    "width": 20,
    "x": 437,
    "y": 190
  },
  "road_3": {
    "height": 14,
    "pixelRatio": 1,
    "width": 25,
    "x": 457,
    "y": 190
  },
  "road_4": {
    "height": 14,
    "pixelRatio": 1,
    "width": 31,
    "x": 253,
    "y": 0
  },
  "road_5": {
    "height": 14,
    "pixelRatio": 1,
    "width": 36,
    "x": 284,
    "y": 0
  },
  "road_6": {
    "height": 14,
    "pixelRatio": 1,
    "width": 40,
    "x": 320,
    "y": 0
  },
  "roadblock": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 168,
    "y": 148
  },
  "roadblock_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 252,
    "y": 127
  },
  "rocket": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 148
  },
  "rocket_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 269,
    "y": 127
  },
  "school": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 210,
    "y": 148
  },
  "school_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 286,
    "y": 127
  },
  "shelter": { 
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 231,
    "y": 148
  },
  "shelter_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 303,
    "y": 127
  },
  "shop": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "shop_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  },
  "skiing": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 21,
    "y": 169
  },
  "skiing_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 337,
    "y": 127
  },
  "soccer": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "soccer_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 354,
    "y": 127
  },
  "square": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 95,
    "y": 230
  },
  "square_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 317,
    "y": 190
  },
  "square_stroked": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 114,
    "y": 230
  },
  "square_stroked_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 332,
    "y": 190
  },
  "stadium": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 169
  },
  "stadium_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 371,
    "y": 127
  },
  "star": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 133,
    "y": 230
  },
  "star_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 347,
    "y": 190
  },
  "star_stroked": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 152,
    "y": 230
  },
  "star_stroked_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 362,
    "y": 190
  },
  "suitcase": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 169
  },
  "suitcase_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 388,
    "y": 127
  },
  "sushi": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 105,
    "y": 169
  },
  "sushi_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 405,
    "y": 127
  },
  "swimming": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 126,
    "y": 169
  },
  "swimming_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 422,
    "y": 127
  },
  "telephone": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 147,
    "y": 169
  },
  "telephone_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 439,
    "y": 127
  },
  "tennis": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 168,
    "y": 169
  },
  "tennis_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 456,
    "y": 127
  },
  "theatre": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189 ,
    "y": 169
  },
  "theatre_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 473,
    "y": 127
  },
  "toilets": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 210,
    "y": 169
  },
  "toilets_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 490,
    "y": 127
  },
  "town_hall": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 231,
    "y": 169
  },
  "town_hall_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 252,
    "y": 148
  },
  "triangle": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 171,
    "y": 230
  },
  "triangle_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 377,
    "y": 190
  },
  "triangle_stroked": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 190,
    "y": 230
  },
  "triangle_stroked_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 392,
    "y": 190
  },
  "us-highway_1": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 269,
    "y": 148
  },
  "us-highway_2": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 286,
    "y": 148
  },
  "us-highway_3": {
    "height": 17,
    "pixelRatio": 1,
    "width": 21,
    "x": 303,
    "y": 148
  },
  "us-interstate_1": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 324,
    "y": 148
  },
  "us-interstate_2": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 341,
    "y": 148
  },
  "us-interstate_3": {
    "height": 17,
    "pixelRatio": 1,
    "width": 21,
    "x": 358,
    "y": 148
  },
  "us-state_1": {
    "height": 14,
    "pixelRatio": 1,
    "width": 17,
    "x": 482,
    "y": 190
  },
  "us-state_2": {
    "height": 14,
    "pixelRatio": 1,
    "width": 22,
    "x": 360,
    "y": 0
  },
  "us-state_3": {
    "height": 14,
    "pixelRatio": 1,
    "width": 27,
    "x": 382,
    "y": 0
  },
  "us-state_4": {
    "height": 14,
    "pixelRatio": 1,
    "width": 32,
    "x": 409,
    "y": 0
  },
  "us-state_5": {
    "height": 14,
    "pixelRatio": 1,
    "width": 37,
    "x": 441,
    "y": 0
  },
  "us-state_6": {
    "height": 14,
    "pixelRatio": 1,
    "width": 42,
    "x": 0,
    "y": 249
  },
  "veterinary": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 190
  },
  "veterinary_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 379,
    "y": 148
  },
  "volcano": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 21,
    "y": 190
  },
  "volcano_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 396,
    "y": 148
  },
  "warehouse": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 209,
    "y": 230
  },
  "warehouse_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 407,
    "y": 190
  },
  "waste_basket": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 42,
    "y": 190
  },
  "waste_basket_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 413,
    "y": 148
  },
  "water": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 190
  },
  "water_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 430,
    "y": 148
  },
  "wetland": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 190
  },
  "wetland_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 447,
    "y": 148
  },
  "wetland_bg_11": {
    "height": 15,
    "pixelRatio": 1,
    "width": 15,
    "x": 422,
    "y": 190
  },
  "wheelchair": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 105,
    "y": 190
  },
  "wheelchair_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 464,
    "y": 148
  },
  "zoo": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 126,
    "y": 190
  },
  "zoo_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 481,
    "y": 148
  },
  "tram_stop": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "bus_stop": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 223,
    "y": 190
  },
  "bus_stop_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 297,
    "y": 169
  },
  "university": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 126,
    "y": 64
  },
  "university_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 64
  },
  "kindergarten": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 210,
    "y": 148
  },
  "kindergarten_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 286,
    "y": 127
  },
  "community_centre": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "townhall": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 231,
    "y": 169
  },
  "townhall_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 252,
    "y": 148
  },
  "grave_yard": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 106
  },
  "grave_yard_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 252,
    "y": 64
  },
  "books": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 211,
    "y": 0
  },
  "books_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 405,
    "y": 85
  },
  "post_office": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 21,
    "y": 148
  },
  "post_office_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 388,
    "y": 106
  },
  "parcel_locker": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 21,
    "y": 148
  },
  "parcel_locker_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 388,
    "y": 106
  },
  "post_box": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 21,
    "y": 148
  },
  "post_box_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 388,
    "y": 106
  },
  "kiosk": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "kiosk_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  },
  "stationery": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
 "stationery_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  }, 
  "shoes": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "shoes_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  },
  "newsagent": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "cosmetics": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "cosmetics_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  },
  "convenience": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "convenience_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  },
  "jewelry": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "tailor": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 210,
    "y": 106
  },
  "tailor_11": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 303,
    "y": 85
  },
  "mall": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "mall:11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  },
  "tobacco": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "tobacco_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  },
  "mobile_phone": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "mobile_phone_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  },
  "hearing_aids": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 127,
    "y": 0
  },
  "hearing_aids_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 388,
    "y": 64
  },
  "optician": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "optician_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  },
  "tattoo": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "tattoo_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  },
  "copyshop": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "copyshop_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  },
  "sports": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 42,
    "y": 169
  },
  "sports_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 354,
    "y": 127
  },
  "computer": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "computer_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 320,
    "y": 127
  },
  "travel_agency": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "motorcycle": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "toys": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "beauty": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "fabric": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "supermarket": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 106
  },
  "greengrocer": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "marketplace": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 106
  },
  "deli": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 64
  },
  "clothes": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "sports_centre": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "car_repair": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "car_parts": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "charging_station": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 152,
    "y": 211
  },
  "educational_institution": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 210,
    "y": 148
  },
  "estate_agent": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "dry_cleaning": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "hostel": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "artwork": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 127
  },
  "arts_centre": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 127
  },
  "moving_company": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "company": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "government": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "insurance": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 64
  },
  "insurance_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 314,
    "y": 230
  },
  "christian": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 148
  },
  "wine": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 105,
    "y": 64
  },
  "it": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "political_party": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "atm": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 64
  },
  "atm_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 314,
    "y": 230
  },
  "ngo": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "hotel": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 127
  },
  "hotel_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 439,
    "y": 85
  },
  "religion": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "brownfield": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "energy_supplier": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "gate": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 114,
    "y": 211
  },
  "pub": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 105,
    "y": 64
  },
  "biergarten": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "hardware": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "ticket": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "recycling": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "bollard": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "lift_gate": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "bicycle_parking": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 85
  },
  "bowls": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "cycle_barrier": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "pattinaggio": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "motorcycle_parking": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "swimming_pool": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 126,
    "y": 169
  },
  "shooting": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "athletics": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "ruins": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "basketball;pickleball": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "terminal": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "running": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "taxi": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 0,
    "y": 211
  },
  "yes": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "paddle_tennis": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 168,
    "y": 169
  },
  "multi": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "courthouse": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "chemist": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "bed": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "perfumery": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "pet": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "second_hand": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "outdoor": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "electronics": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "confectionery": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 64
  },
  "coffee": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 105,
    "y": 64
  },
    "coffee_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 331,
    "y": 230
  },
  "garden_centre": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "interior_decoration": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "photo": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "carpet": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "massage": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "erotic": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "charity": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "antiques": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "watches": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "department_store": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "bag": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "nightclub": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "dormitory": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "coworking": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "financial": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 64
  },
  "financial_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 314,
    "y": 230
  },
  "lawyer": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "escape_game": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "guest_house": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "logistics": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "consulting": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "employment_agency": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "financial_advisor": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 64
  },
  "financial_advisor_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 314,
    "y": 230
  },
  "newspaper": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "tax_advisor": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 64
  },
  "tax_advisor_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 314,
    "y": 230
  },
  "association": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "union": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "beverages": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 105,
    "y": 64
  },
  "security": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "publisher": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "jewish": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "skateboard;roller_skating": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "engineer": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "telecommunication": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "accountant": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 84,
    "y": 64
  },
  "accountant_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 314,
    "y": 230
  },
  "musical_instrument": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "yoga": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "architect": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "art": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "office": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "foundation": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "alcohol": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "board": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "table_tennis": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "terminal;map": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "basketball;tennis": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "gallery": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 63,
    "y": 127
  },
  "caravan_site": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "clinic": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 210,
    "y": 64
  },
    "clinic_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 388,
    "y": 64
  },

  "alpine_hut": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "viewpoint": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "subway": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "station": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "halt": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "ferry_terminal": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 171,
    "y": 211
  },
  "chalet": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "motel": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "bus_station": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 223,
    "y": 190
  },
  "car_rental": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 0,
    "y": 211
  },
  "flats": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "house": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "social_facility": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "shower": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "bbq": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "bench": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "aeroway": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 166,
    "y": 190
  },
  "aerodrome_label": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 166,
    "y": 190
  },
  "boundary": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "place": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "archery": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "basin": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "badminton": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "beachvolleyball": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "billiards": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "bmx": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "border_control": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "camp_site": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "canoe": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 147,
    "y": 190
  },
  "climbing": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "climbing_adventure": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "curling": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "cycling": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "subway_entrance": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "train_station_entrance": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "equestrian": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "food_court": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "free_flying": {
    "height": 19,
    "pixelRatio": 1,
    "width": 19,
    "x": 166,
    "y": 190
  },
  "golf_course": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 168,
    "y": 106
  },
  "miniature_golf": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 168,
    "y": 106
  },
  "hackerspace": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "marina": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 171,
    "y": 211
  },
  "marina_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 447,
    "y": 169
  },
  "dock": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "horse_racing": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "nursing_home": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "ice_rink": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 189,
    "y": 127
  },
  "guidepost": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 21,
    "y": 148
  },
  "guidepost_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 388,
    "y": 106
  },
  "map": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "route_marker": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  },
  "trail_blaze": {
    "height": 21,
    "pixelRatio": 1,
    "width": 21,
    "x": 0,
    "y": 169
  }
}
```

## `static/Spite OLD/old_sprite@2x.json`

Nota: File JSON: verificare dal contenuto se è configurazione o dato.

```text
{
  "aerialway": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 294,
    "y": 380
  },
  "aerialway_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 504,
    "y": 338
  },
  "airfield": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 332,
    "y": 380
  },
  "airfield_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 534,
    "y": 338
  },
  "airport": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 370,
    "y": 380
  },
  "airport_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 876,
    "y": 422
  },
  "alcohol_shop": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 128,
    "y": 0
  },
  "alcohol_shop_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 910,
    "y": 422
  },
  "american_football": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 170,
    "y": 0
  },
  "american_football_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 944,
    "y": 422
  },
  "amusement_park": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 212,
    "y": 0
  },
  "amusement_park_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 978,
    "y": 422
  },
  "aquarium": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 128
  },
  "aquarium_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 492,
    "y": 460
  },
  "arrow": {
    "height": 14,
    "pixelRatio": 2,
    "width": 20,
    "x": 144,
    "y": 498
  },
  "art_gallery": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 42,
    "y": 128
  },
  "art_gallery_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 526,
    "y": 460
  },
  "attraction": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 84,
    "y": 128
  },
  "attraction_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 560,
    "y": 460
  },
  "bakery": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 126,
    "y": 128
  },
  "bakery_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 594,
    "y": 460
  },
  "bank": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 168,
    "y": 128
  },
  "bank_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 628,
    "y": 460
  },
  "bar": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 210,
    "y": 128
  },
  "bar_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 662,
    "y": 460
  },
  "baseball": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 170
  },
  "baseball_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 696,
    "y": 460
  },
  "basketball": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 42,
    "y": 170
  },
  "basketball_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 730,
    "y": 460
  },
  "beer": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 84,
    "y": 170
  },
  "beer_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 764,
    "y": 460
  },
  "bicycle": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 126,
    "y": 170
  },
  "bicycle_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 798,
    "y": 460
  },
  "bicycle_rental": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 168,
    "y": 170
  },
  "bicycle_rental_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 832,
    "y": 460
  },
  "books": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 222,
    "y": 0
  },
  "books_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 810,
    "y": 170
  },
  "building": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 408,
    "y": 380
  },
  "building_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 564,
    "y": 338
  },
  "bus": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 446,
    "y": 380
  },
  "bus_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 594,
    "y": 338
  },
  "butcher": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 210,
    "y": 170
  },
  "butcher_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 866,
    "y": 460
  },
  "cafe": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 212
  },
  "cafe_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 900,
    "y": 460
  },
  "campsite": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 42,
    "y": 212
  },
  "campsite_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 934,
    "y": 460
  },
  "car": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 0,
    "y": 422
  },
  "car_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 624,
    "y": 338
  },
  "castle": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 84,
    "y": 212
  },
  "castle_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 968,
    "y": 460
  },
  "cemetery": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 126,
    "y": 212
  },
  "cemetery_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 504,
    "y": 128
  },
  "cinema": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 168,
    "y": 212
  },
  "cinema_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 538,
    "y": 128
  },
  "circle": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 38,
    "y": 422
  },
  "circle_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 654,
    "y": 338
  },
  "circle_11_black": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 572,
    "y": 128
  },
  "circle_stroked": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 76,
    "y": 422
  },
  "circle_stroked_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 684,
    "y": 338
  },
  "clothing_store": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 210,
    "y": 212
  },
  "clothing_store_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 606,
    "y": 128
  },
  "college": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 252,
    "y": 128
  },
  "college_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 128
  },
  "commercial": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 114,
    "y": 422
  },
  "commercial_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 714,
    "y": 338
  },
  "cosmetics": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
  "cosmetics_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 254
  },
  "convenience": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
  "convenience_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 254
  },
  "cricket": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 294,
    "y": 128
  },
  "cricket_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 674,
    "y": 128
  },
  "cross": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 152,
    "y": 422
  },
  "cross_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 744,
    "y": 338
  },
  "dam": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 190,
    "y": 422
  },
  "dam_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 774,
    "y": 338
  },
  "danger": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 336,
    "y": 128
  },
  "danger_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 708,
    "y": 128
  },
  "default_1": {
    "height": 36,
    "pixelRatio": 2,
    "width": 36,
    "x": 456,
    "y": 460
  },
  "default_2": {
    "height": 36,
    "pixelRatio": 2,
    "width": 50,
    "x": 494,
    "y": 422
  },
  "default_3": {
    "height": 36,
    "pixelRatio": 2,
    "width": 64,
    "x": 544,
    "y": 422
  },
  "default_4": {
    "height": 36,
    "pixelRatio": 2,
    "width": 78,
    "x": 608,
    "y": 422
  },
  "default_5": {
    "height": 36,
    "pixelRatio": 2,
    "width": 90,
    "x": 686,
    "y": 422
  },
  "default_6": {
    "height": 36,
    "pixelRatio": 2,
    "width": 100,
    "x": 776,
    "y": 422
  },
  "dentist": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 378,
    "y": 128
  },
  "dentist_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 742,
    "y": 128
  },
  "doctors": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 420,
    "y": 128
  },
  "doctors_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 776,
    "y": 128
  },
  "dog_park": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 462,
    "y": 128
  },
  "dog_park_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 810,
    "y": 128
  },
  "dot_10": {
    "height": 20,
    "pixelRatio": 2,
    "width": 20,
    "x": 106,
    "y": 498
  },
  "dot_11": {
    "height": 22,
    "pixelRatio": 2,
    "width": 22,
    "x": 84,
    "y": 498
  },
  "dot_9": {
    "height": 18,
    "pixelRatio": 2,
    "width": 18,
    "x": 126,
    "y": 498
  },
  "drinking_water": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 252,
    "y": 170
  },
  "drinking_water_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 844,
    "y": 128
  },
  "embassy": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 294,
    "y": 170
  },
  "embassy_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 878,
    "y": 128
  },
  "entrance": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 228,
    "y": 422
  },
  "entrance_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 804,
    "y": 338
  },
  "fast_food": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 336,
    "y": 170
  },
  "fast_food_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 912,
    "y": 128
  },
  "ferry": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 266,
    "y": 422
  },
  "ferry_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 834,
    "y": 338
  },
  "fire_station": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 378,
    "y": 170
  },
  "fire_station_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 946,
    "y": 128
  },
  "florist": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 420,
    "y": 170
  },
  "fuel": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 304,
    "y": 422
  },
  "fuel_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 864,
    "y": 338
  },
  "furniture": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 462,
    "y": 170
  },
  "garden": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 252,
    "y": 212
  },
  "garden_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 980,
    "y": 128
  },
  "gift": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 294,
    "y": 212
  },
  "gift_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 504,
    "y": 170
  },
  "golf": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 336,
    "y": 212
  },
  "golf_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 538,
    "y": 170
  },
  "grocery": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 378,
    "y": 212
  },
  "grocery_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 572,
    "y": 170
  },
  "hairdresser": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 420,
    "y": 212
  },
  "hairdresser_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 606,
    "y": 170
  },
  "harbor": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 342,
    "y": 422
  },
  "harbor_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 894,
    "y": 338
  },
  "heart": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 462,
    "y": 212
  },
  "heart_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 170
  },
  "heliport": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 380,
    "y": 422
  },
  "heliport_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 924,
    "y": 338
  },
  "hospital": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 254,
    "y": 0
  },
  "hospital_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 674,
    "y": 170
  },
  "ice_cream": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 296,
    "y": 0
  },
  "ice_cream_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 708,
    "y": 170
  },
  "industry": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 418,
    "y": 422
  },
  "industry_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 954,
    "y": 338
  },
  "information": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 338,
    "y": 0
  },
  "information_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 742,
    "y": 170
  },
  "laundry": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 380,
    "y": 0
  },
  "laundry_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 776,
    "y": 170
  },
  "library": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 422,
    "y": 0
  },
  "library_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 810,
    "y": 170
  },
  "lighthouse": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 464,
    "y": 0
  },
  "lighthouse_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 844,
    "y": 170
  },
  "lodging": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 254
  },
  "lodging_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 878,
    "y": 170
  },
  "mall": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
  "mall:11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 254
  },
  "marker": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 456,
    "y": 422
  },
  "marker_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 984,
    "y": 338
  },
  "monument": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 42,
    "y": 254
  },
  "monument_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 912,
    "y": 170
  },
  "mountain": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 84,
    "y": 254
  },
  "mountain_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 946,
    "y": 170
  },
  "museum": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 126,
    "y": 254
  },
  "museum_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 980,
    "y": 170
  },
  "music": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 168,
    "y": 254
  },
  "music_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 504,
    "y": 212
  },
  "oneway": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 210,
    "y": 254
  },
  "park": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 252,
    "y": 254
  },
  "park_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 538,
    "y": 212
  },
  "parking": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 0,
    "y": 460
  },
  "parking_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 484,
    "y": 380
  },
  "parking_garage": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 38,
    "y": 460
  },
  "parking_garage_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 514,
    "y": 380
  },
  "pedestrian_polygon": {
    "height": 128,
    "pixelRatio": 2,
    "width": 128,
    "x": 0,
    "y": 0
  },
  "pharmacy": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 294,
    "y": 254
  },
  "pharmacy_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 572,
    "y": 212
  },
  "picnic_site": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 336,
    "y": 254
  },
  "picnic_site_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 606,
    "y": 212
  },
  "pitch": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 378,
    "y": 254
  },
  "pitch_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 212
  },
  "place_of_worship": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 420,
    "y": 254
  },
  "place_of_worship_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 674,
    "y": 212
  },
  "playground": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 462,
    "y": 254
  },
  "playground_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 708,
    "y": 212
  },
  "police": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 296
  },
  "police_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 742,
    "y": 212
  },
  "post": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 42,
    "y": 296
  },
  "post_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 776,
    "y": 212
  },
  "post_office": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 42,
    "y": 296
  },
  "post_office_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 776,
    "y": 212
  },
  "parcel_locker": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 42,
    "y": 296
  },
  "parcel_locker_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 776,
    "y": 212
  },
  "post_box": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 42,
    "y": 296
  },
  "post_box_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 776,
    "y": 212
  },
  "prison": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 84,
    "y": 296
  },
  "prison_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 810,
    "y": 212
  },
  "kiosk": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
  "kiosk_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 254
  },
  "railway": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 76,
    "y": 460
  },
  "railway_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 544,
    "y": 380
  },
  "railway_light": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 114,
    "y": 460
  },
  "railway_light_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 574,
    "y": 380
  },
  "railway_metro": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 152,
    "y": 460
  },
  "railway_metro_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 604,
    "y": 380
  },
  "ranger_station": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 126,
    "y": 296
  },
  "ranger_station_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 844,
    "y": 212
  },
  "religious_christian": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 168,
    "y": 296
  },
  "religious_christian_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 878,
    "y": 212
  },
  "religious_jewish": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 210,
    "y": 296
  },
  "religious_jewish_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 912,
    "y": 212
  },
  "religious_muslim": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 252,
    "y": 296
  },
  "religious_muslim_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 946,
    "y": 212
  },
  "restaurant": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 294,
    "y": 296
  },
  "restaurant_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 980,
    "y": 212
  },
  "road_1": {
    "height": 28,
    "pixelRatio": 2,
    "width": 28,
    "x": 996,
    "y": 296
  },
  "road_2": {
    "height": 28,
    "pixelRatio": 2,
    "width": 40,
    "x": 874,
    "y": 380
  },
  "road_3": {
    "height": 28,
    "pixelRatio": 2,
    "width": 51,
    "x": 914,
    "y": 380
  },
  "road_4": {
    "height": 28,
    "pixelRatio": 2,
    "width": 62,
    "x": 506,
    "y": 0
  },
  "road_5": {
    "height": 28,
    "pixelRatio": 2,
    "width": 72,
    "x": 568,
    "y": 0
  },
  "road_6": {
    "height": 28,
    "pixelRatio": 2,
    "width": 80,
    "x": 640,
    "y": 0
  },
  "roadblock": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 336,
    "y": 296
  },
  "roadblock_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 504,
    "y": 254
  },
  "rocket": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 378,
    "y": 296
  },
  "rocket_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 538,
    "y": 254
  },
  "school": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 420,
    "y": 296
  },
  "school_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 572,
    "y": 254
  },
  "shelter": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 462,
    "y": 296
  },
  "shelter_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 606,
    "y": 254
  },
  "shop": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
  "shop_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 254
  },
  "skiing": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 42,
    "y": 338
  },
  "skiing_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 674,
    "y": 254
  },
  "soccer": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 84,
    "y": 338
  },
  "soccer_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 708,
    "y": 254
  },
  "square": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 190,
    "y": 460
  },
  "square_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 634,
    "y": 380
  },
  "square_stroked": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 228,
    "y": 460
  },
  "square_stroked_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 664,
    "y": 380
  },
  "stadium": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 126,
    "y": 338
  },
  "stadium_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 742,
    "y": 254
  },
  "star": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 266,
    "y": 460
  },
  "star_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 694,
    "y": 380
  },
  "star_stroked": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 304,
    "y": 460
  },
  "star_stroked_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 724,
    "y": 380
  },
  "stationery": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
 "stationery_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 254
  }, 
  "shoes": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
  "shoes_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 254
  },
  "suitcase": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 168,
    "y": 338
  },
  "suitcase_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 776,
    "y": 254
  },
  "sushi": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 210,
    "y": 338
  },
  "sushi_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 810,
    "y": 254
  },
  "swimming": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 252,
    "y": 338
  },
  "swimming_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 844,
    "y": 254
  },
  "tailor": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 420,
    "y": 212
  },
  "tailor_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 606,
    "y": 170
  },
  "telephone": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 294,
    "y": 338
  },
  "telephone_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 878,
    "y": 254
  },
  "tennis": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 336,
    "y": 338
  },
  "tennis_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 912,
    "y": 254
  },
  "theatre": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 378,
    "y": 338
  },
  "theatre_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 946,
    "y": 254
  },
  "tobacco": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
  "tobacco_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 254
  },
  "toilets": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 420,
    "y": 338
  },
  "toilets_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 980,
    "y": 254
  },
  "town_hall": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 462,
    "y": 338
  },
  "town_hall_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 504,
    "y": 296
  },
  "townhall": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 462,
    "y": 338
  },
  "townhall_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 504,
    "y": 296
  },
  "triangle": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 342,
    "y": 460
  },
  "triangle_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 754,
    "y": 380
  },
  "triangle_stroked": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 380,
    "y": 460
  },
  "triangle_stroked_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 784,
    "y": 380
  },
  "us-highway_1": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 538,
    "y": 296
  },
  "us-highway_2": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 572,
    "y": 296
  },
  "us-highway_3": {
    "height": 34,
    "pixelRatio": 2,
    "width": 42,
    "x": 606,
    "y": 296
  },
  "us-interstate_1": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 648,
    "y": 296
  },
  "us-interstate_2": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 682,
    "y": 296
  },
  "us-interstate_3": {
    "height": 34,
    "pixelRatio": 2,
    "width": 42,
    "x": 716,
    "y": 296
  },
  "us-state_1": {
    "height": 28,
    "pixelRatio": 2,
    "width": 34,
    "x": 965,
    "y": 380
  },
  "us-state_2": {
    "height": 28,
    "pixelRatio": 2,
    "width": 44,
    "x": 720,
    "y": 0
  },
  "us-state_3": {
    "height": 28,
    "pixelRatio": 2,
    "width": 54,
    "x": 764,
    "y": 0
  },
  "us-state_4": {
    "height": 28,
    "pixelRatio": 2,
    "width": 64,
    "x": 818,
    "y": 0
  },
  "us-state_5": {
    "height": 28,
    "pixelRatio": 2,
    "width": 74,
    "x": 882,
    "y": 0
  },
  "us-state_6": {
    "height": 28,
    "pixelRatio": 2,
    "width": 84,
    "x": 0,
    "y": 498
  },
  "veterinary": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 380
  },
  "veterinary_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 758,
    "y": 296
  },
  "volcano": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 42,
    "y": 380
  },
  "volcano_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 792,
    "y": 296
  },
  "warehouse": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 418,
    "y": 460
  },
  "warehouse_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 814,
    "y": 380
  },
  "waste_basket": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 84,
    "y": 380
  },
  "waste_basket_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 826,
    "y": 296
  },
  "water": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 126,
    "y": 380
  },
  "water_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 860,
    "y": 296
  },
  "wetland": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 168,
    "y": 380
  },
  "wetland_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 894,
    "y": 296
  },
  "wetland_bg_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 844,
    "y": 380
  },
  "wheelchair": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 210,
    "y": 380
  },
  "wheelchair_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 928,
    "y": 296
  },
  "zoo": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 252,
    "y": 380
  },
  "zoo_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 962,
    "y": 296
  },
  "tram_stop": {
    "height": 38,
    "pixelRatio": 2,
    "width": 38,
    "x": 446,
    "y": 380
  },
  "tram_stop_11": {
    "height": 30,
    "pixelRatio": 2,
    "width": 30,
    "x": 594,
    "y": 338
  },
  "university": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 252,
    "y": 128
  },
  "university_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 128
  },
  "kindergarten": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 420,
    "y": 296
  },
  "kindergarten_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 572,
    "y": 254
  },
    "grave_yard": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 126,
    "y": 212
  },
  "grave_yard_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 504,
    "y": 128
  },
  "community_centre": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
  "mobile_phone": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
  "mobile_phone_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 254
  },
  "hearing_aids": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 254,
    "y": 0
  },
  "hearing_aids_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 766,
    "y": 128
  },
  "optician": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
  "optician_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 254
  },
  "tattoo": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
  "tattoo_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 254
  },
  "copyshop": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
  "copyshop_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 640,
    "y": 254
  },
  "sports": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 84,
    "y": 338
  },
  "sports_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 708,
    "y": 254
  },
  "computer": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 0,
    "y": 338
  },
  "computer_11": {
    "height": 17,
    "pixelRatio": 1,
    "width": 17,
    "x": 640,
    "y": 254
  },
  "clinic": {
    "height": 42,
    "pixelRatio": 2,
    "width": 42,
    "x": 420,
    "y": 128
  },
    "clinic_11": {
    "height": 34,
    "pixelRatio": 2,
    "width": 34,
    "x": 776,
    "y": 128
  }

}
```

## `static/sprite.json`

Nota: File JSON: verificare dal contenuto se è configurazione o dato.

```text
{
  "accountant": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 0
  },
  "advertising_agency": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 0
  },
  "alcohol": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 0
  },
  "alpine_hut": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 0
  },
  "antiques": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 0
  },
  "architect": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 0
  },
  "art": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 0
  },
  "arts_centre": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 0
  },
  "artwork": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 0
  },
  "athletics": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 0
  },
  "atm": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 0
  },
  "attraction": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 0
  },
  "bag": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 0
  },
  "bakery": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 0
  },
  "bank": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 0
  },
  "bar": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 0
  },
  "basin": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 0
  },
  "basketball": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 0
  },
  "bbq": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 0
  },
  "beachvolleyball": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 0
  },
  "beauty": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 0
  },
  "beverages": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 24
  },
  "bicycle": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 48
  },
  "bicycle_parking": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 72
  },
  "bicycle_rental": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 96
  },
  "biergarten": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 120
  },
  "bmx": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 144
  },
  "board": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 168
  },
  "bollard": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 192
  },
  "books": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 216
  },
  "border_control": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 240
  },
  "boutique": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 264
  },
  "brownfield": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 288
  },
  "bus_station": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 312
  },
  "bus_stop": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 336
  },
  "butcher": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 360
  },
  "cafe": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 384
  },
  "camp_site": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 408
  },
  "canoe": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 432
  },
  "car": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 456
  },
  "car_parts": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 0,
    "y": 480
  },
  "car_repair": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 24
  },
  "caravan_site": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 24
  },
  "carpet": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 24
  },
  "castle": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 24
  },
  "cemetery": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 24
  },
  "chalet": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 24
  },
  "charging_station": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 24
  },
  "chemist": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 24
  },
  "chess": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 24
  },
  "chocolate": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 24
  },
  "christian": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 24
  },
  "cinema": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 24
  },
  "climbing": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 24
  },
  "clinic": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 24
  },
  "clothes": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 24
  },
  "community_centre": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 24
  },
  "company": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 24
  },
  "computer": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 24
  },
  "confectionery": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 24
  },
  "convenience": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 24
  },
  "copyshop": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 48
  },
  "cosmetics": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 72
  },
  "courthouse": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 96
  },
  "cycle_barrier": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 120
  },
  "cycling": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 144
  },
  "deli": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 168
  },
  "dentist": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 192
  },
  "department_store": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 216
  },
  "diving": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 240
  },
  "doctors": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 264
  },
  "dog_park": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 288
  },
  "doityourself": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 312
  },
  "drinking_water": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 336
  },
  "dry_cleaning": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 360
  },
  "educational_institution": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 384
  },
  "electronics": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 408
  },
  "employment_agency": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 432
  },
  "equestrian": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 456
  },
  "escape_game": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 24,
    "y": 480
  },
  "estate_agent": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 48
  },
  "fast_food": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 48
  },
  "ferry_terminal": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 48
  },
  "field_hockey": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 48
  },
  "financial": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 48
  },
  "florist": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 48
  },
  "foundation": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 48
  },
  "fuel": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 48
  },
  "furniture": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 48
  },
  "gallery": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 48
  },
  "garden": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 48
  },
  "garden_centre": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 48
  },
  "gate": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 48
  },
  "gift": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 48
  },
  "golf": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 48
  },
  "government": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 48
  },
  "grave_yard": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 48
  },
  "greengrocer": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 48
  },
  "guest_house": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 48
  },
  "guidepost": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 72
  },
  "gymnastics": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 96
  },
  "hairdresser": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 120
  },
  "halt": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 144
  },
  "handball": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 168
  },
  "hardware": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 192
  },
  "hearing_aids": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 216
  },
  "hospital": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 240
  },
  "hostel": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 264
  },
  "hotel": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 288
  },
  "ice_cream": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 312
  },
  "ice_hockey": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 336
  },
  "information": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 360
  },
  "insurance": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 384
  },
  "interior_decoration": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 408
  },
  "it": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 432
  },
  "jewelry": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 456
  },
  "jewish": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 48,
    "y": 480
  },
  "karting": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 72
  },
  "kindergarten": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 72
  },
  "kiosk": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 72
  },
  "laundry": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 72
  },
  "lawyer": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 72
  },
  "library": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 72
  },
  "lift_gate": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 72
  },
  "mall": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 72
  },
  "map": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 72
  },
  "marina": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 72
  },
  "marketplace": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 72
  },
  "massage": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 72
  },
  "miniature_golf": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 72
  },
  "mobile_phone": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 72
  },
  "monument": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 72
  },
  "motel": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 72
  },
  "motocross": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 72
  },
  "motorcycle": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 72
  },
  "motorcycle_parking": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 96
  },
  "multi": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 120
  },
  "museum": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 144
  },
  "musical_instrument": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 168
  },
  "newsagent": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 192
  },
  "ngo": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 216
  },
  "nightclub": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 240
  },
  "office": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 264
  },
  "optician": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 288
  },
  "outdoor": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 312
  },
  "paint": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 336
  },
  "parcel_locker": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 360
  },
  "park": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 384
  },
  "parking": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 408
  },
  "perfumery": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 432
  },
  "pet": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 456
  },
  "pharmacy": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 72,
    "y": 480
  },
  "photo": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 96
  },
  "pitch": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 96
  },
  "playground": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 96
  },
  "police": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 96
  },
  "political_party": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 96
  },
  "post_box": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 96
  },
  "post_office": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 96
  },
  "prison": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 96
  },
  "pub": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 96
  },
  "public_building": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 96
  },
  "recycling": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 96
  },
  "religion": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 96
  },
  "reservoir": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 96
  },
  "restaurant": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 96
  },
  "route_marker": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 96
  },
  "ruins": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 96
  },
  "running": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 96
  },
  "school": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 120
  },
  "scuba_diving": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 144
  },
  "second_hand": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 168
  },
  "shelter": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 192
  },
  "shoes": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 216
  },
  "skateboard": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 240
  },
  "skiing": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 264
  },
  "soccer": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 288
  },
  "sports": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 312
  },
  "stadium": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 336
  },
  "stationery": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 360
  },
  "subway": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 384
  },
  "supermarket": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 408
  },
  "swimming": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 432
  },
  "swimming_pool": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 456
  },
  "table_tennis": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 96,
    "y": 480
  },
  "tattoo": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 120
  },
  "tax_advisor": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 144,
    "y": 120
  },
  "taxi": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 168,
    "y": 120
  },
  "telephone": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 192,
    "y": 120
  },
  "tennis": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 216,
    "y": 120
  },
  "terminal": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 240,
    "y": 120
  },
  "theatre": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 264,
    "y": 120
  },
  "theme_park": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 288,
    "y": 120
  },
  "ticket": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 312,
    "y": 120
  },
  "tobacco": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 336,
    "y": 120
  },
  "toilets": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 360,
    "y": 120
  },
  "toll_booth": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 384,
    "y": 120
  },
  "townhall": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 408,
    "y": 120
  },
  "toys": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 432,
    "y": 120
  },
  "travel_agency": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 456,
    "y": 120
  },
  "university": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 480,
    "y": 120
  },
  "veterinary": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 144
  },
  "video_games": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 168
  },
  "viewpoint": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 192
  },
  "waste_basket": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 216
  },
  "watches": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 240
  },
  "water_park": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 264
  },
  "weapons": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 288
  },
  "wholesale": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 312
  },
  "wine": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 336
  },
  "zoo": {
    "height": 24,
    "pixelRatio": 1,
    "width": 24,
    "x": 120,
    "y": 360
  }
}
```

## `static/sprite@2x.json`

Nota: File JSON: verificare dal contenuto se è configurazione o dato.

```text
{
  "accountant": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 0
  },
  "advertising_agency": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 0
  },
  "alcohol": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 0
  },
  "alpine_hut": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 0
  },
  "antiques": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 0
  },
  "architect": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 0
  },
  "art": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 0
  },
  "arts_centre": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 0
  },
  "artwork": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 0
  },
  "athletics": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 0
  },
  "atm": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 0
  },
  "attraction": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 0
  },
  "bag": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 0
  },
  "bakery": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 0
  },
  "bank": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 0
  },
  "bar": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 0
  },
  "basin": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 0
  },
  "basketball": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 0
  },
  "bbq": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 0
  },
  "beachvolleyball": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 0
  },
  "beauty": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 0
  },
  "beverages": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 48
  },
  "bicycle": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 96
  },
  "bicycle_parking": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 144
  },
  "bicycle_rental": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 192
  },
  "biergarten": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 240
  },
  "bmx": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 288
  },
  "board": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 336
  },
  "bollard": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 384
  },
  "books": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 432
  },
  "border_control": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 480
  },
  "boutique": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 528
  },
  "brownfield": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 576
  },
  "bus_station": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 624
  },
  "bus_stop": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 672
  },
  "butcher": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 720
  },
  "cafe": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 768
  },
  "camp_site": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 816
  },
  "canoe": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 864
  },
  "car": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 912
  },
  "car_parts": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 0,
    "y": 960
  },
  "car_repair": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 48
  },
  "caravan_site": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 48
  },
  "carpet": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 48
  },
  "castle": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 48
  },
  "cemetery": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 48
  },
  "chalet": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 48
  },
  "charging_station": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 48
  },
  "chemist": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 48
  },
  "chess": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 48
  },
  "chocolate": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 48
  },
  "christian": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 48
  },
  "cinema": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 48
  },
  "climbing": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 48
  },
  "clinic": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 48
  },
  "clothes": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 48
  },
  "community_centre": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 48
  },
  "company": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 48
  },
  "computer": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 48
  },
  "confectionery": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 48
  },
  "convenience": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 48
  },
  "copyshop": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 96
  },
  "cosmetics": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 144
  },
  "courthouse": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 192
  },
  "cycle_barrier": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 240
  },
  "cycling": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 288
  },
  "deli": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 336
  },
  "dentist": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 384
  },
  "department_store": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 432
  },
  "diving": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 480
  },
  "doctors": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 528
  },
  "dog_park": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 576
  },
  "doityourself": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 624
  },
  "drinking_water": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 672
  },
  "dry_cleaning": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 720
  },
  "educational_institution": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 768
  },
  "electronics": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 816
  },
  "employment_agency": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 864
  },
  "equestrian": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 912
  },
  "escape_game": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 48,
    "y": 960
  },
  "estate_agent": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 96
  },
  "fast_food": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 96
  },
  "ferry_terminal": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 96
  },
  "field_hockey": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 96
  },
  "financial": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 96
  },
  "florist": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 96
  },
  "foundation": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 96
  },
  "fuel": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 96
  },
  "furniture": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 96
  },
  "gallery": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 96
  },
  "garden": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 96
  },
  "garden_centre": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 96
  },
  "gate": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 96
  },
  "gift": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 96
  },
  "golf": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 96
  },
  "government": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 96
  },
  "grave_yard": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 96
  },
  "greengrocer": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 96
  },
  "guest_house": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 96
  },
  "guidepost": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 144
  },
  "gymnastics": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 192
  },
  "hairdresser": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 240
  },
  "halt": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 288
  },
  "handball": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 336
  },
  "hardware": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 384
  },
  "hearing_aids": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 432
  },
  "hospital": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 480
  },
  "hostel": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 528
  },
  "hotel": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 576
  },
  "ice_cream": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 624
  },
  "ice_hockey": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 672
  },
  "information": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 720
  },
  "insurance": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 768
  },
  "interior_decoration": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 816
  },
  "it": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 864
  },
  "jewelry": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 912
  },
  "jewish": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 96,
    "y": 960
  },
  "karting": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 144
  },
  "kindergarten": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 144
  },
  "kiosk": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 144
  },
  "laundry": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 144
  },
  "lawyer": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 144
  },
  "library": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 144
  },
  "lift_gate": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 144
  },
  "mall": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 144
  },
  "map": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 144
  },
  "marina": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 144
  },
  "marketplace": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 144
  },
  "massage": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 144
  },
  "miniature_golf": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 144
  },
  "mobile_phone": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 144
  },
  "monument": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 144
  },
  "motel": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 144
  },
  "motocross": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 144
  },
  "motorcycle": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 144
  },
  "motorcycle_parking": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 192
  },
  "multi": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 240
  },
  "museum": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 288
  },
  "musical_instrument": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 336
  },
  "newsagent": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 384
  },
  "ngo": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 432
  },
  "nightclub": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 480
  },
  "office": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 528
  },
  "optician": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 576
  },
  "outdoor": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 624
  },
  "paint": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 672
  },
  "parcel_locker": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 720
  },
  "park": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 768
  },
  "parking": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 816
  },
  "perfumery": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 864
  },
  "pet": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 912
  },
  "pharmacy": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 144,
    "y": 960
  },
  "photo": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 192
  },
  "pitch": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 192
  },
  "playground": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 192
  },
  "police": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 192
  },
  "political_party": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 192
  },
  "post_box": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 192
  },
  "post_office": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 192
  },
  "prison": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 192
  },
  "pub": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 192
  },
  "public_building": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 192
  },
  "recycling": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 192
  },
  "religion": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 192
  },
  "reservoir": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 192
  },
  "restaurant": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 192
  },
  "route_marker": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 192
  },
  "ruins": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 192
  },
  "running": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 192
  },
  "school": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 240
  },
  "scuba_diving": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 288
  },
  "second_hand": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 336
  },
  "shelter": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 384
  },
  "shoes": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 432
  },
  "skateboard": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 480
  },
  "skiing": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 528
  },
  "soccer": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 576
  },
  "sports": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 624
  },
  "stadium": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 672
  },
  "stationery": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 720
  },
  "subway": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 768
  },
  "supermarket": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 816
  },
  "swimming": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 864
  },
  "swimming_pool": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 912
  },
  "table_tennis": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 192,
    "y": 960
  },
  "tattoo": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 240
  },
  "tax_advisor": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 288,
    "y": 240
  },
  "taxi": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 336,
    "y": 240
  },
  "telephone": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 384,
    "y": 240
  },
  "tennis": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 432,
    "y": 240
  },
  "terminal": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 480,
    "y": 240
  },
  "theatre": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 528,
    "y": 240
  },
  "theme_park": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 576,
    "y": 240
  },
  "ticket": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 624,
    "y": 240
  },
  "tobacco": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 672,
    "y": 240
  },
  "toilets": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 720,
    "y": 240
  },
  "toll_booth": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 768,
    "y": 240
  },
  "townhall": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 816,
    "y": 240
  },
  "toys": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 864,
    "y": 240
  },
  "travel_agency": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 912,
    "y": 240
  },
  "university": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 960,
    "y": 240
  },
  "veterinary": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 288
  },
  "video_games": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 336
  },
  "viewpoint": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 384
  },
  "waste_basket": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 432
  },
  "watches": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 480
  },
  "water_park": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 528
  },
  "weapons": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 576
  },
  "wholesale": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 624
  },
  "wine": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 672
  },
  "zoo": {
    "height": 48,
    "pixelRatio": 2,
    "width": 48,
    "x": 240,
    "y": 720
  }
}
```
