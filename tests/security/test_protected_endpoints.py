"""
Security Tests: Endpoint Authorization & RBAC Enforcement
"""
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.config import get_settings
from app.database.models import User
from app.security.authorization import (
    require_admin,
    require_investigator,
    require_analyst,
    require_any_authenticated
)
from app.security.authentication import get_current_user
from app.api.routes.reports import trigger_retrain, export_csv, list_alerts, resolve_alert
from app.database.repositories.audit_repo import AuditRepository

settings = get_settings()


def test_rbac_require_admin_hierarchy():
    admin = User(id=1, username="admin_boss", role="admin")
    investigator = User(id=2, username="inv_agent", role="investigator")
    analyst = User(id=3, username="analyst_jane", role="analyst")
    client = User(id=4, username="api_client", role="client")

    # Only admin allowed
    assert require_admin(admin) == admin
    for u in [investigator, analyst, client]:
        with pytest.raises(HTTPException) as exc:
            require_admin(u)
        assert exc.value.status_code == 403


def test_rbac_require_investigator_hierarchy():
    admin = User(id=1, username="admin_boss", role="admin")
    investigator = User(id=2, username="inv_agent", role="investigator")
    analyst = User(id=3, username="analyst_jane", role="analyst")
    client = User(id=4, username="api_client", role="client")

    # Both admin and investigator allowed
    assert require_investigator(admin) == admin
    assert require_investigator(investigator) == investigator

    # Analyst and client blocked
    for u in [analyst, client]:
        with pytest.raises(HTTPException) as exc:
            require_investigator(u)
        assert exc.value.status_code == 403


def test_rbac_require_analyst_hierarchy():
    admin = User(id=1, username="admin_boss", role="admin")
    investigator = User(id=2, username="inv_agent", role="investigator")
    analyst = User(id=3, username="analyst_jane", role="analyst")
    client = User(id=4, username="api_client", role="client")

    assert require_analyst(admin) == admin
    assert require_analyst(investigator) == investigator
    assert require_analyst(analyst) == analyst

    with pytest.raises(HTTPException) as exc:
        require_analyst(client)
    assert exc.value.status_code == 403


def test_get_current_user_with_admin_key(db_session):
    request = MagicMock()
    request.query_params = {}
    user = get_current_user(request=request, credentials=None, api_key=settings.ADMIN_API_KEY, db=db_session)
    assert user is not None
    assert user.role == "admin"


def test_get_current_user_with_query_param_key(db_session):
    request = MagicMock()
    request.query_params = {"api_key": settings.ADMIN_API_KEY}
    user = get_current_user(request=request, credentials=None, api_key=None, db=db_session)
    assert user is not None
    assert user.role == "admin"


def test_get_current_user_missing_credentials(db_session):
    request = MagicMock()
    request.query_params = {}
    with pytest.raises(HTTPException) as exc:
        get_current_user(request=request, credentials=None, api_key=None, db=db_session)
    assert exc.value.status_code == 401


def test_export_csv_and_retrain_endpoints(db_session):
    admin = User(id=1, username="testadmin", role="admin")

    # Export CSV succeeds with authorized user
    res = export_csv(db=db_session, user=admin)
    assert res.media_type == "text/csv"
    assert "attachment; filename=" in res.headers["content-disposition"]

    # Retrain succeeds with admin
    retrain_res = trigger_retrain(db=db_session, user=admin)
    assert retrain_res["status"] == "SUCCESS"
    assert "retrained_at" in retrain_res


def test_alert_lifecycle_and_audit_logging(db_session):
    investigator = User(id=2, username="testinv", role="investigator")

    # List alerts
    alerts = list_alerts(limit=10, unresolved_only=False, db=db_session, user=investigator)
    assert isinstance(alerts, list)

    # Audit logging verification
    audit = AuditRepository(db_session)
    log_entry = audit.log(
        action="SECURITY_TEST_AUDIT",
        resource_type="TestResource",
        resource_id="res_123",
        user_id=investigator.id,
        username=investigator.username,
        details={"test": True}
    )
    assert log_entry.id is not None
    assert log_entry.action == "SECURITY_TEST_AUDIT"
