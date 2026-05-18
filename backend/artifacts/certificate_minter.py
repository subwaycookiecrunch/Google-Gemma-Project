import os
import json
import hashlib
from datetime import datetime
from dataclasses import dataclass
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from rich.console import Console

console = Console()

@dataclass
class InfectionCertificate:
    session_id: str
    tx_hash: str
    block_number: int
    timestamp: str
    certificate_data: dict
    verification_url: str
    minted: bool
    network: str = "Polygon Mumbai Testnet"

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "tx_hash": self.tx_hash,
            "block_number": self.block_number,
            "timestamp": self.timestamp,
            "certificate_data": self.certificate_data,
            "verification_url": self.verification_url,
            "minted": self.minted,
            "network": self.network
        }

def mint_certificate(session_id: str, full_results: dict) -> InfectionCertificate:
    inf_data = full_results.get("infiltration", {})
    ev_data = full_results.get("evolution", {})
    rev_data = full_results.get("revelation", {})
    sym_data = full_results.get("symbiotic", None)
    
    repo_path = inf_data.get("repo_path", "unknown")
    repo_hash = hashlib.sha256(repo_path.encode()).hexdigest()
    
    fp_count = len(inf_data.get("feeding_points_raw", []))
    
    # Safely extract evolution data
    dominant_strain_name = "UNKNOWN"
    fitness_score = 0.0
    attack_vector = "UNKNOWN"
    if "dominant" in ev_data:
        dominant_strain = ev_data["dominant"]
        dominant_strain_name = getattr(dominant_strain, "strain_id", dominant_strain.get("strain_id", "UNKNOWN") if isinstance(dominant_strain, dict) else "UNKNOWN")
        fitness_score = getattr(dominant_strain, "fitness_score", dominant_strain.get("fitness_score", 0.0) if isinstance(dominant_strain, dict) else 0.0)
        target_fp = getattr(dominant_strain, "target_feeding_point", dominant_strain.get("target_feeding_point", {}) if isinstance(dominant_strain, dict) else {})
        attack_vector = getattr(target_fp, "name", target_fp.get("name", "UNKNOWN") if isinstance(target_fp, dict) else "UNKNOWN")

    # Safely extract revelation data
    time_impact = rev_data.get("time_to_impact")
    time_to_comp = getattr(time_impact, "minutes_to_complete_attack", time_impact.get("minutes_to_complete_attack", 0) if isinstance(time_impact, dict) else 0)
    natural_disc = getattr(time_impact, "days_to_natural_discovery", time_impact.get("days_to_natural_discovery", 0) if isinstance(time_impact, dict) else 0)
    
    verdict = rev_data.get("final_verdict", "")
    verdict_hash = hashlib.sha256(verdict.encode()).hexdigest()
    
    personality = "SYMBIOTIC" if sym_data else "PARASITIC"
    timestamp = datetime.now().isoformat()
    
    cert_data = {
        "case_id": session_id,
        "repository_hash": repo_hash,
        "feeding_points": fp_count,
        "dominant_strain": dominant_strain_name,
        "fitness_score": float(fitness_score),
        "attack_vector": attack_vector,
        "time_to_compromise_minutes": float(time_to_comp),
        "natural_discovery_days": int(natural_disc),
        "parasite_version": "EVOLVED",
        "personality": personality,
        "verdict_hash": verdict_hash,
        "generated_at": timestamp
    }
    
    rpc_url = os.environ.get("POLYGON_RPC_URL", "https://rpc-mumbai.maticvigil.com")
    private_key = os.environ.get("WALLET_PRIVATE_KEY", "")
    wallet_address = os.environ.get("WALLET_ADDRESS", "")
    
    tx_hash = f"0x{hashlib.sha256((session_id + timestamp).encode()).hexdigest()}"
    block_num = 45982134
    minted = False
    
    if private_key and wallet_address:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            
            if w3.is_connected():
                # Encode JSON as hex
                data_hex = w3.to_hex(text=json.dumps(cert_data))
                
                nonce = w3.eth.get_transaction_count(wallet_address)
                tx = {
                    'nonce': nonce,
                    'to': wallet_address, # Self send to store data
                    'value': 0,
                    'gas': 100000,
                    'gasPrice': w3.eth.gas_price,
                    'data': data_hex,
                    'chainId': 80001 # Mumbai
                }
                
                signed_tx = w3.eth.account.sign_transaction(tx, private_key)
                tx_id = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                receipt = w3.eth.wait_for_transaction_receipt(tx_id)
                
                tx_hash = tx_id.hex()
                block_num = receipt.blockNumber
                minted = True
                console.print(f"[bold green]✅ Certificate minted on Polygon: {tx_hash}[/bold green]")
            else:
                raise Exception("Failed to connect to Polygon RPC")
        except Exception as e:
            console.print(f"[bold yellow]⚠️ Blockchain unavailable — using offline certificate. Error: {e}[/bold yellow]")
    else:
        console.print("[bold yellow]⚠️ Missing WALLET_PRIVATE_KEY — using offline certificate for demo.[/bold yellow]")
        
    verify_url = f"https://mumbai.polygonscan.com/tx/{tx_hash}"
        
    return InfectionCertificate(
        session_id=session_id,
        tx_hash=tx_hash,
        block_number=block_num,
        timestamp=timestamp,
        certificate_data=cert_data,
        verification_url=verify_url,
        minted=minted
    )
