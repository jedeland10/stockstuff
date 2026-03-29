# StonkLens — Affärsplan

## Produkt

**URL:** [stonklens.com](https://stonklens.com)

Aktie-screener fokuserad på nordiska aktier. Hjälper investerare hitta undervärderade och finansiellt starka bolag genom beprövade analysmodeller.

---

## Nuläge

- 497 nordiska aktier
- Data från Yahoo Finance API, uppdateras 4 ggr/dag
- Magic Formula (Joel Greenblatt) — rankar aktier på earnings yield + return on capital
- Piotroski F-Score — utvärderar finansiell styrka via 9 binära tester (lönsamhet, hävstång, effektivitet)
- Highlights-sida: sammanfattning, topp 10 gainers/losers, senaste rapporter, sektorsöversikt
- Watchlist
- Excel-export
- Inga användarkonton
- Ingen monetarisering

---

## Marknad

Nordiska aktier är en underservad nisch — de flesta screeners fokuserar på US-marknaden. Validerad betalningsvilja: liknande tjänster tar ~200 kr/mån i Norden.

---

## Prismodell: Freemium

### Gratis (konto krävs)

- Screener med topp 100 aktier
- Grundläggande nyckeltal
- Watchlist (max 10 aktier)
- Highlights-sida med begränsad data

### Premium (99–149 kr/mån)

- Alla 497+ aktier (mål: 800+)
- Magic Formula + Piotroski F-Score + fler rating-formler
- Spidergraph med 4–5 ratings per aktie
- Export till Excel
- Nyhetsflöde
- Rapportdata
- Obegränsad watchlist
- Notifikationer vid kursrörelser för bevakade aktier

---

## Feature-roadmap

### Prio 1 — Krävs för första intäkt

1. **Användarhantering + betalvägg** — Clerk/NextAuth + Stripe. Utan detta finns ingen intäkt och ingen användarbas att konvertera.
2. **Utöka antalet aktier** — Från 497 till 800+. Kvantitet är ett enkelt och tydligt säljargument.
3. **Highlights-sida bakom premium** — Redan implementerad, lägg bakom betalvägg. "Sparar mig tid"-features är det folk betalar för.
4. **Spidergraph med flera ratings** — Visuellt tilltalande, ser proffsigt ut, bra för screenshots och marknadsföring.

### Prio 2 — Bygg när betalande användare finns

5. **Nyhetsflöde** — Kräver scraping eller finansiellt nyhets-API.
6. **Rapportdata** — Kvartals- och årsrapporter kopplade till aktier.
7. **Notifikationer** — Kräver aggressivare schemaläggning och push-infrastruktur.

---

## Konto-strategi

Kräv konto för allt utom landningssidan. Anledning: utan konton finns det noll användare att konvertera till betalande. Håll det friktionsfritt — "logga in med Google" räcker som steg ett. En e-postlista över registrerade användare är den mest värdefulla tillgången tidigt.

---

## Distribution

- **X/Twitter** — Korta inlägg med screenshots från StonkLens, t.ex. "Topp 5 undervärderade nordiska aktier enligt Magic Formula just nu". Gratis, visar produkten, når rätt målgrupp.
- **Aktie-communities** — Avanza-forum, r/ISKbansen, svenska aktie-Twitter.
- **SEO** — Blogginlägg optimerade för söktermer som driver organisk trafik till verktyget.

---

## Intäktspotential

| Betalande användare | Pris/mån | Månadsintäkt | Årsintäkt |
|---------------------|---------|-------------|-----------|
| 50 | 149 kr | 7 450 kr | 89 400 kr |
| 100 | 149 kr | 14 900 kr | 178 800 kr |
| 200 | 149 kr | 29 800 kr | 357 600 kr |

---

## Konkurrensfördel

- Nischfokus: nordiska aktier istället för den övermättade US-marknaden
- Beprövade analysmodeller (Magic Formula, Piotroski) som inte finns lättillgängliga för nordiska bolag
- Snabb utvecklingscykel — soloutvecklare med AI-verktyg (Claude Code) ger kort tid från idé till feature
- Lägre pris än befintliga alternativ (~200 kr/mån) med jämförbar eller bättre funktionalitet
