```
                                       _.-----._
                                     .'  _..     \
                                    / .-'   \     \
                                  .'  |      \     \
         __..........______ __..-'    |       \     \
 ___..--'                   \          \       \     |
|                            | o   O    \       |    |
\                             \          `.._ _/    /
 \                             \ o      ________..-'
  \                             '------'|
   '^^._                            __.-'  LGB
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        w e b s a w - n g   ::   forging your dreams
```

# websaw-ng

> **Forging your dreams.** Tools for trailblazers.

websaw-ng is a batteries-included, **async** Python web platform built for one
purpose: **so you can blaze your own trail — confidently.**

It's a workshop of loosely-coupled, open-source, self-hostable packages. Pick any
saw, swap any part, run it anywhere: **no lock-in, no gatekeepers, no platform
tax — your stack, your rules.** You bring the vision; the saws clear the path and
forge it into something real enough to change your corner of the world.

![license](https://img.shields.io/badge/license-MIT-blue)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![conda](https://img.shields.io/badge/conda-websaw--ng-brightgreen)

## Why

Everything here serves **self-determination**. When you own your whole stack —
data, UI, identity, access, packaging, observability — no vendor can revoke your
runway. And batteries-included guardrails (RBAC, audit, metrics) let you ship
*without fear*. That's the whole point: to **enable individuals and companies to
blaze their own trail, confidently — to self-actualize, and change their world.**

Under the hood, websaw-ng is the **next generation** — a heavily-diverged
successor of [websaw](https://github.com/valq7711/websaw) (Valery Kucherov's take
on [py4web](https://github.com/web2py/py4web) /
[web2py](http://www.web2py.com)). It keeps the web2py *developer joy* — `DAL`,
`Field`, fixtures, per-app folders. The original websaw was **WSGI (sync)**;
websaw-ng adds an async core so it now runs **both sync and async** — plus a real
UI kit, fine-grained RBAC, an identity service with a built-in OIDC IdP, an app
store, and
DuckDB/OpenTelemetry observability. It has diverged far enough to be **its own
thing**.

## The bench

These are the saws you reach for — take the whole bench, or a single blade. Each
is its own installable package; all of it is yours to wield.

| Package | Role | Persona |
|---|---|---|
| **websaw-ng** | async web framework (this repo) | 🔥 the Forge |
| **ombott-ng** | async HTTP core — ASGI, WebSockets, SSE | 📯 the Courier |
| **sqladal** | data layer — the pydal API on SQLAlchemy (sync **and** async) | ⚒ the Anvil |
| **gridsaw** | UI — data-bound grids, forms & widgets across Bulma/Bootstrap/Tailwind | 🪚 the Ripsaw |
| **identsaw** | identity & auth — password/JWT/OAuth2/OIDC/TOTP/magic-link/passkey/SAML **+ a centralized OIDC IdP** | 🗝 the Keymaster |
| **guardsaw** | fine-grained RBAC/ABAC, multi-tenancy, field masking & a web2py-style admin | 🛡 the Warden |
| **appsaw** | web2py-style app packaging — download/upload/install with dependencies | ⚓ the Shipwright |
| **obsaw** | observability — a DuckDB metrics store + built-in viewer + OTLP export | 👁 the Watcher |
| **upytl** | Ultra-Pythonic Template Language — write HTML in pure Python | ✒ the Scribe |
| **yatl-ng** | Yet Another Template Language — the classic `{{ }}` templates (fork of py4web's yatl) | 🧵 the Loom |
| **pyjsaw** | a Python → JavaScript compiler (with a Vue-flavoured toolkit) | ⚗ the Alchemist |

## Install

Everything is published as conda packages on the public **websaw-ng** channel:

```bash
pixi init myapp && cd myapp
pixi project channel add https://prefix.dev/websaw-ng conda-forge
pixi add websaw-ng           # the framework — pull any others as you need them
```

or from source:

```bash
pip install -e .          # from a checkout of this repo
```

## Quick start

```python
# apps/hello/__init__.py
from websaw_ng import DefaultApp

app = DefaultApp(name=__package__)

@app.route("/")
def index(ctx):
    return "hello from websaw-ng"
```

```bash
python -m websaw_ng run apps -s uvicorn        # async server; visit http://127.0.0.1:8000/hello
```

## Highlights

- **Async-first**, WSGI-still-works: served by the `ombott-ng` core over uvicorn/
  hypercorn/granian, with WebSockets and Server-Sent Events.
- **Per-app folders** you can zip, download and install elsewhere (via `appsaw`) —
  dependencies and default RBAC policies included.
- **Fixtures** for DB, sessions (incl. a shared **GroupSession** for cross-app SSO),
  auth and templates.
- **Out of the box**: error tickets, an audit log, request metrics and a rich admin
  (via `guardsaw` + `obsaw`).

## Lineage & credits

```
web2py  →  py4web  →  websaw  →  websaw-ng
(Massimo    (BSD-3)   (Valery    (KellerKev,
 Di Pierro)           Kucherov)   this fork)
```

websaw-ng stands on the shoulders of **Massimo Di Pierro** (web2py / py4web) and
**Valery Kucherov** (the original `websaw`, and the `upytl` / `pyjsaw` / `ombott`
tools it builds on). Their copyright notices are retained throughout. 🙏

## License

**MIT** — see [LICENSE](LICENSE). Copyright © 2026 KellerKev; portions © 2022
Valery Kucherov, and derived from py4web (© Massimo Di Pierro 2017–2022). The
sibling packages carry their own licenses — the `*saw` packages authored here are
BSD-3-Clause; `upytl` / `pyjsaw` / `ombott-ng` are MIT.

---

*Part of the **websaw-ng** platform · forging your dreams.*
