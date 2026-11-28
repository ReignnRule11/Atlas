import pytest
from pydantic import ValidationError

from app.schemas.proof import EvidenceCreate, ProjectCreate, ProjectUpdate


def test_project_title_is_trimmed_and_url_must_be_http():
    payload = ProjectCreate(title="  Atlas  ", project_url="https://example.com")
    assert payload.title == "Atlas"
    with pytest.raises(ValidationError):
        ProjectCreate(title="   ")
    with pytest.raises(ValidationError):
        ProjectCreate(title="Atlas", project_url="javascript:alert(1)")


def test_project_update_rejects_null_title():
    with pytest.raises(ValidationError):
        ProjectUpdate(title=None)


def test_evidence_is_normalized_and_url_validated():
    payload = EvidenceCreate(title="  Delivery demo ", evidence_url="https://example.com/demo")
    assert payload.title == "Delivery demo"
    with pytest.raises(ValidationError):
        EvidenceCreate(title="Demo", evidence_url="file:///etc/passwd")
