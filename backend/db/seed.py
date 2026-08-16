"""
Seed script — ingests all .docx files from ./sops/ into pgvector at startup.
Also generates synthetic SOPs if the sops/ folder is empty (dev mode).
Run: python -m db.seed
"""
import glob
import os
from db.models import init_db
from db.vectorstore import store
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 150))

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " "],
)

# ── Synthetic SOPs for dev/demo when no .docx files are present ──────────────

SYNTHETIC_SOPS = [
    {
        "filename": "SOP-Calibration-v3.docx",
        "content": """
SOP: Instrument Calibration Procedure v3
Purpose: Define calibration procedures for all analytical instruments.
Scope: pH meters, balances, spectrophotometers, temperature loggers.
Procedure:
1. Calibrate pH meters daily using pH 4.0, 7.0, and 10.0 buffer solutions.
2. Calibrate balances weekly using certified reference weights (Class F1).
3. Calibrate spectrophotometers monthly using NIST-traceable filters.
4. Record all calibration results in the instrument logbook within 2 hours.
5. If calibration fails, quarantine instrument and notify supervisor immediately.
Calibration intervals: pH meters daily, balances weekly, spectrophotometers monthly.
Tolerance: pH ±0.05 units, balance ±0.1mg, absorbance ±0.005 AU.
Responsibility: Instrument Custodian, QC Technician.
Revision: v3 | Approved by: QA Manager | Effective: 2024-01-10
        """,
    },
    {
        "filename": "SOP-Sample-Handling-v2.docx",
        "content": """
SOP: Sample Receipt and Handling v2
Purpose: Define procedures for receiving, logging, and storing samples.
Scope: All incoming samples to the analytical laboratory.
Procedure:
1. Upon receipt verify sample identity against chain of custody documentation.
2. Log sample within 30 minutes using barcode scanner and LIMS entry.
3. Assign unique accession number: YYYY-MM-DD-NNNNN format.
4. Record sample condition: intact, compromised, hemolyzed, lipemic.
5. Store at designated temperature: -80°C serum, 4°C whole blood, RT urine.
6. Document deviations in the non-conformance module within 1 hour.
Responsibility: Laboratory Technician II or above.
Revision: v2 | Approved by: Lab Director | Effective: 2024-02-01
        """,
    },
    {
        "filename": "SOP-QC-Management-v3.docx",
        "content": """
SOP: Quality Control Sample Management v3
Purpose: Define QC sample management and Westgard rule application.
Scope: Internal QC, external proficiency testing, method validation samples.
Procedure:
1. QC samples assigned own accession numbers flagged as QC type.
2. Westgard rules applied: 1-2s warning, 1-3s rejection, R-4s rejection.
3. Levey-Jennings charts generated for each analyte and QC level.
4. QC failure triggers automatic hold on all patient results.
5. Proficiency testing results entered manually within 24 hours of receipt.
6. Monthly QC review: supervisor documents Levey-Jennings trend analysis.
Corrective action: root cause analysis documented within 24 hours of failure.
Responsibility: QC Coordinator, Lab Supervisor.
Revision: v3.5 | Approved by: QA Manager | Effective: 2024-01-01
        """,
    },
    {
        "filename": "SOP-Result-Entry-v4.docx",
        "content": """
SOP: Result Entry and Verification v4
Purpose: Define entry, review, and approval of test results.
Scope: All quantitative and qualitative test results.
Procedure:
1. Primary entry by performing technician immediately after analysis.
2. Second verification required for all critical values and reportable results.
3. Auto-verification flags results outside reference ranges for manual review.
4. Flagged results must not be released without supervisor approval.
5. Amendment: original result preserved in audit trail; reason code required.
6. Turnaround time targets: STAT 1 hour, Routine 24 hours.
Critical value notification documented within 15 minutes of verbal notification.
Responsibility: Technician (entry), Senior Technician (verification).
Revision: v4 | Approved by: QA Director | Effective: 2024-03-01
        """,
    },
    {
        "filename": "SOP-Data-Integrity-v2.docx",
        "content": """
SOP: Data Integrity and Backup Procedures v2
Purpose: Ensure integrity and recoverability of all laboratory data.
Scope: All databases, configurations, and archived records.
Backup schedule:
- Incremental: every 6 hours
- Full backup: daily at 02:00
- Offsite replication: real-time to disaster recovery site
- Retention: 90 days online, 7 years archived
Integrity checks:
1. Automated checksum verification after every backup.
2. Monthly restore test to verify data integrity.
3. Annual full disaster recovery drill.
Data modification controls: no direct database access outside application layer.
All modifications logged with before/after values in audit trail.
Responsibility: IT Database Administrator, QA.
Revision: v2.1 | Approved by: CTO | Effective: 2024-01-01
        """,
    },
]


def seed_synthetic():
    """Used when no .docx files exist in sops/ — for dev/demo."""
    print("  No .docx files found in sops/ — loading synthetic SOPs for demo.")
    total = 0
    for sop in SYNTHETIC_SOPS:
        doc    = Document(
            page_content=sop["content"].strip(),
            metadata={
                "source":   sop["filename"],
                "doc_type": "sop",
            }
        )
        chunks = splitter.split_documents([doc])
        for i, c in enumerate(chunks):
            c.metadata["chunk_idx"] = i
        store(chunks)
        total += len(chunks)
        print(f"  ✓ {sop['filename']} — {len(chunks)} chunks")
    return total


def seed_from_disk():
    """Loads actual .docx files from sops/."""
    paths  = glob.glob("./sops/*.docx")
    total  = 0
    for path in paths:
        filename = os.path.basename(path)
        try:
            loader = Docx2txtLoader(path)
            docs   = loader.load()
            chunks = splitter.split_documents(docs)
            for i, c in enumerate(chunks):
                c.metadata.update({
                    "source":    filename,
                    "doc_type":  "sop",
                    "chunk_idx": i,
                })
            store(chunks)
            total += len(chunks)
            print(f"  ✓ {filename} — {len(chunks)} chunks")
        except Exception as e:
            print(f"  ✗ {filename} — SKIPPED: {e}")
    return total


def seed():
    print("Initialising database…")
    init_db()
    print("Ingesting SOPs into pgvector…")
    paths = glob.glob("./sops/*.docx")
    if paths:
        total = seed_from_disk()
    else:
        total = seed_synthetic()
    print(f"Seed complete — {total} chunks stored.\n")


if __name__ == "__main__":
    seed()
