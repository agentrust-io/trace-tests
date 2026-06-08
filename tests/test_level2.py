import pytest


@pytest.mark.level2
@pytest.mark.skip(reason="Level 2 requires TEE attestation report verification")
class TestLevel2Conformance:
    def test_measurement_matches_tee_report(self, trust_record, attestation_report):
        raise NotImplementedError

    def test_attestation_report_freshness(self, trust_record, attestation_report):
        raise NotImplementedError

    def test_platform_matches_report_format(self, trust_record, attestation_report):
        raise NotImplementedError

    def test_cnf_key_sealed_in_tee_measurement(self, trust_record, attestation_report):
        raise NotImplementedError
