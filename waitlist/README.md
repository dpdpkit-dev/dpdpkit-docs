# Waitlist backend (Google Sheets + Apps Script)

The waitlist form on [docs/waitlist.md](../docs/waitlist.md) posts to a Google Apps Script web app,
[Code.gs](Code.gs). The script writes each signup to a Google Sheet that the project owns. It costs nothing,
has no monthly signup cap at waitlist volumes (Apps Script quotas are thousands of runs a day), keeps
entries until you delete them, and exports to CSV.

## One-time setup (about 10 minutes)

1. Sign in to Google with the account that should own the list. A project account is better than a personal one.
2. Create a Google Sheet called `dpdpkit waitlist`.
3. In the sheet, open **Extensions → Apps Script**. Replace the contents of `Code.gs` with [Code.gs](Code.gs)
   and save.
4. Click **Deploy → New deployment**, choose the type **Web app**, and set:
   - **Execute as:** Me
   - **Who has access:** Anyone

   Click **Deploy** and authorise the script. Google warns that the app is unverified because it's your own
   script: choose **Advanced → Go to … (unsafe)**. Copy the **Web app URL**
   (`https://script.google.com/macros/s/…/exec`).
5. Check that it works:

   ```bash
   curl -L -d "email=test@example.com&consent=yes&_ajax=1" "https://script.google.com/macros/s/…/exec"
   # {"ok":true}
   ```

   A `Waitlist` tab appears with a header row and the test entry. Delete the test row.
6. In GitHub, open `dpdpkit-dev/dpdpkit-docs` → **Settings → Secrets and variables → Actions → Variables**
   and add two repository variables:

   | Variable | Value |
   | --- | --- |
   | `WAITLIST_ACTION` | the Web app URL from step 4 |
   | `WAITLIST_PROCESSOR` | `Google (Google Sheets)` |

   Or, with the GitHub CLI:

   ```bash
   gh variable set WAITLIST_ACTION --repo dpdpkit-dev/dpdpkit-docs --body "https://script.google.com/macros/s/…/exec"
   gh variable set WAITLIST_PROCESSOR --repo dpdpkit-dev/dpdpkit-docs --body "Google (Google Sheets)"
   ```

7. Re-run the **Docs** workflow (Actions → Docs → Run workflow) or push to `main`. The form on the waitlist
   page is enabled once the deploy finishes. Sign up once from the live page and delete that row afterwards.

## Changing the script later

Edit `Code.gs` here first, paste it into the Apps Script editor, then use **Deploy → Manage deployments →
Edit → Version: New version**. That keeps the same URL. A *new deployment* would change the URL, and then
`WAITLIST_ACTION` would need updating.

## Running the list

The notice on the waitlist page makes promises. These are the steps that keep them:

- **Withdrawal or erasure request:** delete the person's row within 7 days.
- **Retention:** 12 months after dpdpkit Cloud becomes generally available, delete the remaining rows.
- **Access or correction request:** send them their row, or edit it.
- **Notice changes:** bump `extra.waitlist.notice_version` in `mkdocs.yml`. Each row records the version the
  person saw.
- **New-signup alerts:** in the sheet, use **Tools → Notification settings → Edit notifications**.
- **Metrics (GTM-10):** signups = number of rows minus the header.

Signing up again with the same email updates the existing row instead of adding a duplicate. Submissions
that fill the hidden `_gotcha` field (bots) are acknowledged but not stored.
