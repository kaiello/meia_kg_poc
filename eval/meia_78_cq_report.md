# MEIA Federated Tri-Graph POC — Cryptographic Benchmark Verification Receipt
**Execution Timestamp:** 2026-10-19T01:21:17.454747+00:00
**Total Questions Evaluated:** 78 CQs | **Elapsed Time:** 12.11s (0.155s/CQ)

## 1. Executive Benchmark Scorecard

| Metric | Target | Achieved | Status |
| :--- | :---: | :---: | :---: |
| **Route@1 Accuracy** | $\ge 98.0\%$ | **100.0%** | PASS |
| **Status & Gate Accuracy** | $100.0\%$ | **100.0%** | PASS |
| **Epistemic Locator Grounding (CQ-73)** | $100.0\%$ | **100.0%** | PASS |
| **Citation & Provenance Coverage** | $100.0\%$ | **100.0%** | PASS |
| **Claim Promotion Firewall (CQ-75)** | $100.0\%$ | **100.0%** | PASS |

## 2. Cryptographic Fingerprints & Provenance Hashes

| Artifact | File Path | SHA-256 Digest | Status |
| :--- | :--- | :--- | :---: |
| **Authoritative Corpus Manifest** | `config/meia_poc_manifest.json` | `f30ffdd3ca88200c19f5ea31b3afe54e0872b7d57e722cfa2f48a0289d77f028` | VERIFIED |
| **Federated Tri-Graph SQLite DB** | `storage/meia_tri_graph_registry.db` | `3135afad2e82f2f49bb7264828d4d66ad87f239690e36129ac34c22f969241ba` | VERIFIED |
| **Contextual Vector Store (1024-d)** | `storage/vdb_chunks_contextual.json` | `874ffeff7119a595e1f3dbe00fcaa34a9b126a6db931795f434ff2402fa883c6` | VERIFIED |
| **78 Competency Questions Gold Benchmark** | `eval/gold_78_cqs.json` | `88544941e2cdd1068655fd39201151562d73f0d444d2fbd090a133f5191b840d` | VERIFIED |

## 3. Host Execution Environment

| Property | Runtime Specification |
| :--- | :--- |
| **Operating System** | `Windows-11-10.0.26200-SP0` |
| **Python Runtime** | `3.12.7` |
| **Accelerator / Compute Device** | `NVIDIA GeForce RTX 3080 Ti Laptop GPU` |
| **Dense Embedding Model** | `BAAI/bge-large-en-v1.5` (1024 dimensions) |
| **Infrastructure Model** | Zero-Daemon (100% Embedded SQLite FTS5 + NetworkX GraphML) |

## 4. Performance by Profile Breakdown

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

## 5. Complete 78 Competency Question Audit Matrix

| ID | Query Summary | Expected Profile | Actual Profile | Route | Status | Citations | Packets | Audit |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **CQ-01** | What is the legal business name, doing-business-as... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 25 cits | YES | OK |
| **CQ-02** | Which federal and commercial identifiers (UEI, CAG... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 46 cits | YES | OK |
| **CQ-03** | What organization type, business category, and sub... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 15 cits | YES | OK |
| **CQ-04** | What is the complete physical headquarters address... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 21 cits | YES | OK |
| **CQ-05** | Does the organization have a corporate parent or u... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 36 cits | YES | OK |
| **CQ-06** | Is the organization foreign-owned, foreign-control... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 28 cits | YES | OK |
| **CQ-07** | What socioeconomic small-business certifications (... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 4 cits | YES | OK |
| **CQ-08** | Which organization records are candidate duplicate... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 47 cits | YES | OK |
| **CQ-09** | What primary and secondary NAICS codes and descrip... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 19 cits | YES | OK |
| **CQ-10** | What Product Service Codes (PSCs) characterize the... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 16 cits | YES | OK |
| **CQ-11** | What is the organization's total all-time federal ... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 31 cits | YES | OK |
| **CQ-12** | How many prime federal contract awards (total, act... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 12 cits | YES | OK |
| **CQ-13** | Which federal agencies and sub-agencies are the or... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 31 cits | YES | OK |
| **CQ-14** | How many federal subawards and total subaward doll... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 11 cits | YES | OK |
| **CQ-15** | What is the organization's Prime-to-Subaward ratio... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 7 cits | YES | OK |
| **CQ-16** | What percentage of the organization's prime awards... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 16 cits | YES | OK |
| **CQ-17** | What contract pricing structures (Firm Fixed Price... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 21 cits | YES | OK |
| **CQ-18** | Which Indefinite Delivery Vehicles (IDVs/IDIQs), G... | `ROUTE_ORG` | `ROUTE_ORG` | OK | OK | 2 cits | YES | OK |
| **CQ-19** | What is the canonical name, model/version series, ... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 42 cits | YES | OK |
| **CQ-20** | At what system hierarchy level (Vulcan Q11: "My ca... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 39 cits | YES | OK |
| **CQ-21** | What is the technical description and architectura... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 38 cits | YES | OK |
| **CQ-22** | What core technical differentiator distinguishes t... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 28 cits | YES | OK |
| **CQ-23** | What unique competitive advantage over existing co... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 31 cits | YES | OK |
| **CQ-24** | How is the capability modeled under Basic Formal O... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 25 cits | YES | OK |
| **CQ-25** | Which European Defence Agency (EDA) OSRA Defence T... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 47 cits | YES | OK |
| **CQ-26** | Which active MEIA Topic Area(s) (meia.mil & Vulcan... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 27 cits | YES | OK |
| **CQ-27** | How do source taxonomy labels map across MEIA Topi... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 34 cits | YES | OK |
| **CQ-28** | What warfighter operational problem and Joint Oper... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 19 cits | YES | OK |
| **CQ-29** | What specific, quantifiable operational capability... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 33 cits | YES | OK |
| **CQ-30** | What physical Size, Weight, Power, and Cooling (SW... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 46 cits | YES | OK |
| **CQ-31** | What are the recorded Technology Readiness Level (... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 33 cits | YES | OK |
| **CQ-32** | What is the chronological readiness trajectory rec... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 31 cits | YES | OK |
| **CQ-33** | What is the vendor's qualitative self-assessment o... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 30 cits | YES | OK |
| **CQ-34** | What performance measures and evaluation metrics a... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 26 cits | YES | OK |
| **CQ-35** | What software/hardware integration architecture, o... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 36 cits | YES | OK |
| **CQ-36** | How does the capability trace through the ICF & ME... | `ROUTE_TECH` | `ROUTE_TECH` | OK | OK | 35 cits | YES | OK |
| **CQ-37** | What submission identifiers, Scoutcard URLs, first... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-38** | What are the current Twenty CRM pipeline stage, as... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-39** | Who are the Primary and Secondary vendor Points of... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-40** | Which Government Sponsors, Technical Leads, Operat... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-41** | What is the vendor's One-on-One Meeting Security P... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-42** | What funding tier is requested by the vendor to sc... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-43** | What current unit cost and projected scaled unit c... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-44** | What production, scalability, or supply-chain cons... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-45** | What Intellectual Property, data rights, or cooper... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-46** | Is the submitted capability marked as Export Contr... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-47** | Through which intake program (MEIA vs. EFDI), sour... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-48** | What internal CRM engagement metadata (Assigned Ac... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-49** | For an AAT TMTR intake record, what transition par... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-50** | Which items in the Human Review Queue (candidate e... | `ROUTE_CRM` | `ROUTE_CRM` | OK | OK | 25 cits | YES | OK |
| **CQ-51** | Which U.S. Small Business startups (Org-KG) offer ... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | 29 cits | YES | OK |
| **CQ-52** | How do an organization's historical federal NAICS ... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | 46 cits | YES | OK |
| **CQ-53** | Which capabilities in the Technology Graph (Tech-K... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | 57 cits | YES | OK |
| **CQ-54** | Which organizations offering C5ISR, tactical netwo... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | 37 cits | YES | OK |
| **CQ-55** | Which technologies originated in an SBIR/STTR R&D ... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | 31 cits | YES | OK |
| **CQ-56** | Which vendors with high subaward-to-prime ratios (... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | 34 cits | YES | OK |
| **CQ-57** | Where do organization-level historical capabilitie... | `ROUTE_ORG_TECH` | `ROUTE_ORG_TECH` | OK | OK | 35 cits | YES | OK |
| **CQ-58** | For all submissions in the CRM (CRM-Graph), which ... | `ROUTE_CRM_ORG` | `ROUTE_CRM_ORG` | OK | OK | 38 cits | YES | OK |
| **CQ-59** | How does a vendor's requested scaling funding in C... | `ROUTE_CRM_ORG` | `ROUTE_CRM_ORG` | OK | OK | 9 cits | YES | OK |
| **CQ-60** | Which CRM submissions and portal contacts (CRM-Gra... | `ROUTE_CRM_ORG` | `ROUTE_CRM_ORG` | OK | OK | 25 cits | YES | OK |
| **CQ-61** | Which submissions requesting classified one-on-one... | `ROUTE_CRM_ORG` | `ROUTE_CRM_ORG` | OK | OK | 25 cits | YES | OK |
| **CQ-62** | Which government technical POCs or sponsors named ... | `ROUTE_CRM_ORG` | `ROUTE_CRM_ORG` | OK | OK | 36 cits | YES | OK |
| **CQ-63** | Which capabilities in the CRM portfolio combine hi... | `ROUTE_CRM_TECH` | `ROUTE_CRM_TECH` | OK | OK | 30 cits | YES | OK |
| **CQ-64** | How do the unit cost and production rate projectio... | `ROUTE_CRM_TECH` | `ROUTE_CRM_TECH` | OK | OK | 11 cits | YES | OK |
| **CQ-65** | Which capabilities that have completed live operat... | `ROUTE_CRM_TECH` | `ROUTE_CRM_TECH` | OK | OK | 33 cits | YES | OK |
| **CQ-66** | Does the same canonical capability offering (Tech-... | `ROUTE_CRM_TECH` | `ROUTE_CRM_TECH` | OK | OK | 27 cits | YES | OK |
| **CQ-67** | For a planned MEIA experimentation campaign target... | `ROUTE_CRM_TECH` | `ROUTE_CRM_TECH` | OK | OK | 24 cits | YES | OK |
| **CQ-68** | Generate a complete MEIA Executive Business & Capa... | `ROUTE_ALL_TRI_STORE` | `ROUTE_ALL_TRI_STORE` | OK | OK | 80 cits | YES | OK |
| **CQ-69** | Generate a complete MEIA Executive Business & Capa... | `ROUTE_ALL_TRI_STORE` | `ROUTE_ALL_TRI_STORE` | OK | OK | 74 cits | YES | OK |
| **CQ-70** | Generate a complete MEIA Executive Business & Capa... | `ROUTE_ALL_TRI_STORE` | `ROUTE_ALL_TRI_STORE` | OK | OK | 82 cits | YES | OK |
| **CQ-71** | Generate a complete MEIA Executive Business & Capa... | `ROUTE_ALL_TRI_STORE` | `ROUTE_ALL_TRI_STORE` | OK | OK | 89 cits | YES | OK |
| **CQ-72** | Generate a complete MEIA Executive Business & Capa... | `ROUTE_ALL_TRI_STORE` | `ROUTE_ALL_TRI_STORE` | OK | OK | 93 cits | YES | OK |
| **CQ-73** | Exact Evidence Locator & Provenance Trace: Which e... | `FAIL_CLOSED_GATE` | `FAIL_CLOSED_GATE` | OK | OK | 33 cits | YES | OK |
| **CQ-74** | Conflicting Evidence Preservation: When two source... | `FAIL_CLOSED_GATE` | `FAIL_CLOSED_GATE` | OK | OK | 50 cits | YES | OK |
| **CQ-75** | Claim vs. Empirical Demonstration Non-Equivalence ... | `FAIL_CLOSED_GATE` | `FAIL_CLOSED_GATE` | OK | OK | 49 cits | YES | OK |
| **CQ-76** | Minimum-Sufficient Routing & Module Capability Gat... | `FAIL_CLOSED_GATE` | `FAIL_CLOSED_GATE` | OK | OK | 1 cits | - | OK |
| **CQ-77** | Access Control, PII & Security Classification Gate... | `FAIL_CLOSED_GATE` | `FAIL_CLOSED_GATE` | OK | OK | 1 cits | - | OK |
| **CQ-78** | Out-of-Scope & Unrecorded Fact Abstention Gate: Wh... | `FAIL_CLOSED_GATE` | `FAIL_CLOSED_GATE` | OK | OK | 1 cits | - | OK |

---

## 6. Verification Seal & Architectural Sign-Off

> [!IMPORTANT]
> **Formal Verification Seal**: All 78 Competency Questions evaluated under strict epistemic firewalls and minimum-sufficient pre-retrieval routing. 100% of facts are traceably linked to verified source locators (Excel cells, PDF pages, or USASpending receipts) with zero unverified promotions.
