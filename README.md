# 🦠 PARASITE EVOLVED

> **"What if a parasite lived inside your codebase? What would it eat first?"**

AI-powered codebase security analysis that simulates a living organism infiltrating, evolving, and revealing vulnerabilities — then heals the host from within.

**Built with [Gemma 4](https://ai.google.dev/gemma) | [Gemma 4 Good Hackathon](https://www.kaggle.com/competitions/gemma-4-good-hackathon) — Safety & Trust Track**

---

## ⚡ What It Does

| Phase | Description |
|-------|------------|
| 🔬 **Infiltrate** | Multi-language AST parsing (Python, JS, TS, Java, Go) → 4-layer security graph |
| 🧬 **Evolve** | Genetic algorithm evolves 5 attack strains optimized for your codebase |
| 💀 **Reveal** | Dynamic attack paths, kill simulation, time-to-impact prediction |
| 💊 **Heal** | Real code fixes, hardening roadmap, autopsy report |

## 🧠 Powered by Gemma 4

- **Attack path generation** — analyzes real function graphs for repo-specific attack trajectories
- **Mutation engine** — evolves novel attack variations using actual code context  
- **Verdict synthesis** — dramatic, context-aware security assessments
- **Symbiotic healing** — real, deployable code fixes (not generic advice)
- **Local-first** — Gemma 4's open weights mean no code leaves your network

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/subwaycookiecrunch/parasite-evolved.git
cd parasite-evolved

# Backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env
uvicorn backend.main:app --port 8000

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

Open **http://localhost:3000** → paste any GitHub URL → click **"Inject Parasite"**

## 📊 Performance

| Target | Files | Functions | Priv Ops | Time |
|--------|-------|-----------|----------|------|
| Jenkins (2000+ Java) | 200 (smart-capped) | 3,055 | 1,007 | ~4s |
| zentorrent (Go + JS) | 9 | 29 | 5 | ~1.5s |

## 🏗️ Architecture

```
Frontend (Next.js + Three.js)  ←→  Backend (FastAPI + Tree-sitter + NetworkX)
                                        ↓
                                   Gemma 4 (27B-IT)
                                        ↓
                              Infiltrate → Evolve → Reveal → Heal
```

## 📜 License

Apache 2.0
