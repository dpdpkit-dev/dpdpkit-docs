// Waitlist backend for docs/waitlist.md: a Google Apps Script web app that appends each signup to the
// "Waitlist" tab of a spreadsheet: the one it is bound to, or for a standalone script project, the one named
// by the SHEET_ID script property. Setup steps are in waitlist/README.md.
//
// Apps Script cannot set HTTP status codes, so every reply is 200 and the form reads {"ok": ...} instead.
// Requests from the docs site's JavaScript carry _ajax=1 and get JSON; a plain form post (no JavaScript)
// gets a short HTML page.

const SHEET_NAME = "Waitlist";
const DOCS_URL = "https://dpdpkit-dev.github.io/dpdpkit-docs/dev/waitlist/";
const FIELDS = [
  "email",
  "organisation",
  "stack",
  "interest_cloud",
  "interest_services",
  "interest_design_partner",
  "consent",
  "notice_version",
];
const MAX_LENGTH = 200;
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function doPost(e) {
  const p = (e && e.parameter) || {};
  const ajax = p._ajax === "1";
  if (p._gotcha) return reply_(ajax, true); // honeypot: pretend it worked, store nothing

  const email = String(p.email || "").trim().toLowerCase();
  if (!EMAIL.test(email) || email.length > MAX_LENGTH || p.consent !== "yes") {
    return reply_(ajax, false, "invalid");
  }

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const sheet = sheet_();
    const existing = sheet.getRange("B:B").createTextFinder(email).matchEntireCell(true).findNext();
    const row = [new Date()].concat(FIELDS.map((f) => (f === "email" ? email : clean_(p[f]))));
    if (existing) {
      // Signing up again refreshes the entry (new interests, newer notice version) instead of duplicating it.
      sheet.getRange(existing.getRow(), 1, 1, row.length).setValues([row]);
    } else {
      sheet.appendRow(row);
    }
  } finally {
    lock.releaseLock();
  }
  return reply_(ajax, true);
}

function sheet_() {
  const book =
    SpreadsheetApp.getActiveSpreadsheet() ||
    SpreadsheetApp.openById(PropertiesService.getScriptProperties().getProperty("SHEET_ID"));
  const sheet = book.getSheetByName(SHEET_NAME) || book.insertSheet(SHEET_NAME);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(["received_at"].concat(FIELDS));
    sheet.setFrozenRows(1);
  }
  return sheet;
}

// Trims, caps length, and stops spreadsheet formula injection (=, +, -, @ at the start of a cell).
function clean_(value) {
  const text = String(value == null ? "" : value).trim().slice(0, MAX_LENGTH);
  return /^[=+\-@]/.test(text) ? "'" + text : text;
}

function reply_(ajax, ok, error) {
  if (ajax) {
    const body = ok ? { ok: true } : { ok: false, error: error };
    return ContentService.createTextOutput(JSON.stringify(body)).setMimeType(ContentService.MimeType.JSON);
  }
  const message = ok
    ? "Thanks, you're on the list. We'll email you when there is news."
    : "That didn't go through: please enter a valid email address and tick the consent box.";
  return HtmlService.createHtmlOutput(
    "<p>" + message + '</p><p><a href="' + DOCS_URL + '" target="_top">Back to the dpdpkit docs</a></p>'
  ).setTitle("dpdpkit waitlist");
}
