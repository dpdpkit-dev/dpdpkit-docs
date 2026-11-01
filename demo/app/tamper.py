"""Play an insider with database access: quietly turn the latest withdrawal back into a grant."""

import sqlite3

db = sqlite3.connect("app.db")
changed = db.execute(
    "UPDATE dpdp_consent_events SET action = 'grant'"
    " WHERE seq = (SELECT MAX(seq) FROM dpdp_consent_events WHERE action = 'withdraw')"
).rowcount
db.commit()
print(f"rewrote {changed} consent row(s) in app.db: withdraw -> grant")
