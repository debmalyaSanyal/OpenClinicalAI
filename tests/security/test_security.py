from __future__ import annotations

import unittest

from core.security import check_role, redact_phi, stable_audit_hash


class TestSecurity(unittest.TestCase):
    def test_redact_phone_and_email(self) -> None:
        redacted = redact_phi("Call 9876543210 or test@example.com")
        self.assertNotIn("9876543210", redacted)
        self.assertNotIn("test@example.com", redacted)

    def test_role_check(self) -> None:
        self.assertTrue(check_role({"clinician"}, {"clinician"}).allowed)
        self.assertFalse(check_role({"admin"}, {"patient"}).allowed)

    def test_hash_stable(self) -> None:
        self.assertEqual(stable_audit_hash("x"), stable_audit_hash("x"))


if __name__ == "__main__":
    unittest.main()
