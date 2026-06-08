import pytest


@pytest.mark.level1
@pytest.mark.skip(reason="Level 1 requires a signed EAT implementation")
class TestLevel1Conformance:
    def test_eat_is_cose_sign1(self, signed_eat_bytes):
        raise NotImplementedError

    def test_eat_protected_header_content_type(self, signed_eat_bytes):
        raise NotImplementedError

    def test_signature_verifies_against_cnf_key(self, signed_eat_bytes):
        raise NotImplementedError

    def test_eat_nonce_matches_challenge(self, signed_eat_bytes, challenge_nonce):
        raise NotImplementedError
