import os
from dataclasses import dataclass
from rich.console import Console

from backend.artifacts.certificate_minter import mint_certificate, InfectionCertificate
from backend.artifacts.qr_generator import generate_certificate_qr
from backend.artifacts.report_generator import generate_report, AutopsyReport

console = Console()

@dataclass
class ArtifactsResult:
    session_id: str
    report: AutopsyReport
    certificate: InfectionCertificate
    qr_code_base64: str
    report_download_url: str
    certificate_verify_url: str
    complete: bool = True

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "report": self.report.to_dict(),
            "certificate": self.certificate.to_dict(),
            "qr_code_base64": self.qr_code_base64,
            "report_download_url": self.report_download_url,
            "certificate_verify_url": self.certificate_verify_url,
            "complete": self.complete
        }

def generate_artifacts(session_id: str, full_results: dict) -> ArtifactsResult:
    console.print("\n[bold red]📄 GENERATING AUTOPSY REPORT...[/bold red]")
    
    # 1. Mint blockchain certificate
    console.print("[dim]⛓️  Minting infection certificate on Polygon...[/dim]")
    cert = mint_certificate(session_id, full_results)
    
    # 2. Generate QR code
    qr_b64 = generate_certificate_qr(session_id, cert.tx_hash, cert.verification_url, cert.timestamp)
    console.print("[dim]🔖 QR code generated[/dim]")
    
    # 3. Generate PDF Report
    report = generate_report(session_id, full_results, qr_b64, cert.to_dict())
    
    console.print("[bold red]☠️  AUTOPSY COMPLETE.[/bold red]")
    console.print(f"[red]📁 Report saved: {report.pdf_path}[/red]\n")
    
    return ArtifactsResult(
        session_id=session_id,
        report=report,
        certificate=cert,
        qr_code_base64=qr_b64,
        report_download_url=report.pdf_path,
        certificate_verify_url=cert.verification_url
    )
