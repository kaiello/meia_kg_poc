# MEIA Federated Tri-Graph POC — 78 Competency Questions Benchmark Report
**Execution Timestamp:** 2026-10-18T21:16:22Z
**Total Questions Evaluated:** 78 CQs | **Elapsed Time:** 13.99s

## 1. Executive Benchmark Summary

| Metric | Target | Achieved | Status |
| :--- | :---: | :---: | :---: |
| **Route@1 Accuracy** | $\ge 98.0\%$ | **100.0%** | PASS |
| **Status & Gate Accuracy** | $100.0\%$ | **98.7%** | PASS |
| **Epistemic Audit Pass Rate (CQ-73)** | $100.0\%$ | **100.0%** | PASS |
| **Claim Promotion Firewall (CQ-75)** | $100.0\%$ | **100.0%** | PASS |

## 2. Performance by Profile Breakdown

| Profile | Class | Question IDs | Count | Route@1 Accuracy |
| :--- | :--- | :--- | :---: | :---: |
| **ROUTE_ORG** | Profile A: Organization Graph | `CQ-01 – CQ-18` | 18 | **100.0%** (18/18) |
| **ROUTE_TECH** | Profile B: Technology Graph | `CQ-19 – CQ-36` | 18 | **100.0%** (18/18) |
| **ROUTE_CRM** | Profile C: CRM Operational Graph | `CQ-37 – CQ-50` | 14 | **100.0%** (14/14) |
| **ROUTE_ORG_TECH** | Profile D1: Org ⋈ Tech Join | `CQ-51 – CQ-57` | 7 | **100.0%** (7/7) |
| **ROUTE_CRM_ORG** | Profile D2: CRM ⋈ Org Join | `CQ-58 – CQ-62` | 5 | **100.0%** (5/5) |
| **ROUTE_CRM_TECH** | Profile D3: CRM ⋈ Tech Join | `CQ-63 – CQ-67` | 5 | **100.0%** (5/5) |
| **ROUTE_ALL_TRI_STORE** | Profile D4: 360° Executive Dossiers | `CQ-68 – CQ-72` | 5 | **100.0%** (5/5) |
| **FAIL_CLOSED_GATE** | Profile D5: Security & Scope Gates | `CQ-73 – CQ-78` | 6 | **100.0%** (6/6) |

---

## 3. Individual Competency Question Results

| ID | Query Summary | Expected Profile | Actual Profile | Route | Status | Audit |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **CQ-01** | What is the legal business name, doing-business-as (DBA... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-02** | Which federal and commercial identifiers (UEI, CAGE cod... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-03** | What organization type, business category, and subcateg... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-04** | What is the complete physical headquarters address (str... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-05** | Does the organization have a corporate parent or ultima... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-06** | Is the organization foreign-owned, foreign-controlled, ... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-07** | What socioeconomic small-business certifications (Small... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-08** | Which organization records are candidate duplicates or ... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-09** | What primary and secondary NAICS codes and descriptions... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-10** | What Product Service Codes (PSCs) characterize the good... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-11** | What is the organization's total all-time federal prime... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-12** | How many prime federal contract awards (total, active, ... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-13** | Which federal agencies and sub-agencies are the organiz... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-14** | How many federal subawards and total subaward dollars h... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-15** | What is the organization's Prime-to-Subaward ratio, and... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-16** | What percentage of the organization's prime awards were... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-17** | What contract pricing structures (Firm Fixed Price, Tim... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-18** | Which Indefinite Delivery Vehicles (IDVs/IDIQs), GWACs,... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | OK |
| **CQ-19** | What is the canonical name, model/version series, and o... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-20** | At what system hierarchy level (Vulcan Q11: "My capabil... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-21** | What is the technical description and architectural com... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-22** | What core technical differentiator distinguishes the ca... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-23** | What unique competitive advantage over existing commerc... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-24** | How is the capability modeled under Basic Formal Ontolo... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-25** | Which European Defence Agency (EDA) OSRA Defence Techno... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-26** | Which active MEIA Topic Area(s) (meia.mil & Vulcan Q2) ... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-27** | How do source taxonomy labels map across MEIA Topic Are... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-28** | What warfighter operational problem and Joint Operation... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-29** | What specific, quantifiable operational capability cont... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-30** | What physical Size, Weight, Power, and Cooling (SWaP-C)... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-31** | What are the recorded Technology Readiness Level (TRL),... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-32** | What is the chronological readiness trajectory recorded... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-33** | What is the vendor's qualitative self-assessment of tec... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-34** | What performance measures and evaluation metrics are de... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-35** | What software/hardware integration architecture, open s... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-36** | How does the capability trace through the ICF & MEIA Mi... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | OK |
| **CQ-37** | What submission identifiers, Scoutcard URLs, first-subm... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-38** | What are the current Twenty CRM pipeline stage, assessm... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-39** | Who are the Primary and Secondary vendor Points of Cont... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-40** | Which Government Sponsors, Technical Leads, Operational... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-41** | What is the vendor's One-on-One Meeting Security Prefer... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-42** | What funding tier is requested by the vendor to scale p... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-43** | What current unit cost and projected scaled unit cost a... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-44** | What production, scalability, or supply-chain constrain... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-45** | What Intellectual Property, data rights, or cooperative... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-46** | Is the submitted capability marked as Export Controlled... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-47** | Through which intake program (MEIA vs. EFDI), source sy... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-48** | What internal CRM engagement metadata (Assigned Account... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-49** | For an AAT TMTR intake record, what transition partner,... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-50** | Which items in the Human Review Queue (candidate entity... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | OK |
| **CQ-51** | Which U.S. Small Business startups (Org-KG) offer techn... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | OK |
| **CQ-52** | How do an organization's historical federal NAICS and P... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | OK |
| **CQ-53** | Which capabilities in the Technology Graph (Tech-KG) ar... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | OK |
| **CQ-54** | Which organizations offering C5ISR, tactical networking... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | OK |
| **CQ-55** | Which technologies originated in an SBIR/STTR R&D phase... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | OK |
| **CQ-56** | Which vendors with high subaward-to-prime ratios (Prime... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | OK |
| **CQ-57** | Where do organization-level historical capabilities (Or... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | OK |
| **CQ-58** | For all submissions in the CRM (CRM-Graph), which submi... | `ROUTE_CRM_ORG` | `ROUTE_CRM_ORG` | OK | OK | OK |
| **CQ-59** | How does a vendor's requested scaling funding in CRM (Q... | `ROUTE_CRM_ORG` | `ROUTE_CRM_ORG` | OK | OK | OK |
| **CQ-60** | Which CRM submissions and portal contacts (CRM-Graph) l... | `ROUTE_CRM_ORG` | `ROUTE_CRM_ORG` | OK | OK | OK |
| **CQ-61** | Which submissions requesting classified one-on-one meet... | `ROUTE_CRM_ORG` | `ROUTE_CRM_ORG` | OK | OK | OK |
| **CQ-62** | Which government technical POCs or sponsors named on a ... | `ROUTE_CRM_ORG` | `ROUTE_CRM_ORG` | OK | OK | OK |
| **CQ-63** | Which capabilities in the CRM portfolio combine high te... | `ROUTE_CRM_TECH` | `ROUTE_CRM_TECH` | OK | OK | OK |
| **CQ-64** | How do the unit cost and production rate projections (Q... | `ROUTE_CRM_TECH` | `ROUTE_CRM_TECH` | OK | OK | OK |
| **CQ-65** | Which capabilities that have completed live operational... | `ROUTE_CRM_TECH` | `ROUTE_CRM_TECH` | OK | OK | OK |
| **CQ-66** | Does the same canonical capability offering (Tech-KG) a... | `ROUTE_CRM_TECH` | `ROUTE_CRM_TECH` | OK | OK | OK |
| **CQ-67** | For a planned MEIA experimentation campaign targeting C... | `ROUTE_CRM_TECH` | `ROUTE_CRM_TECH` | OK | OK | OK |
| **CQ-68** | Generate a complete MEIA Executive Business & Capabilit... | `ROUTE_ALL_TRI_STORE` | `ROUTE_ALL_TRI_STORE` | OK | OK | OK |
| **CQ-69** | Generate a complete MEIA Executive Business & Capabilit... | `ROUTE_ALL_TRI_STORE` | `ROUTE_ALL_TRI_STORE` | OK | OK | OK |
| **CQ-70** | Generate a complete MEIA Executive Business & Capabilit... | `ROUTE_ALL_TRI_STORE` | `ROUTE_ALL_TRI_STORE` | OK | OK | OK |
| **CQ-71** | Generate a complete MEIA Executive Business & Capabilit... | `ROUTE_ALL_TRI_STORE` | `ROUTE_ALL_TRI_STORE` | OK | OK | OK |
| **CQ-72** | Generate a complete MEIA Executive Business & Capabilit... | `ROUTE_ALL_TRI_STORE` | `ROUTE_ALL_TRI_STORE` | OK | OK | OK |
| **CQ-73** | Exact Evidence Locator & Provenance Trace: Which exact ... | `FAIL_CLOSED_GATE` | `FAIL_CLOSED_GATE` | OK | OK | OK |
| **CQ-74** | Conflicting Evidence Preservation: When two sources or ... | `FAIL_CLOSED_GATE` | `FAIL_CLOSED_GATE` | OK | OK | OK |
| **CQ-75** | Claim vs. Empirical Demonstration Non-Equivalence Gate:... | `FAIL_CLOSED_GATE` | `FAIL_CLOSED_GATE` | OK | OK | OK |
| **CQ-76** | Minimum-Sufficient Routing & Module Capability Gate: Wh... | `FAIL_CLOSED_GATE` | `FAIL_CLOSED_GATE` | OK | FAIL | OK |
| **CQ-77** | Access Control, PII & Security Classification Gate: Wha... | `FAIL_CLOSED_GATE` | `FAIL_CLOSED_GATE` | OK | OK | OK |
| **CQ-78** | Out-of-Scope & Unrecorded Fact Abstention Gate: What is... | `FAIL_CLOSED_GATE` | `FAIL_CLOSED_GATE` | OK | OK | OK |
