-- ============================================================================
-- ChainVerify Database Schema
-- Smart India Hackathon 2026
-- Project: Blockchain & MySQL-based Certificate Verification System
-- Target DBMS: MySQL 8.0+ / MariaDB 10.5+
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Database Initialization
-- ----------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS `chainverify_db`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE `chainverify_db`;

-- Temporarily disable foreign key checks for safe re-creation
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `verification_logs`;
DROP TABLE IF EXISTS `certificates`;
DROP TABLE IF EXISTS `users`;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- Table: users
-- Description: Stores authentication credentials, identity, and role-based
--              access levels for administrators, students, and verifiers.
-- ============================================================================
CREATE TABLE `users` (
    `user_id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique internal surrogate ID',
    `full_name` VARCHAR(100) NOT NULL COMMENT 'Full legal name of the user/entity',
    `email` VARCHAR(100) NOT NULL UNIQUE COMMENT 'Unique login email address',
    `password_hash` VARCHAR(255) NOT NULL COMMENT 'Salted & hashed password (Argon2id/PBKDF2/bcrypt)',
    `role` ENUM('admin', 'student', 'verifier') NOT NULL COMMENT 'Role-based access control level',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Account creation timestamp',

    -- Indexes
    INDEX `idx_users_email` (`email`),
    INDEX `idx_users_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User identity and access management';

-- ============================================================================
-- Table: certificates
-- Description: Stores metadata of issued educational/vocational certificates,
--              including SHA-256 document fingerprint, storage paths, and
--              public blockchain ledger transaction hashes.
-- ============================================================================
CREATE TABLE `certificates` (
    `certificate_id` VARCHAR(50) NOT NULL PRIMARY KEY COMMENT 'Human-readable unique ID (e.g., SIH-2026-BCH-001)',
    `student_id` INT NOT NULL COMMENT 'FK referencing recipient student in users table',
    `issuer_id` INT NOT NULL COMMENT 'FK referencing issuing authority/admin in users table',
    `certificate_type` VARCHAR(100) NOT NULL COMMENT 'Type/Title of certificate (e.g., Degree, Merit, Completion)',
    `issue_date` DATE NOT NULL COMMENT 'Official certificate issuance date',
    `document_hash` VARCHAR(64) NOT NULL COMMENT 'Cryptographic SHA-256 hash (64 hex chars) of original PDF',
    `file_path` VARCHAR(255) NOT NULL COMMENT 'Relative or absolute file system/S3 URI of certificate PDF',
    `qr_code_path` VARCHAR(255) NOT NULL COMMENT 'Storage path of dynamically generated verification QR code image',
    `tx_hash` VARCHAR(66) NOT NULL COMMENT 'Ethereum/Polygon blockchain transaction hash (0x + 64 hex chars)',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Metadata registration timestamp',

    -- Foreign Key Constraints
    CONSTRAINT `fk_certificates_student`
        FOREIGN KEY (`student_id`) REFERENCES `users` (`user_id`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT `fk_certificates_issuer`
        FOREIGN KEY (`issuer_id`) REFERENCES `users` (`user_id`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Indexes for High Performance Lookup
    INDEX `idx_certificates_doc_hash` (`document_hash`) COMMENT 'High-speed lookup for offline/file upload verification',
    INDEX `idx_certificates_tx_hash` (`tx_hash`) COMMENT 'Quick blockchain transaction matching',
    INDEX `idx_certificates_student` (`student_id`) COMMENT 'Fast retrieval of all certificates for student dashboard',
    INDEX `idx_certificates_issuer` (`issuer_id`) COMMENT 'Auditing issued certificates by admin entity'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Certificate metadata and cryptographic ledger anchor';

-- ============================================================================
-- Table: verification_logs
-- Description: Audit trail recording every scan/lookup attempt. Tracks whether
--              the cryptographic fingerprint matched the blockchain registry.
-- ============================================================================
CREATE TABLE `verification_logs` (
    `log_id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Sequential audit entry ID',
    `certificate_id` VARCHAR(50) NOT NULL COMMENT 'FK referencing queried certificate',
    `verified_by` INT NULL DEFAULT NULL COMMENT 'FK referencing verifier user if authenticated, NULL if public anonymous scan',
    `verification_status` ENUM('VERIFIED', 'TAMPERED') NOT NULL COMMENT 'Verification outcome: VERIFIED=Tamper-free, TAMPERED=Hash mismatch',
    `scanned_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Exact moment verification occurred',

    -- Foreign Key Constraints
    CONSTRAINT `fk_verification_logs_cert`
        FOREIGN KEY (`certificate_id`) REFERENCES `certificates` (`certificate_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT `fk_verification_logs_verifier`
        FOREIGN KEY (`verified_by`) REFERENCES `users` (`user_id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    -- Indexes for Auditing & Analytics
    INDEX `idx_logs_cert_id` (`certificate_id`) COMMENT 'Audit trail retrieval per certificate',
    INDEX `idx_logs_verified_by` (`verified_by`) COMMENT 'Auditing verifier activity',
    INDEX `idx_logs_status` (`verification_status`) COMMENT 'Tamper detection rate analytics',
    INDEX `idx_logs_scanned_at` (`scanned_at`) COMMENT 'Timeline and frequency reporting'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Immutable audit trail of certificate verification attempts';
