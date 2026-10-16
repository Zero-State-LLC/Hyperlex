# Research 008: Lexical emergence

Status: DRAFT.

- Only C1–C3 are VERIFIED. They were checked by live lookup on 2026-10-15.
- Everything else is UNVERIFIED unless it is an internal repo finding (F1–F9 in spec).
- Author names for C1 and C2 are not verified, so they are cited by title and DOI.

## C1 (VERIFIED)

- **Citation:** "Social Networks of Lexical Innovation. Investigating the Social Dynamics of Diffusion of Neologisms on Twitter". Frontiers in Artificial Intelligence, 2021. doi:10.3389/frai.2021.648583.
- **URL:** https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2021.648583/full
- **Paper:**
  - 99 English neologisms on Twitter, 2006–2018.
  - Frequency alone misses the temporal profile.
  - Time series show high volatility (coefficient of variation).
  - Some terms stay confined to single, tightly connected network communities.
- **Brief claim:** "2021 longitudinal study of 99 neologisms (volatility, community movement)."
- **Fit:** Volatility and the count of 99 match. "Community movement" is looser than the paper. The paper describes communities in the Twitter network, and some terms never leave one.
- **Use in 008:**
  - CR-1 and CR-4: dormancy is not deletion, and volatility is data.
  - CR-7: diffusion needs network or community structure.

## C2 (VERIFIED)

- **Citation:** "How position in the network determines the fate of lexical innovations on Twitter". PLOS Complex Systems, 2024. doi:10.1371/journal.pcsy.0000005.
- **URL:** https://journals.plos.org/complexsystems/article?id=10.1371%2Fjournal.pcsy.0000005
- **Paper:**
  - About 650M French tweets, 2.5M users, and 392 innovations: 141 changes and 251 buzzes.
  - In the innovation phase, adopter profiles are similar. Prediction is weak (precision about 0.56, AUC about 0.61).
  - In the propagation phase, network profiles predict fate (precision about 0.81, AUC about 0.86).
- **Brief claim:** "2024 ~650M French tweets (early obs insufficient; network info more predictive during propagation)."
- **Fit:** Matches.
- **Use in 008:**
  - CR-1: bursts are a major fate class and must be kept.
  - CR-2: author and network structure is the signal.
  - CR-5: never-spread innovations are needed as negatives. This is our design inference, not a paper claim.
  - CR-9: discrimination metrics are standard.
  - Plan §5: expect a weak early signal.
- **Companion:** Tarrade, Magué, Chevrot 2022, doi:10.2478/plc-2022-15. Listed as a companion. Its content and URL are UNVERIFIED.

## C3 (VERIFIED, added)

- **Citation:** Zhu and Jurgens, "The structure of online social networks modulates the rate of lexical change". NAACL 2021.
- **URL:** https://aclanthology.org/2021.naacl-main.178
- **Paper:**
  - 80k neologisms across 4,420 subreddits.
  - Methods: Poisson regression and survival analysis.
  - A minimum-frequency threshold of 10 was applied for analysis.
- **Brief claim:** Not cited in the brief. It was added for conflict research.
- **Use in 008:**
  - CR-1 and CR-3: thresholds are analysis choices, not storage rules.
  - CR-2 and CR-7: network structure modulates change.
  - S2: survival modelling has precedent.

## Internal evidence (repo findings, not external sources)

| Finding | Summary |
|---|---|
| F1 | Single-use rejection effect lives in archived VERDICT-RULES v1.4 (d43a44a, PR #124), not on main |
| F2 | `SHADOW_INSTRUMENT_ONLY` and "V6 classifier" undefined on main |
| F3 | Store has no author or community columns |
| F4 | Ruling code R writes `rejected` |
| F5 | Export dedups on `content_sha256` |
| F6 | Oct-13 holds: goreslop 10 rows, the other 8 have 0 |
| F7 | Rights are provenance only, and the private overlay holds sensitive members |
| F8 | Constitution III, IV, V, VI, and VIII apply |
| F9 | 008 is the next free spec id |

## UNVERIFIED (not to be cited as fact)

- Author lists for C1 and C2.
- The content and URL of the C2 companion paper.
- Interfaces to Noesis and Trutina.
- Attested occurrences for 8 of the 9 Oct-13 holds: none found; Danny ruled they stay NOT_ATTESTED (2026-10-15).
- The best near-duplicate method or threshold for short social text. It is chosen at prereg freeze, with no literature claim.
- Expected effect size at Δ = 24 h. C2 suggests it is weak, but transfer to Hyperlex sources is unverified.
- Sockpuppet prevalence in Hyperlex sources.

## Resolved by repo research

- `SHADOW_INSTRUMENT_ONLY` and the rejected V6 final-label classifier: defined in argotide `docs/EVIDENCE.md` (2026-10-02 refresh). See spec CR-8.
