# PARASITE EVOLVED

## The idea

So here's what bugged me — every security tool I've used just throws a wall of CVEs at you and calls it a day. You get 200 warnings, most of them are noise, and you still have no idea how an actual attacker would chain things together to break in. That gap between "here's a list of issues" and "here's how someone would actually wreck your system" is massive, and nothing out there really bridges it.

That's where PARASITE EVOLVED came from. I wanted to build something that thinks like an attacker, not a scanner. The whole concept is biological — treat the codebase like a living host, drop a parasite in it, let it find what it wants to eat, watch it evolve, and then see exactly how it would kill the host. And then flip it — use that same understanding to heal the code.

Weird concept? Maybe. But it works really well.

## What it actually does

There are four phases and they run in sequence:

**Infiltration** — The system clones your repo (or reads a local path), parses every source file using Tree-sitter (supports Python, JavaScript, TypeScript, Java, and Go), and builds this massive 4-layer graph. The layers are file dependencies, function call chains, data flow from user input to dangerous sinks, and privilege operations like shell exec, database queries, auth handling, etc. For something like Jenkins which has 2000+ Java files, there's a smart prioritizer that scores files by security-relevant keyword density and picks the 200 most interesting ones. The whole thing finishes in about 4 seconds on Jenkins. Not minutes. Seconds.

**Evolution** — This is the fun part. A genetic algorithm breeds 5 attack "strains", each one representing a different exploitation strategy. They get scored on stealth, blast radius, and persistence. Gemma 4 handles the mutation step — it looks at the actual code context and generates novel attack variations that are specific to YOUR repo. Not generic templates. Real stuff based on what it found.

**Revelation** — The system generates three complete attack paths: data exfiltration, privilege escalation, and persistence. Every single step in these paths references actual functions from your codebase. If it says "inject through streamMagnet() in stream.go", that function actually exists and actually has that vulnerability. There's also a kill simulation timeline and a time-to-impact prediction using survival analysis. At the end, Gemma 4 writes a verdict — basically a dramatic summary of how screwed your codebase is (or isn't).

**Symbiotic Healing** — This is where it stops being scary and starts being useful. For every vulnerability found, the system generates a real code fix. Not "add input validation" — actual code. Command injection? Here's the subprocess.run call with proper argument lists. SQL injection? Here's the parameterized query. Plus it builds a prioritized roadmap of what to fix first.

## How Gemma 4 fits in

I went with Gemma 4 for a few reasons. The obvious one is that security tools deal with sensitive code — production code, proprietary stuff. With Gemma 4 being open-weight, you can run the whole pipeline on-premise. Nobody's code leaves the building. That matters a LOT for anyone in healthcare, finance, government, etc.

But honestly the bigger reason is that it's just good at code. The attack path generation needs the model to look at a function graph and figure out how an attacker would chain calls together. The healing engine needs it to understand vulnerability patterns and write working fixes. Gemma 4 handles both of those surprisingly well.

Specifically, Gemma 4 powers:
- Attack path generation (turns the function graph into realistic attack trajectories)
- Mutation engine (evolves attack strains using real code context)
- Verdict synthesis (writes the final security assessment)
- Code fix generation (produces deployable patches for each vulnerability)
- Hardening roadmaps (prioritizes what to fix and why)

When the API key isn't set, everything still works — the system falls back to data-driven heuristics built from the actual scan results. No hardcoded templates, no fake data. Just less "creative" output.

## The tech

Backend is Python with FastAPI. Tree-sitter does the AST parsing across all five languages. NetworkX builds and analyzes the graph. The genetic algorithm and fitness scoring are custom. Frontend is Next.js with Three.js for the 3D graph visualization (you can actually fly through your codebase's vulnerability graph, which is pretty cool). Framer Motion handles the animations.

The progress tracking system uses a background thread architecture — when you submit a large repo, the scan runs async and the frontend polls for updates every 500ms. You see a live progress bar with files scanned, functions found, privilege operations detected, and an ETA. Makes scanning massive repos way less painful.

For the file prioritization on large repos: it reads the first 8KB of every file, scores it against a list of security-relevant keywords (exec, system, password, auth, query, etc.), penalizes huge generated files, and picks the top 200. This means even on a repo with thousands of files, you get results in seconds instead of minutes, and the results are focused on the files that actually matter for security.

## Numbers

| What | Result |
|------|--------|
| Jenkins (2000+ Java files) | 200 files selected, 3055 functions, 1007 priv ops, ~4 sec |
| zentorrent (Go + JS) | 9 files, 29 functions, 5 priv ops, ~1.5 sec |
| Attack paths per scan | 3 (exfil, privesc, persistence) |
| Code fixes generated | 1 per vulnerability found |

## Why this matters

Pentesting is expensive. Like, $5K-$50K per engagement expensive. And most open-source projects never get one. Most startups can't afford one. Most student projects definitely can't afford one.

This tool is free. It runs locally. It gives you the attacker's perspective, not just a list of findings. And it tells you exactly how to fix things.

I think there's something powerful about making security accessible in a way that isn't just "here's another linting rule." Showing developers how an attacker would actually move through their code changes the way they think about security. It's not abstract anymore — it's concrete, it's visual, and it's specific to their codebase.

## Running it

```bash
git clone https://github.com/subwaycookiecrunch/Google-Gemma-Project.git
cd Google-Gemma-Project

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env

cd frontend && npm install && npm run dev &
cd .. && uvicorn backend.main:app --port 8000
```

Open localhost:3000, paste any GitHub URL, hit "Inject Parasite." That's it.

## What's next

There's a bunch of stuff I want to add — multi-repo scanning for microservice architectures, WebGL rendering upgrades for really large graphs, JWT auth for multi-user deployments, and containerization so the PDF generation doesn't depend on local system libraries. But for now, it does what it's supposed to do: show you how an attacker sees your code, and help you fix it before they get the chance.
