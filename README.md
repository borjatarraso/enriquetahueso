# Enriqueta Hueso — enriquetahueso.com

Bilingual (EN/ES) artist-portfolio website for **Enriqueta Hueso**.

- **Live site:** https://www.enriquetahueso.com
- **Hosting:** Cloudflare Pages (deployed via `wrangler`)
- **DNS:** Arsys (registrar) → Cloudflare nameservers
- **Repo:** https://github.com/borjatarraso/enriquetahueso
- **Stack:** Python static-site builders (`build_site.py`, `build_gallery.py`) + handcrafted CSS themes (dark / light)

> This is the oldest project in the workshop (folder created
> 2026-04-18). It was decoupled from the sibling `galeriaomaso` site on
> 2026-05-17 — cross-links between the two now use absolute URLs.

---

## How a content change reaches visitors

```
edit  →  build  →  commit  →  push  →  Cloudflare build  →  serve from edge
```

Compared to a pure-static site, this repo has one extra stage: the
Python builders regenerate the `public/` tree from the source content
(`gallery-data.json`, templates, raw images) before the commit.

### Overview diagram

![Five-stage deploy flow — abstract](docs/deploy_pipeline_overview.jpg)

> Click for full resolution: [`docs/deploy_pipeline_overview.png`](docs/deploy_pipeline_overview.png)

### Detailed diagram (stages + APIs + cache layers + DNS)

![Detailed pipeline](docs/deploy_pipeline_detailed.jpg)

> Full-screen: [`docs/deploy_pipeline_detailed.png`](docs/deploy_pipeline_detailed.png)

### Internals (every API call, fallback, verify loop)

![Pipeline internals](docs/deploy_pipeline_internals.jpg)

> Full-screen: [`docs/deploy_pipeline_internals.png`](docs/deploy_pipeline_internals.png)

---

## Day-to-day workflow

```bash
# 1. edit content / gallery data / template
$EDITOR gallery-data.json

# 2. regenerate the public/ tree
python3 build_site.py
python3 build_gallery.py

# 3. preview locally
xdg-open public/index.html

# 4. commit + push the regenerated public/ alongside the source
git add -A
git commit -m "Add new exhibition entry"
git push origin main

# 5. wait ~30–60 s, then verify the live site has the new version
curl -sI https://www.enriquetahueso.com/css/styles.css | grep -i etag
```

If the live site does **not** pick up the change within ~2 minutes, see
the troubleshooting section — Cloudflare's GitHub auto-deploy can
silently disconnect, which is exactly why we built the verification
tooling described next.

---

## Why we ship our own verifier

Cloudflare's "push and forget" GitHub integration looks reliable but has
two failure modes that are silent from the publisher's point of view:

1. **The webhook can desync.** A repo permission change, a token rotation
   or even a transient GitHub outage can leave the integration in a
   "connected but not firing" state. The dashboard still says *Connected*.
2. **A build succeeds without reaching the edge.** The build log is
   green, but the asset that the public sees still hashes to the
   previous version — usually a cache-busting or route-conflict edge
   case.

Our companion tool (**Lynx Factory** — a local-only dashboard) closes
both gaps by:

- Hashing the local artifact (`css/styles.css`) with SHA-256.
- Fetching the same asset from the live URL.
- Comparing the two. If they differ, it re-issues the deploy with
  `wrangler` and polls every 5 s for up to 90 s.

The **Test** button in that dashboard turns **green only when the live
SHA matches local**. No more "I pushed, looks fine, but visitors see the
old page".

> **Heads-up:** never use an HTML page as the fingerprint asset.
> Cloudflare's bot-management layer injects a per-request `<script>` tag
> into HTML responses, so the hash always changes. Pick a CSS/JS/font/
> image asset instead — for this repo we use `css/styles.css`.

---

## Cloudflare configuration (sanitized)

The deploy verifier and the auto-redeploy watcher need three pieces of
metadata. Real values live only in shell env vars (`CF_API_TOKEN_*`) on
the maintainer's machine — **never** committed.

| Setting | Value |
|---------|-------|
| Account ID | `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` |
| Zone ID (enriquetahueso.com) | `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` |
| Pages project | `enriquetahueso` |
| Deploy method | `wrangler` (runs `npx wrangler deploy` from `public/`) |
| API token env var | `CF_API_TOKEN_ENRIQUETAHUESO` |
| Fingerprint asset | `css/styles.css` |
| Auto-redeploy branch | `main` |

### Token scope (least-privilege)

The deploy token only needs:

- **Account → Cloudflare Pages → Edit**
- **Zone → enriquetahueso.com → Cache Purge → Purge** *(optional, for
  manual cache busts)*

We deliberately do **not** use the broader "account-wide admin" token
here — least-privilege keeps the blast radius small if the token ever
leaks.

```sh
# ~/.bashrc.d/enriquetahueso_cf.sh   (chmod 600, never committed)
export CF_API_TOKEN_ENRIQUETAHUESO="cfat_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
export CF_ZONE_ID_ENRIQUETAHUESO="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

After editing:

```bash
source ~/.bashrc.d/enriquetahueso_cf.sh
# restart the local dashboard so the env var is picked up
```

---

## Troubleshooting

### "I pushed but the site looks unchanged"

```bash
# 1. did the push reach GitHub?
git log origin/main -1

# 2. did Cloudflare build it?
#    → check the Pages deployments tab in the dashboard

# 3. does the live asset differ from the local one?
sha256sum public/css/styles.css
curl -s https://www.enriquetahueso.com/css/styles.css | sha256sum

# 4. force a redeploy from the local checkout
cd public && npx wrangler deploy
```

### Cloudflare GitHub integration looks "connected" but doesn't fire

Disconnect and reconnect in **Workers & Pages → enriquetahueso →
Settings → Builds & deployments → Source**. Then push a trivial commit
to verify the webhook actually triggers a new build.

### DNS / TLS

- Nameservers must point at Cloudflare (managed at Arsys).
- TLS mode in Cloudflare: **Full (strict)**.
- Always Use HTTPS: **On**.

---

## Full deployment guide

A complete, plain-language walkthrough of the whole pipeline — including
zero-knowledge onboarding, an internals appendix, and a glossary — is
shipped alongside this README in both English and Spanish.

- 📕 English: [`docs/deploy_pipeline_guide_en.pdf`](docs/deploy_pipeline_guide_en.pdf)
- 📗 Español: [`docs/deploy_pipeline_guide_es.pdf`](docs/deploy_pipeline_guide_es.pdf)

Both PDFs embed the three diagrams above at full resolution.

---

## Layout

```
.
├── build_site.py           # main static-site builder
├── build_gallery.py        # gallery / exhibition page builder
├── generate_docs.py        # builds the EN/ES instruction PDFs in docs/
├── sanitize_site.py        # post-build sanitizer (strips dev artifacts)
├── gallery-data.json       # source of truth for exhibition data
├── index.html              # source landing page
├── css/                    # source stylesheets
├── js/                     # source scripts
├── img/                    # source images
├── public/                 # generated output — `wrangler deploy` runs here
├── site/                   # legacy staging tree (kept for reference)
└── docs/                   # human-facing documentation (this guide)
```

---

## Contributing

This repo is public on GitHub and external contributions are welcome. You do
**not** need Lynx Factory, the multiplexer, or any of the local tooling
described above — those are operator conveniences for the maintainer. A plain
git + Python + GitHub workflow is enough.

```bash
# 1. fork the repo on GitHub (Fork button, top-right of the repo page)
# 2. clone your fork
git clone https://github.com/<your-username>/enriquetahueso.git
cd enriquetahueso

# 3. create a topic branch
git checkout -b add/new-exhibition-entry

# 4. edit source content (gallery-data.json, templates, css, images...)
$EDITOR gallery-data.json

# 5. rebuild the public/ tree so reviewers can see the rendered output
python3 build_site.py
python3 build_gallery.py

# 6. preview locally
xdg-open public/index.html

# 7. commit + push to your fork (include both source AND regenerated public/)
git add -A
git commit -m "Add 2026 Helsinki exhibition entry"
git push -u origin add/new-exhibition-entry

# 8. open a Pull Request on GitHub
#    Your fork's page will show a "Compare & pull request" button.
#    Target the upstream `borjatarraso/enriquetahueso` repo, `main` branch.
```

> GitHub calls these **Pull Requests** (PRs); GitLab calls the same thing
> Merge Requests (MRs). Same concept either way.

**Borja Tarraso** (`<borja.tarraso@member.fsf.org>`) will review every PR and
either merge it (sometimes with small adjustments) or leave review comments
explaining why a change can't be accepted in its current form. Please:

- Keep PRs focused — one logical change per PR is easier to review than a
  large multi-purpose patch.
- Always commit the **regenerated `public/` tree** alongside your source
  edits — the deploy reads from `public/`, so a PR that only changes source
  would deploy nothing.
- Write a short PR description explaining *why* the change is useful, not
  just *what* the change is.
- For bigger ideas (new sections, design changes, structural moves), open a
  GitHub issue first to agree on the approach before investing time.

---

## License & author

Author: **Borja Tarraso** &nbsp;`<borja.tarraso@member.fsf.org>`

This repository is released under the **BSD-3-Clause** license.
