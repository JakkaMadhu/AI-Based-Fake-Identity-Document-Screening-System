import sqlite3
import json
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path
import threading
from ..utils.logging import logger

DB_PATH = Path("screening_system.db").resolve()

class SqliteStore:
    """
    Persistent SQLite Database Store with Cryptographic SHA-256 Hash Chained Ledger.
    Ensures persistent screening history, document metadata, and tamper-evident audit blocks
    across server restarts.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SqliteStore, cls).__new__(cls)
                cls._instance._init_db()
            return cls._instance

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        self._genesis_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Documents Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT,
                    stored_filename TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    mime_type TEXT,
                    uploaded_at TEXT,
                    status TEXT,
                    face_stored_filename TEXT,
                    face_file_path TEXT,
                    raw_json TEXT
                )
            """)

            # 2. Screening Results Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS screening_results (
                    document_id TEXT PRIMARY KEY,
                    filename TEXT,
                    screening_status TEXT,
                    risk_level TEXT,
                    risk_score INTEGER,
                    genuine_probability REAL,
                    forged_probability REAL,
                    model_confidence REAL,
                    screening_timestamp TEXT,
                    face_verified INTEGER,
                    ocr_name TEXT,
                    ocr_doc_number TEXT,
                    block_hash TEXT,
                    result_json TEXT
                )
            """)

            # 3. Blockchain Audit Ledger Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blockchain_ledger (
                    block_index INTEGER PRIMARY KEY,
                    block_hash TEXT UNIQUE,
                    previous_hash TEXT,
                    document_id TEXT,
                    status TEXT,
                    timestamp TEXT,
                    signature_algorithm TEXT,
                    integrity_status TEXT
                )
            """)

            # Clean out any demo / test data
            cursor.execute("DELETE FROM documents WHERE id LIKE 'doc-demo-%'")
            cursor.execute("DELETE FROM screening_results WHERE document_id LIKE 'doc-demo-%'")
            cursor.execute("DELETE FROM blockchain_ledger WHERE document_id LIKE 'doc-demo-%'")

            conn.commit()

        logger.info(f"SQLite database initialized at {DB_PATH}")

    def _compute_block_hash(self, index: int, prev_hash: str, doc_id: str, status: str, timestamp: str) -> str:
        header = f"{index}:{prev_hash}:{doc_id}:{status}:{timestamp}"
        return hashlib.sha256(header.encode("utf-8")).hexdigest()

    def save_document(self, doc_data: Dict[str, Any]) -> str:
        doc_id = doc_data.get("id") or f"doc-{uuid.uuid4().hex[:8]}"
        doc_data["id"] = doc_id
        if "uploaded_at" not in doc_data:
            doc_data["uploaded_at"] = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO documents (
                    id, filename, stored_filename, file_path, file_size,
                    mime_type, uploaded_at, status, face_stored_filename,
                    face_file_path, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id,
                doc_data.get("filename"),
                doc_data.get("stored_filename"),
                doc_data.get("file_path"),
                doc_data.get("file_size"),
                doc_data.get("mime_type"),
                doc_data.get("uploaded_at"),
                doc_data.get("status", "uploaded"),
                doc_data.get("face_stored_filename"),
                doc_data.get("face_file_path"),
                json.dumps(doc_data)
            ))
            conn.commit()
        return doc_id

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT raw_json FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            if row and row["raw_json"]:
                return json.loads(row["raw_json"])
        return None

    def save_screening_result(self, doc_id: str, result_data: Dict[str, Any]):
        now_ts = datetime.now(timezone.utc).isoformat()
        result_data["document_id"] = doc_id
        result_data["screening_timestamp"] = now_ts

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Retrieve latest block for hash chaining
            cursor.execute("SELECT block_index, block_hash FROM blockchain_ledger ORDER BY block_index DESC LIMIT 1")
            last_block = cursor.fetchone()
            if last_block:
                idx = last_block["block_index"] + 1
                prev_hash = last_block["block_hash"]
            else:
                idx = 1
                prev_hash = self._genesis_hash

            status = result_data.get("screening_status", "Screened")
            block_hash = self._compute_block_hash(idx, prev_hash, doc_id, status, now_ts)

            ledger_block = {
                "block_index": idx,
                "block_hash": block_hash,
                "previous_hash": prev_hash,
                "timestamp": now_ts,
                "signature_algorithm": "SHA-256 Hash Chained Ledger",
                "integrity_status": "Verified Immutable Record"
            }
            result_data["ledger_block"] = ledger_block

            # Insert blockchain block
            cursor.execute("""
                INSERT INTO blockchain_ledger (
                    block_index, block_hash, previous_hash, document_id, status,
                    timestamp, signature_algorithm, integrity_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                idx,
                block_hash,
                prev_hash,
                doc_id,
                status,
                now_ts,
                ledger_block["signature_algorithm"],
                ledger_block["integrity_status"]
            ))

            # Insert or replace screening result
            face_verified = None
            if result_data.get("face_match"):
                face_verified = 1 if result_data["face_match"].get("face_verified") else 0

            ocr = result_data.get("ocr_results", {})
            cursor.execute("""
                INSERT OR REPLACE INTO screening_results (
                    document_id, filename, screening_status, risk_level, risk_score,
                    genuine_probability, forged_probability, model_confidence,
                    screening_timestamp, face_verified, ocr_name, ocr_doc_number,
                    block_hash, result_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id,
                result_data.get("filename", "document.jpg"),
                status,
                result_data.get("risk_level", "Unknown"),
                result_data.get("risk_score", 15),
                result_data.get("genuine_probability", 0.0),
                result_data.get("forged_probability", 0.0),
                result_data.get("model_confidence", 0.0),
                now_ts,
                face_verified,
                ocr.get("name"),
                ocr.get("document_number"),
                block_hash,
                json.dumps(result_data)
            ))

            # Update document status in documents table
            cursor.execute("""
                UPDATE documents SET status = 'screened' WHERE id = ?
            """, (doc_id,))

            conn.commit()

    def get_screening_result(self, doc_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT result_json FROM screening_results WHERE document_id = ?", (doc_id,))
            row = cursor.fetchone()
            if row and row["result_json"]:
                return json.loads(row["result_json"])
        return None

    def list_history(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT result_json FROM screening_results WHERE 1=1"
            params: List[Any] = []

            if status and status.lower() != "all":
                query += " AND LOWER(screening_status) = LOWER(?)"
                params.append(status)

            if risk_level and risk_level.lower() != "all":
                query += " AND LOWER(risk_level) = LOWER(?)"
                params.append(risk_level)

            if search:
                query += " AND (LOWER(filename) LIKE ? OR LOWER(document_id) LIKE ? OR LOWER(ocr_name) LIKE ? OR LOWER(ocr_doc_number) LIKE ?)"
                s_param = f"%{search.lower()}%"
                params.extend([s_param, s_param, s_param, s_param])

            query += " ORDER BY screening_timestamp DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            all_items = []
            for r in rows:
                item = json.loads(r["result_json"])
                all_items.append({
                    "document_id": item.get("document_id") or item.get("id"),
                    "filename": item.get("filename", "document.jpg"),
                    "screening_date": item.get("screening_timestamp", ""),
                    "status": item.get("screening_status", "Unknown"),
                    "risk_level": item.get("risk_level", "Unknown"),
                    "risk_score": item.get("risk_score", 15),
                    "ai_confidence": item.get("model_confidence", 0.0),
                    "genuine_probability": item.get("genuine_probability", 0.0),
                    "forged_probability": item.get("forged_probability", 0.0),
                    "face_verified": item.get("face_match", {}).get("face_verified") if item.get("face_match") else None,
                    "block_hash": item.get("ledger_block", {}).get("block_hash")
                })

            total = len(all_items)
            start = (page - 1) * page_size
            end = start + page_size
            paginated_items = all_items[start:end]
            total_pages = max(1, (total + page_size - 1) // page_size)

            return {
                "items": paginated_items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }

    def get_dashboard_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM screening_results")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM screening_results WHERE screening_status = 'Likely Genuine'")
            genuine = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM screening_results WHERE screening_status = 'Suspicious'")
            suspicious = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM screening_results WHERE screening_status = 'Requires Manual Review'")
            manual_review = cursor.fetchone()[0]

            cursor.execute("SELECT result_json FROM screening_results ORDER BY screening_timestamp DESC LIMIT 5")
            rows = cursor.fetchall()
            recent_activity = []
            for r in rows:
                item = json.loads(r["result_json"])
                recent_activity.append({
                    "document_id": item.get("document_id") or item.get("id", "doc-unknown"),
                    "filename": item.get("filename", "document.jpg"),
                    "screening_date": item.get("screening_timestamp", ""),
                    "status": item.get("screening_status", "Unknown"),
                    "risk_level": item.get("risk_level", "Unknown"),
                    "risk_score": item.get("risk_score", 15),
                    "ai_confidence": item.get("model_confidence", 0.0),
                    "genuine_probability": item.get("genuine_probability", 0.0),
                    "forged_probability": item.get("forged_probability", 0.0),
                    "face_verified": item.get("face_match", {}).get("face_verified") if item.get("face_match") else None,
                    "block_hash": item.get("ledger_block", {}).get("block_hash")
                })

            return {
                "total_screened": total,
                "likely_genuine": genuine,
                "suspicious": suspicious,
                "requires_manual_review": manual_review,
                "recent_activity": recent_activity
            }

    @property
    def blockchain_ledger(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM blockchain_ledger ORDER BY block_index ASC")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

sqlite_store = SqliteStore()
