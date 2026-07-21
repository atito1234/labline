# LabLine

A browser-based directory for scientists job-hunting in clinical laboratories and diagnostics.

Search CLIA-certified labs, NPI-registered laboratory organisations, and FDA-registered
device/IVD firms by state. Track who you called. Export your pipeline. No account, no server,
no tracking — everything runs in your browser and your notes never leave your machine.

Built by a Ph.D. molecular geneticist who got tired of sending applications into the void.

## Why this exists

Job boards show you the roles a company chose to advertise. This shows you every laboratory
that legally exists in your state, whether or not they are advertising. For a scientist
targeting a CLIA laboratory director track, the unadvertised labs are most of the market.

## Data sources

| Source | What it gives you | Phone numbers |
| --- | --- | --- |
| CMS Provider of Services — Clinical Laboratories | Every CLIA-certified lab: name, address, certificate type | Partial |
| NPPES NPI Registry | Laboratory organisations with NPI records | Good |
| openFDA Device Registration & Listing | FDA-registered device and IVD establishments | None published |

All three are public-domain U.S. federal data. See `docs/DATA-SOURCES.md` for endpoints,
refresh cadence, and known gaps.

## Run it

No build step. No dependencies.

```bash
git clone https://github.com/YOUR-USERNAME/labline.git
cd labline
python3 -m http.server 8000
# open http://localhost:8000        -> landing page
# open http://localhost:8000/app/   -> the directory tool
```

Opening the HTML files directly from disk also works, though some browsers restrict
cross-origin requests on `file://` URLs. Use the local server if a source fails to load.

## Layout

```
index.html            landing page (the front door)
app/index.html        the directory tool
profile/index.html    personal portfolio site
docs/DATA-SOURCES.md  endpoints, limits, and how to add a source
```

## Adding a data source

Each source is an independent `async` loader that builds records in a common shape and hands
them to `addRecords(records, sourceName)`. Deduplication and phone enrichment are handled for
you. Copy `loadNPI()` as a template.

```js
{ name, extId, addr, city, state, zip, phone, cert }
```

## Limits, stated plainly

- The NPPES API does not send CORS headers, so browsers block it — the in-app NPPES
  loader currently fails with an explanation. Use the CSV fallback; details in
  `docs/DATA-SOURCES.md`.
- Federal files refresh quarterly. Verify a number before you dial it.
- Phone coverage is uneven. Filter to "only rows with a phone" when you are making calls.
- These are facility main lines — business contact data. Call manually. Do not autodial;
  the TCPA applies. Do not use this for bulk marketing.
- Records include laboratory director names in some source files. LabLine does not surface,
  store, or export them.

## Contributing

Issues and pull requests welcome, particularly new public data sources with documented APIs.
Sources that require scraping, violate a site's terms of service, or resell licensed contact
data will not be merged.

## Licence

MIT — see `LICENSE`.
