"""The app recorded in the 5-minute demo: the FastAPI quickstart, on a tiny shop.

`X-User` stands in for real authentication; `staff` is an admin.
"""

import os

from fastapi import Depends, FastAPI, Request

from dpdpkit import ConsoleNotifier, Contact
from dpdpkit.fastapi import DPDPKit, require_consent

app = FastAPI(title="Chai & Co (dpdpkit demo)")
USERS = {"u_42": {"name": "Asha Rao", "email": "asha@example.in"}}  # stand-in for your own tables


def current_user(request: Request) -> str | None:
    return request.headers.get("X-User")  # replace with your auth


def staff_role(request: Request) -> str | None:
    return "admin" if request.headers.get("X-User") == "staff" else None


def contact_for(user_id: str) -> Contact | None:
    user = USERS.get(user_id)
    return Contact(email=user["email"]) if user else None


dpdp = DPDPKit(
    db_url=os.environ.get("DATABASE_URL", "sqlite:///./app.db"),
    config="dpdpkit.yaml",
    principal_resolver=current_user,
    admin_guard=staff_role,
    contact_resolver=contact_for,
    notifier=ConsoleNotifier(),
    signing_key=os.environ.get("DPDPKIT_SIGNING_KEY", "dev-only"),
    migrate_on_startup=True,
)
dpdp.install(app, prefix="/dpdp")


@dpdp.kit.retention.register_handler
def erase_user_data(user_id: str, purposes: list[str]) -> None:
    if "account" in purposes:
        USERS.pop(user_id, None)


@app.post("/offers/send", dependencies=[Depends(require_consent("marketing"))])
def send_offer() -> dict[str, bool]:
    return {"sent": True}
