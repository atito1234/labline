# Data sources

Every source LabLine uses is public-domain U.S. federal data with a documented API.
Nothing here is scraped, purchased, or licensed.

---

## 1. CMS Provider of Services — Clinical Laboratories

The authoritative registry of CLIA-certified laboratories.

**API endpoints** (newest first — LabLine probes each until one responds):

```
https://data.cms.gov/data-api/v1/dataset/d3eb38ac-d8e9-40d3-b7b7-6205d3d1dc16/data   2026-01-01
https://data.cms.gov/data-api/v1/dataset/899fd424-a4aa-400f-85ce-5a7e98334b03/data   2026-01-01
https://data.cms.gov/data-api/v1/dataset/12fe8c01-ed51-4af9-8902-0e1ec54d9cec/data   2025-10-01
https://data.cms.gov/data-api/v1/dataset/a1831002-8e90-4ff5-a811-0ea4bed3c4ce/data   2025-07-01
```

Parameters: `size`, `offset`, and `filter[COLUMN]=value`.

**Direct CSV** (for the offline fallback):
`https://data.cms.gov/sites/default/files/2026-04/63b67f01-10fe-4233-8f64-e537ba6ee294/clia.DATA.Q1_2026.csv`

Refresh cadence: quarterly (`R/P3M` in the dataset metadata).

Useful columns: `FAC_NAME`, `PRVDR_NUM`, `ST_ADR`, `CITY_NAME`, `STATE_CD`, `ZIP_CD`,
`CRTFCT_TYPE_CD`. Column names have changed between quarterly releases, so LabLine
matches them case-insensitively against a list of aliases rather than by exact name.

**Verified live 2026-07-21:** the endpoint responds 200 and reflects the request `Origin`
in `Access-Control-Allow-Origin`, so it works from the browser. Field names are uppercase
(`FAC_NAME`, `PHNE_NUM`, …). `CRTFCT_TYPE_CD` arrives as a code — 1 Compliance, 2 Waiver,
3 Accreditation, 4 PPM Microscopy, 9 Registration — which LabLine maps to labels. The file
also contains historical records: in a 2,000-row TX sample, 73% carried a non-zero
`PGM_TRMNTN_CD` (terminated), so LabLine requests `filter[PGM_TRMNTN_CD]=00` (active only).

**Certificate types that matter for a director track:** Certificate of Compliance and
Certificate of Accreditation indicate labs running non-waived testing. Under 42 CFR
§493.1443, high-complexity director eligibility requires an earned doctoral degree in a
chemical, biological, clinical or medical laboratory science plus certification by an
HHS-approved board. These are the labs where that experience is accrued.

**Known gap:** phone coverage is incomplete. Some quarterly releases omit the phone
column entirely. This is the main reason NPPES was added.

New quarterly endpoints appear here:
<https://catalog.data.gov/dataset/provider-of-services-file-clinical-laboratories>

---

## 2. NPPES NPI Registry

Every healthcare organisation with a National Provider Identifier. Best phone coverage
of the three sources.

```
https://npiregistry.cms.hhs.gov/api/?version=2.1&enumeration_type=NPI-2
  &state=TX&taxonomy_description=Clinical%20Medical%20Laboratory&limit=200&skip=0
```

- `enumeration_type=NPI-2` restricts results to organisations, not individual providers.
- `limit` maxes out at 200; page with `skip` (capped around 1000).
- No API key. Updated weekly.

LabLine queries four taxonomy descriptions: Clinical Medical Laboratory, Laboratory,
Physiological Laboratory, Clinical Pathology.

**Note:** individual-provider records (`NPI-1`) contain personal data. LabLine deliberately
queries organisations only.

**CORS limitation (verified 2026-07-21):** the NPPES API returns HTTP 200 with the expected
JSON from curl/PowerShell/server-side code, but it sends no `Access-Control-Allow-Origin`
header — even when the request carries an `Origin`. Browsers therefore block every response,
so the in-app NPPES loader cannot work from a web page today. The loader is kept in place
and reports this specific failure in the log panel rather than being removed, in case NPPES
adds CORS later. Workarounds: the in-app CSV fallback, or NPPES's monthly full-file download
at <https://download.cms.gov/nppes/NPI_Files.html>.

---

## 3. openFDA Device Registration & Listing

FDA-registered device establishments — the closest public equivalent to a biotech and
IVD-manufacturer directory.

```
https://api.fda.gov/device/registrationlisting.json?search=registration.state_code:"TX"&limit=100&skip=0
```

- No API key needed at low volume; rate limits apply above that.
- Returns HTTP 404 rather than an empty array when results are exhausted.
- Does **not** publish phone numbers — names and addresses only.
- Verified live 2026-07-21: responds 200 with `Access-Control-Allow-Origin: *`, so it
  works from the browser. For US establishments the zip is in `registration.zip_code`;
  `registration.postal_code` is an empty string.

---

## Worth adding next

These have documented public APIs and would meaningfully extend coverage. Contributions welcome.

**NIH RePORTER** — `https://api.reporter.nih.gov/v2/projects/search` (POST). Funded projects
with organisation names and principal investigators. The single best source for targeting
academic postdoc positions: it tells you which labs currently hold active funding, which is
the real precondition for a lab being able to hire you.

**ClinicalTrials.gov v2** — `https://clinicaltrials.gov/api/v2/studies`. Trial sponsors and
site facilities. Good for finding CROs and sponsor companies actively running studies in
your state.

**SEC EDGAR full-text search** — `https://efts.sec.gov/LATEST/search-index?q=...`. Public
biotech companies by SIC code (2836 biological products, 8731 commercial physical and
biological research). Gives corporate addresses and filings, not phone numbers.

**State health department laboratory lists** — several states publish their own licensed-lab
registries with better contact data than the federal file. New York (Wadsworth Center),
California, Florida, and Washington all publish lists. These are per-state and formats vary.

---

## Sources deliberately excluded

**LinkedIn, ZoomInfo, Apollo, and similar.** Scraping LinkedIn violates its terms of service
and has produced actual litigation. Purchased contact databases are compiled without the
consent of the people in them, and reselling or acting on that data raises obligations under
state privacy laws.

There is also a practical argument. Clinical diagnostics is a small field, and laboratory
directors talk to each other. A candidate who reaches out through a channel that is obviously
sourced from a scraped list reads as a vendor, not a colleague. If you are positioning
yourself as a regulatory and compliance professional, the way you source your own data is
part of your credibility.

Public federal registries are better on every axis that matters here: legal, free, more
complete for laboratories specifically, and defensible when someone asks where you got
their number.

---

## Call Prep — optional local AI

LabLine's directory needs no AI. The optional **Call Prep** layer connects to a language
model **you** run on your own machine (Ollama or LM Studio) to draft tailored cold-call
scripts from your resume plus company info you paste. Nothing is sent to any third party —
resume, company notes, and generated scripts stay in your browser and talk only to your
local model.

**It runs locally, not on the hosted site.** Browsers block a public `https://` page from
reaching a local model (mixed-content / private-network rules), so Call Prep works when you
launch LabLine on your own computer (`python -m http.server` then open the local URL). The
public github.io site remains the free directory.

**One-time setup (Ollama):** start Ollama allowing the LabLine origin, e.g.
`OLLAMA_ORIGINS=* ollama serve`, then in LabLine → **AI settings** set the endpoint
(`http://localhost:11434`) and a model name (`ollama list`). LM Studio: enable its local
server, use `http://localhost:1234/v1`.

**Web research (optional) — via the local proxy.** Browsers cannot call
`ollama.com/api/web_search` directly: it sends no CORS headers, so an in-browser request fails
with "Failed to fetch." LabLine therefore talks to a tiny proxy you run locally
(`tools/ollama-search-proxy.py`, stdlib only). The proxy holds your Ollama API key in an
environment variable — **the key never touches the browser** — forwards each search to Ollama,
and returns it with CORS headers the page accepts. Setup:

```
# 1) get a key at ollama.com -> Settings -> Keys
# 2) run the proxy (Windows PowerShell):
$env:OLLAMA_API_KEY = "your-key"
python tools/ollama-search-proxy.py
# 3) LabLine -> AI settings: Enable web search, Search URL = http://127.0.0.1:8791/search
#    (use 127.0.0.1, not localhost), Search key = blank
```

"Research & Prep" then runs research over your currently-filtered leads in a capped batch,
sequentially, with a live progress panel and a Stop button. Search queries reach Ollama's
service through the proxy, so that part isn't fully offline; for a fully local alternative,
point the Search URL at a self-hosted SearXNG instead. With web search off, prep still works
but is role/strategy-only — the model is instructed not to assert unverified specifics.

**Guardrails on research.** The prompt forces the model to ground every specific claim in the
provided sources, cite them, and mark anything unverified as "not found." On people it is
restricted to publicly published professional roles (who to ask for) — never personal or
private details, never invented individuals or dossiers. This is deliberate: it keeps outreach
credible and consistent with the no-scraped-contacts stance below.

**Direct page fetching is still out of scope client-side.** Arbitrary third-party sites block
cross-origin reads, so beyond the search API you can also paste page text manually. Full
server-side fetching would need a backend (a natural paid-tier feature).

**Two scores, kept separate.** *Call Priority* rates how good a target a lab is (reachability,
test complexity, cross-source confirmation). *Call Readiness* rates how prepared you are
(resume on file, call sheet generated, decision-maker identified, already engaged). Both are
heuristics to help you prioritize — not official ratings.

---

## Handling contact data responsibly

- Facility main lines only. LabLine never surfaces, stores, or exports the laboratory
  director names present in some source files.
- Manual dialling only. Automated calling to these numbers implicates the TCPA.
- Verify before dialling — federal files are quarterly snapshots and go stale.
- Pipeline notes stay in the user's own browser. There is no server and no analytics.
