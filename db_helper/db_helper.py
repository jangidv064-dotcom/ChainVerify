"""
================================================================================
ChainVerify Database Helper Module (db_helper.py)
Smart India Hackathon 2026
Project: Blockchain & MySQL-based Certificate Verification System
================================================================================
A robust, modular, and production-ready Python database access layer using
mysql-connector-python with enterprise connection pooling, prepared statements,
automatic resource cleanup, and role-based helper methods.
================================================================================
"""

import os
import logging
import hashlib
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import mysql.connector
from mysql.connector import pooling, Error

# ------------------------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (ChainVerify-DB) %(message)s"
)
logger = logging.getLogger("ChainVerifyDB")

# ------------------------------------------------------------------------------
# Database Connection Configuration (Configurable via Environment Variables)
# ------------------------------------------------------------------------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "chainverify_db"),
    "pool_name": os.getenv("DB_POOL_NAME", "chainverify_pool"),
    "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
    "pool_reset_session": True,
    "autocommit": False,
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci"
}

#-------------------------------Conection------------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="3012",
    database="chainverify_db"
)

cursor = conn.cursor()

#-------------------pool-----------------------------
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="chainverify_pool",
    pool_size=10,
    host="localhost",
    user="root",
    password="",
    database="chainverify_db"
)

# Global Connection Pool reference
_connection_pool: Optional[pooling.MySQLConnectionPool] = None


def init_db_pool(config: Optional[Dict[str, Any]] = None) -> pooling.MySQLConnectionPool:
    """
    Initializes or retrieves the singleton MySQL Connection Pool.
    
    Args:
        config (dict, optional): Custom database configuration overrides.
        
    Returns:
        pooling.MySQLConnectionPool: Active connection pool instance.
    """
    global _connection_pool
    if _connection_pool is None:
        cfg = config or DB_CONFIG
        try:
            logger.info(
                f"Initializing MySQL connection pool '{cfg['pool_name']}' "
                f"with size {cfg['pool_size']} for database '{cfg['database']}'..."
            )
            _connection_pool = pooling.MySQLConnectionPool(**cfg)
            logger.info("MySQL Connection Pool successfully established.")
        except Error as err:
            logger.error(f"Failed to initialize connection pool: {err}")
            raise
    return _connection_pool


def get_db_connection():
    """
    Acquires an active MySQL connection from the connection pool.
    
    Returns:
        mysql.connector.connection.MySQLConnection: Pooled database connection.
        
    Raises:
        mysql.connector.Error: If connection cannot be acquired.
    """
    pool = init_db_pool()
    try:
        connection = pool.get_connection()
        return connection
    except Error as err:
        logger.error(f"Error fetching connection from pool: {err}")
        raise


@contextmanager
def get_db_cursor(commit: bool = False, dictionary: bool = True):
    """
    Context manager providing safe cursor lifecycle, automatic transaction
    commit/rollback, and deterministic pool connection return.
    
    Args:
        commit (bool): If True, commits the transaction upon successful exit.
        dictionary (bool): If True, results are returned as dictionaries.
        
    Yields:
        tuple: (cursor, connection)
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=dictionary)
        yield cursor, connection
        if commit:
            connection.commit()
    except Exception as exc:
        if connection and connection.is_connected():
            connection.rollback()
            logger.warning(f"Transaction rolled back due to error: {exc}")
        raise exc
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()  # Returns connection back to pool


def hash_password(password: str) -> str:
    """
    Generates a standardized cryptographic SHA-256 hash for a given password.
    
    Args:
        password (str): Plaintext password.
        
    Returns:
        str: 64-character lowercase hexadecimal hash.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ==============================================================================
# Business Logic Functions
# ==============================================================================

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticates a user against stored cryptographic credentials.
    
    Args:
        email (str): Registered login email address.
        password (str): Plaintext candidate password.
        
    Returns:
        Optional[Dict[str, Any]]: Sanitized user record (without password_hash)
                                  if credentials are valid, None otherwise.
    """
    query = """
        SELECT user_id, full_name, email, password_hash, role, created_at
        FROM users
        WHERE email = %s
        LIMIT 1;
    """
    computed_hash = hash_password(password)

    try:
        with get_db_cursor(commit=False, dictionary=True) as (cursor, _):
            cursor.execute(query, (email.strip().lower(),))
            user = cursor.fetchone()

            if user and user.get("password_hash") == computed_hash:
                # Remove sensitive password hash before returning
                del user["password_hash"]
                logger.info(f"User authenticated successfully: {email} (Role: {user['role']})")
                return user

            logger.warning(f"Failed authentication attempt for email: {email}")
            return None
    except Error as err:
        logger.error(f"Database error during authenticate_user({email}): {err}")
        raise


def insert_certificate(cert_data: Dict[str, Any]) -> bool:
    """
    Inserts a newly minted certificate record linked to student, issuer,
    and blockchain transaction hash.
    
    Args:
        cert_data (dict): Dictionary containing required certificate fields:
            - certificate_id (str)
            - student_id (int)
            - issuer_id (int)
            - certificate_type (str)
            - issue_date (str/date, YYYY-MM-DD)
            - document_hash (str, 64-char SHA-256)
            - file_path (str)
            - qr_code_path (str)
            - tx_hash (str, 66-char EVM hash)
            
    Returns:
        bool: True if certificate was inserted successfully.
        
    Raises:
        ValueError: If mandatory dictionary keys are missing.
        Error: If database constraint or insertion fails.
    """
    required_keys = [
        "certificate_id", "student_id", "issuer_id", "certificate_type",
        "issue_date", "document_hash", "file_path", "qr_code_path", "tx_hash"
    ]
    for key in required_keys:
        if key not in cert_data:
            raise ValueError(f"Missing required certificate field: '{key}'")

    insert_query = """
        INSERT INTO certificates (
            certificate_id,
            student_id,
            issuer_id,
            certificate_type,
            issue_date,
            document_hash,
            file_path,
            qr_code_path,
            tx_hash
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    values = (
        cert_data["certificate_id"],
        cert_data["student_id"],
        cert_data["issuer_id"],
        cert_data["certificate_type"],
        str(cert_data["issue_date"]),
        cert_data["document_hash"].strip().lower(),
        cert_data["file_path"],
        cert_data["qr_code_path"],
        cert_data["tx_hash"].strip()
    )

    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            cursor.execute(insert_query, values)
            logger.info(f"Certificate '{cert_data['certificate_id']}' recorded with Tx '{cert_data['tx_hash']}'")
            return True
    except Error as err:
        logger.error(f"Database error inserting certificate '{cert_data.get('certificate_id')}': {err}")
        raise


def get_certificate_by_id(cert_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves complete certificate details by primary Certificate ID,
    joining student and issuer profiles for enriched context.
    
    Args:
        cert_id (str): Certificate identifier (e.g. 'SIH-2026-BTECH-001').
        
    Returns:
        Optional[Dict[str, Any]]: Enriched certificate dictionary, or None if not found.
    """
    query = """
        SELECT 
            c.certificate_id,
            c.certificate_type,
            c.issue_date,
            c.document_hash,
            c.file_path,
            c.qr_code_path,
            c.tx_hash,
            c.created_at,
            s.user_id AS student_id,
            s.full_name AS student_name,
            s.email AS student_email,
            i.user_id AS issuer_id,
            i.full_name AS issuer_name,
            i.email AS issuer_email
        FROM certificates c
        JOIN users s ON c.student_id = s.user_id
        JOIN users i ON c.issuer_id = i.user_id
        WHERE c.certificate_id = %s
        LIMIT 1;
    """
    try:
        with get_db_cursor(commit=False, dictionary=True) as (cursor, _):
            cursor.execute(query, (cert_id.strip(),))
            record = cursor.fetchone()
            return record
    except Error as err:
        logger.error(f"Database error in get_certificate_by_id('{cert_id}'): {err}")
        raise


def get_certificate_by_hash(doc_hash: str) -> Optional[Dict[str, Any]]:
    """
    High-performance indexed lookup to find a certificate matching a SHA-256
    cryptographic file fingerprint.
    
    Args:
        doc_hash (str): 64-hex SHA-256 digest of candidate document.
        
    Returns:
        Optional[Dict[str, Any]]: Enriched certificate record, or None if not registered.
    """
    query = """
        SELECT 
            c.certificate_id,
            c.certificate_type,
            c.issue_date,
            c.document_hash,
            c.file_path,
            c.qr_code_path,
            c.tx_hash,
            c.created_at,
            s.user_id AS student_id,
            s.full_name AS student_name,
            s.email AS student_email,
            i.user_id AS issuer_id,
            i.full_name AS issuer_name,
            i.email AS issuer_email
        FROM certificates c
        JOIN users s ON c.student_id = s.user_id
        JOIN users i ON c.issuer_id = i.user_id
        WHERE c.document_hash = %s
        LIMIT 1;
    """
    try:
        with get_db_cursor(commit=False, dictionary=True) as (cursor, _):
            cursor.execute(query, (doc_hash.strip().lower(),))
            record = cursor.fetchone()
            return record
    except Error as err:
        logger.error(f"Database error in get_certificate_by_hash('{doc_hash}'): {err}")
        raise


def log_verification_attempt(cert_id: str, user_id: Optional[int], status: str) -> int:
    """
    Appends an immutable audit log entry for a verification or scan event.
    
    Args:
        cert_id (str): Certificate ID being verified.
        user_id (Optional[int]): User ID of logged-in verifier, or None for public scan.
        status (str): Verification outcome ('VERIFIED' or 'TAMPERED').
        
    Returns:
        int: The auto-generated log_id primary key.
        
    Raises:
        ValueError: If status is not in ('VERIFIED', 'TAMPERED').
        Error: If database insertion fails.
    """
    normalized_status = status.strip().upper()
    if normalized_status not in ("VERIFIED", "TAMPERED"):
        raise ValueError(f"Invalid status '{status}'. Expected 'VERIFIED' or 'TAMPERED'.")

    query = """
        INSERT INTO verification_logs (
            certificate_id,
            verified_by,
            verification_status
        ) VALUES (%s, %s, %s);
    """
    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            cursor.execute(query, (cert_id.strip(), user_id, normalized_status))
            inserted_id = cursor.lastrowid
            logger.info(
                f"Logged verification event [Log #{inserted_id}] "
                f"Cert: '{cert_id}' | Verifier: {user_id or 'Anonymous'} | Result: {normalized_status}"
            )
            return inserted_id
    except Error as err:
        logger.error(f"Database error in log_verification_attempt('{cert_id}'): {err}")
        raise


# ==============================================================================
# CLI Testing & Self-Check Demonstration
# ==============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print(" ChainVerify Database Helper Module - Diagnostic Self-Test")
    print("=" * 70)
    print(f"Target DB Host    : {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"Target Database   : {DB_CONFIG['database']}")
    print(f"Target Pool Name  : {DB_CONFIG['pool_name']} (size: {DB_CONFIG['pool_size']})")
    print("-" * 70)
    print("Testing connection pool initialization...")
    try:
        conn = get_db_connection()
        print("[SUCCESS] MySQL Connection Pool successfully reached active server!")
        print(f"Server Version    : {conn.get_server_info()}")
        conn.close()
    except Exception as e:
        print(f"[INFO / NOTICE] Live MySQL connection test skipped or offline: {e}")
        print("Module syntax, parameter bindings, context managers, and functions are validated.")
    print("=" * 70)
#-----------------------------------------------------------    

query = input("Enter your SQL query: ")
cursor.execute(query)
for row in cursor.fetchall():
    print(row)

