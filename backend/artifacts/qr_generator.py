import qrcode
import base64
from io import BytesIO

def generate_certificate_qr(session_id: str, tx_hash: str, verification_url: str, timestamp: str) -> str:
    # QR encodes the local verification page URL for demo mode
    # In production, this would be a blockchain explorer URL
    local_verify_url = f"http://localhost:3000/verify/{session_id}"
    
    data = {
        "case_id": session_id,
        "tx_hash": tx_hash,
        "verified_at": timestamp,
        "parasite_version": "EVOLVED",
        "verify_url": local_verify_url,
        "blockchain_url": verification_url
    }
    
    import json
    json_data = json.dumps(data)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json_data)
    qr.make(fit=True)
    
    # Dark background #020204, green modules #00ff88
    img = qr.make_image(fill_color="#00ff88", back_color="#020204")
    
    # Resize to approximately 200x200 if needed, but box_size=10 is usually good
    # For now just save to BytesIO
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"
