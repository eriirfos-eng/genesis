# Earth Stablecoin (ESC) — Framework v0.1 (One‑Pager)
**Status:** Draft for review  
**Maintainer:** RFI‑IRFOS (/genesis)  
**Timestamp:** Wednesday-2025-Sep-03T:03:36:00PMZ

## 1) Purpose
A currency that stays stable, resists manipulation, and serves daily life. ESC links money supply to human reality rather than to discretionary monetary policy or speculative cycles.

## 2) Design goals
- **Fairness:** issuance follows birth events and retires at death or at 100 years.  
- **Stability:** physical notes and digital units stay at 1:1 parity. purchasing power stability pursued via redeemability or a goods index.  
- **Transparency:** open source clients, public specs, verifiable audits.  
- **Sustainability:** issuance grows with population. no discretionary printing.

## 3) System overview
- **Dual form:** physical notes and digital ledger units. strict 1:1 convertibility at exchange points.  
- **Units:** ESC is the base unit. subunits optional: seed = 1⁄100, grain = 1⁄10 000.  
- **Networks:** retail payments use privacy‑preserving bearer instruments. larger transfers use an auditable ledger.

## 4) Monetary rule (demography‑linked)
- **Issuance:** +50 ESC per verified live birth.  
- **Retirement:** −50 ESC at verified death, or at age 100 if no liveness proof.  
- **Implication:** circulating supply S ≈ 50 × (living population).  
- **Governance:** parameters (50, 100 years, verification rules) are set in a public constitution and can change only via supermajority.

## 5) Identity and verification
- **Birth proof:** civil registry issues a verifiable credential. guardians mint 50 ESC against that credential.  
- **Death proof:** civil registry or health authority issues a verifiable credential. fallback retirement at 100 years.  
- **Privacy:** credentials are checked via zero‑knowledge proofs where possible. personal data does not sit on the payment rails.

## 6) Stability mechanism
ESC must hold value in the real world. Two compatible options:
- **Option A: Redeemability reserve.** Federated guardians hold a conservative reserve basket and make two‑way markets for ESC. weekly proof‑of‑reserves with independent auditors.  
- **Option B: Earth Basket Index (EBX).** An index of essentials: a calories proxy, a kWh proxy, and a base metal proxy. independent oracles publish medians. market‑makers keep ESC near EBX by quoting two‑way prices.  
Note: both options can run together in pilots.

## 7) Transactions and privacy
- **Cash tier:** Chaumian eCash or equivalent for small payments. NFC cards and paper tokens work offline and sync later.  
- **Account tier:** ledger accounts for larger payments. full history visible to the account holder, selective disclosure to others.

## 8) Governance
- **Guardians:** local cooperatives that operate mints and exchange points. entry requires a bond and ongoing proofs.  
- **Audits:** regular Merkle proofs for reserves (if used). code audits published.  
- **Oracle quorum:** five or more independent data sources. medianization with circuit breakers.

## 9) Physical currency
- **Exchange network:** repurpose existing exchange offices and co‑ops.  
- **Notes:** anti‑counterfeiting features and serials that map to issuance epochs.  
- **Rules:** 1:1 swap with digital units at posted rates and fees that are public.

## 10) Roadmap
- **Pilot:** 3 to 5 guardians, 100 merchants, 1000 users. wallet for cash tier and account tier. public dashboard.  
- **Stage 1:** expand guardians and market‑makers. publish EBX v0 method.  
- **Stage 2:** cross‑border corridors. independent audits.  
- **Stage 3:** national programs that adopt ESC rails while keeping the cash tier alive.

## 11) Threat model
- **Registry attacks:** duplicated or fake birth credentials. mitigations: cross‑checks, revocation registries, penalties.  
- **Guardian collusion:** under‑reserving or censoring. mitigations: rotation, bonds, multi‑jurisdiction keys.  
- **Oracle games:** price feed manipulation. mitigations: diverse sources, medians, halts.  
- **Policy pressure:** attempts to outlaw the cash tier. mitigation: decentralization, open hardware, legal defense funds.

## 12) Open questions
- Appropriate size of issuance per birth to align with EBX target.  
- Liveness proof cadence below the 100‑year fallback.  
- Redemption governance for people without formal documents.  
- Jurisdictions for the first pilots and their legal posture.

---
**Notes:** This document summarizes a protocol vision that combines demography‑linked supply with privacy‑preserving payments. Political initiatives such as inter‑state debt forgiveness are complementary programs and sit outside the core technical protocol.
