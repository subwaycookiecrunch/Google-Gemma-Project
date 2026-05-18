import os
import sys
import json
import requests
import time

BASE_URL = "http://localhost:8000"
FRONTEND_PUBLIC = os.path.join(os.path.dirname(__file__), "frontend", "public")

def main():
    print("🦠 Pre-warming PARASITE EVOLVED demo session...")
    repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "demo_repo"))
    
    # 1. Infiltrate
    print("1. Infiltrating...")
    res = requests.post(f"{BASE_URL}/api/infiltrate", json={"repo_path": repo_path}, timeout=120)
    res.raise_for_status()
    session_id = res.json()["session_id"]
    
    # 2. Evolve
    print(f"2. Evolving (Session: {session_id})...")
    res = requests.post(f"{BASE_URL}/api/evolve", json={"session_id": session_id}, timeout=120)
    res.raise_for_status()
    
    # Wait a bit for evolution to theoretically complete if it was async, though it's sync here
    time.sleep(1)
    
    # 3. Reveal
    print("3. Revealing...")
    res = requests.post(f"{BASE_URL}/api/reveal", json={"session_id": session_id}, timeout=120)
    res.raise_for_status()
    
    # 4. Symbiotic
    print("4. Generating Symbiotic Mode...")
    res = requests.post(f"{BASE_URL}/api/symbiotic", json={"session_id": session_id}, timeout=120)
    res.raise_for_status()
    
    # 5. Artifacts
    print("5. Generating Artifacts...")
    try:
        res = requests.post(f"{BASE_URL}/api/artifacts", json={"session_id": session_id}, timeout=120)
        res.raise_for_status()
    except Exception as e:
        print(f"⚠️ Artifact generation warning (likely weasyprint/blockchain fallback): {e}")
    
    # 6. Save session
    os.makedirs(FRONTEND_PUBLIC, exist_ok=True)
    demo_file = os.path.join(FRONTEND_PUBLIC, "demo-session.json")
    with open(demo_file, "w") as f:
        json.dump({"session_id": session_id}, f)
        
    print(f"✅ Demo session ready: {session_id}")

if __name__ == "__main__":
    main()
