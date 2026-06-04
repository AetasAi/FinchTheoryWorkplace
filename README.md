# Finch Theory — Workplace

**Live site:** https://finchtheory.com  
**Repo:** (set when GitHub repo is created)  
**Deployed via:** GitHub Pages (automatic on push to `main`)  
**Contact:** matthew.steiner@finchtheory.com

---

## Overview

Finch Theory is a consultancy-led business performance service for SMEs, LLPs, and professional practices. It identifies and fixes the hidden cost of financial pressure in the workforce — in productivity, retention, and leadership time. Where regulated financial advice is required, this is provided by an FCA-authorised adviser.

This site is a rebrand of the Aetas in the Workplace codebase, converted to the Finch Theory visual identity (Cormorant Garamond / Montserrat, black / gold / warm white palette).

---

## Find-and-replace checklist before go-live

| Placeholder | Replace with |
|---|---|
| `BOOKING_LINK_PLACEHOLDER` | Live GoHighLevel booking widget URL |
| `matthew.steiner@finchtheory.com` | Live email address |
| `/assets/finch-theory-mark.png` | Actual Finch Theory logo file |
| `/og-image.png` | New Finch Theory OG image (1200×630) |
| `finchtheory.com` | Confirmed live domain |

---

## Design system

Pure static HTML, CSS, and vanilla JS. No build tools or frameworks.

### Colours

```css
--ft-black:       #0e0e0e   /* Primary — backgrounds, nav, footer */
--ft-gold:        #a58d5c   /* Accent — eyebrows, CTAs, borders */
--ft-gold-light:  #c4aa7a   /* Lighter gold for italic highlights */
--warm-white:     #faf8f5   /* Page background */
--warm-grey:      #f3f0eb   /* Alternate section background */
--mid-grey:       #e2ddd6   /* Borders, dividers */
--text-secondary: #6b6560   /* Body text */
```

### Typography

| Role | Font | Weights |
|---|---|---|
| Display, headings | Cormorant Garamond | 300, 400, 300 italic, 400 italic |
| Body, UI, labels, nav | Montserrat | 300, 400, 500, 600 |

All loaded via Google Fonts.

---

## Assets required

Place these in `/assets/` before deployment:

- `finch-theory-mark.png` — logo mark (40×40px nav size, supply 2× for retina)
- `/og-image.png` — OG social image (1200×630)
- `/icons/favicon-32.png`, `/icons/favicon-16.png`, `/icons/apple-touch-icon.png`
- `/assets/js/analytics.js` — GA4 snippet (copy from existing setup, update measurement ID)

---

## Navigation

All pages share this nav order:

```
Limited companies | LLPs | Pricing | Calculator | Diagnostic | Insights | FAQs | Book a Review
```

Nav CTA: `BOOKING_LINK_PLACEHOLDER`

The nav block is duplicated in every `.html` file. If any nav label or link changes, update all pages.

---

## Deployment

```bash
git add -A
git commit -m "Description of changes"
git push origin main
```

GitHub Pages deploys automatically. Takes 1–2 minutes.

**CNAME:** `finchtheory.com`  
**Branch:** `main` only

---

## Regulatory footer

All public pages include:

> Finch Theory provides workplace financial wellbeing, education, and consultancy services to employers. These services do not constitute regulated financial advice. Where regulated advice is required, this is provided separately by an FCA-authorised adviser.

*Update this if the regulated entity relationship is formalised.*
