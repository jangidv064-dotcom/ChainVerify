-- ============================================================================
-- ChainVerify Database Seed Data
-- Smart India Hackathon 2026
-- Project: Blockchain & MySQL-based Certificate Verification System
-- Target Database: chainverify_db
-- ============================================================================

USE `chainverify_db`;

-- Temporarily disable foreign key checks for clean truncation/population
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE `verification_logs`;
TRUNCATE TABLE `certificates`;
TRUNCATE TABLE `users`;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- 1. SEED DATA: users
-- Roles:
--   1 Admin    : Dr. Rajesh Sharma (University Registrar / Issuing Authority)
--   2 Students : Aarav Patel, Priya Sharma
--   1 Verifier : Vikram Malhotra (Senior HR & Talent Acquisition, TCS)
--
-- Password hashes below are generated using SHA-256 (compatible with standard
-- modern auth implementations & db_helper.py).
-- Default Plaintext Passwords for Hackathon Testing:
--   - admin.sih@chainverify.edu   : Admin@ChainVerify2026!
--   - aarav.patel@student.edu     : Student@Aarav2026!
--   - priya.sharma@student.edu    : Student@Priya2026!
--   - tcs.recruiter@tcs.com       : Verifier@TCS2026!
-- ============================================================================
INSERT INTO `users` (`user_id`, `full_name`, `email`, `password_hash`, `role`, `created_at`) VALUES
(
    1,
    'Dr. Rajesh Sharma',
    'admin.sih@chainverify.edu',
    'd391a42e8ec1e532e2ddc2f44556c409e059ff33551fc2f0e8b99ceefa539725',
    'admin',
    '2026-01-10 09:00:00'
),
(
    2,
    'Aarav Patel',
    'aarav.patel@student.edu',
    '7e01e1865403edd7f6ae6e7580852d8381b019b708add3b86155f17658f89f2c',
    'student',
    '2026-01-15 10:15:00'
),
(
    3,
    'Priya Sharma',
    'priya.sharma@student.edu',
    'b9e43261e379bc8fb91328ace95dfa4de9ba53df65cc52c52a9c345fbb6a547f',
    'student',
    '2026-01-15 10:20:00'
),
(
    4,
    'Vikram Malhotra',
    'tcs.recruiter@tcs.com',
    '25f2274affeeef31fe2405e62e5e3aef407945a3623a992f5edadd8b7e1b64d8',
    'verifier',
    '2026-02-01 14:30:00'
);

-- ============================================================================
-- 2. SEED DATA: certificates
-- Contains 2 production-grade sample records:
--   - B.Tech Degree Certificate issued to Aarav Patel (student_id = 2)
--   - National AI Merit Honor issued to Priya Sharma (student_id = 3)
--   - Both issued by Registrar Dr. Rajesh Sharma (issuer_id = 1)
--
-- Document Hashes: 64-character SHA-256 digests matching certificate PDF files
-- Tx Hashes: 66-character EVM-compatible Ethereum/Polygon ledger transaction IDs
-- ============================================================================
INSERT INTO `certificates` (
    `certificate_id`,
    `student_id`,
    `issuer_id`,
    `certificate_type`,
    `issue_date`,
    `document_hash`,
    `file_path`,
    `qr_code_path`,
    `tx_hash`,
    `created_at`
) VALUES
(
    'SIH-2026-BTECH-001',
    2,
    1,
    'Bachelor of Technology in Computer Science & Engineering',
    '2026-05-15',
    'e9d851f120a85600a59211672693d695e6d80f01aea3bd21b55abc4a01e555ba',
    '/storage/certificates/2026/SIH-2026-BTECH-001.pdf',
    '/storage/qrcodes/2026/SIH-2026-BTECH-001_qr.png',
    '0x7b9c1482de5b8392cf99a80392adfe715694821a37c09361a8ef15309d431201',
    '2026-05-15 11:30:00'
),
(
    'SIH-2026-HON-002',
    3,
    1,
    'National Merit Gold Medal - AI & Machine Learning',
    '2026-06-20',
    '5f1287fc627ae8227525c32453c34816a7d04f25f900cea451ac84081f2d3426',
    '/storage/certificates/2026/SIH-2026-HON-002.pdf',
    '/storage/qrcodes/2026/SIH-2026-HON-002_qr.png',
    '0x4a82cf91350812de4801fbce71839201594837a281048bca64028371940182bc',
    '2026-06-20 16:45:00'
);

-- ============================================================================
-- 3. SEED DATA: verification_logs
-- Demonstrates both authenticated recruiter verification and public scan:
--   - Log 1: Authenticated background check by TCS Recruiter (user_id = 4) -> VERIFIED
--   - Log 2: Anonymous public QR scan via mobile camera -> VERIFIED
--   - Log 3: Tampered document upload attempt flagged by system -> TAMPERED
-- ============================================================================
INSERT INTO `verification_logs` (
    `log_id`,
    `certificate_id`,
    `verified_by`,
    `verification_status`,
    `scanned_at`
) VALUES
(
    1,
    'SIH-2026-BTECH-001',
    4,
    'VERIFIED',
    '2026-09-21 08:30:00'
),
(
    2,
    'SIH-2026-HON-002',
    NULL,
    'VERIFIED',
    '2026-09-21 08:45:12'
),
(
    3,
    'SIH-2026-BTECH-001',
    NULL,
    'TAMPERED',
    '2026-09-21 09:05:30'
);
