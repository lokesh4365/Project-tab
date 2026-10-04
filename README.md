# AfterTab
### Keep the memories. Split the bill.

A small receipt assistant for the awkward five minutes after dinner: one person has paid, three people ordered different things, and nobody wants to do the maths.

AfterTab reads a receipt with Gemini, lets the table correct it, calculates each person's share in integer paise, and emails the exact reviewed recap. The visual direction is a warm café receipt: paper colours, forest-green text, terracotta buttons, and a tilted sample receipt.

## What works

- Photo or typed receipt → structured extraction with Gemini.
- Editable line totals, tax/fee/discount adjustment, and optional extra tip.
- Equal splits or per-item sharing, including dishes shared by several people.
- Printed-total mismatch check; final shares always sum to the calculated total.
- Context-aware receipt questions with short conversation memory.
- Exact-message preview, explicit review checkbox, email delivery, and text download.
- Clearly labelled sample mode without API keys.
- Optional access code for a coursework deployment; session-level email cooldown and duplicate prevention.

## Run locally (Python 3.12 recommended)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows PowerShell activation: `.venv\Scripts\Activate.ps1`.
Open the localhost URL printed by Streamlit. Enter a name and click **Load sample table** to explore without credentials.

## Connect the live features

1. Create a Gemini API key at https://aistudio.google.com/apikey.
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
3. Set `GEMINI_API_KEY`. The configurable default is `gemini-2.5-flash`; use an available text-and-image model supported by your account if that model is unavailable. No model/key was live-tested in this delivery.
4. For email, enable Google 2-Step Verification and create an App Password at https://myaccount.google.com/apppasswords. This option depends on your account policy. Put the Gmail sender and App Password in the two Gmail secrets. Never use your normal account password.
5. Set `APP_ACCESS_CODE` to a long random code for a public demo and share it privately with your evaluator. Remove this setting locally if you do not need a gate.
6. Restart the app. Upload an INR receipt, review, ask a question, then send a recap to your own email.

Credentials belong only in local secrets or the hosting secrets panel. Never paste them into chat, screenshots, README files, or GitHub. The example file contains placeholders only.

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository named `aftertab` and upload the contents of this directory at its root. Include `.streamlit/config.toml`, `.streamlit/secrets.toml.example` and `.gitignore`; exclude the real secrets file and virtual environment.
2. At https://share.streamlit.io, connect GitHub and create an app from the repository, selecting `app.py` as the entry point and Python 3.12.
3. Paste your real secrets into the deployment's secrets settings. Keep the repository free of credentials.
4. Deploy and test the public link in a fresh browser session. Verify access-code entry, photo extraction, editing, chat, and one actual email to yourself.
5. Submit your actual GitHub link and live Streamlit URL at https://forms.ccbp.in/ai-vision-chatbot-last-project-submission.

The supplied assignment lists **4 October, 11:59 PM** as its deadline. This package has not been uploaded to GitHub, deployed, or submitted. A sample-mode-only deployment does not prove the required live AI → email flow.

## Files

| File | Purpose |
| --- | --- |
| `app.py` | Onboarding, receipt review, splitting controls, chat and recap UI |
| `prompts.py` | Scoped extraction and explanation prompts |
| `core.py` | Input validation, paise arithmetic, allocation and recap text |
| `services.py` | Gemini structured output, image preparation, Gmail SMTP |
| `tests/` | Calculation, UI-flow and mocked email boundary tests |
| `.streamlit/` | Theme and credential template |
| `DEMO_GUIDE.md` | Walkthrough and code explanation for presentation |

## Checks

```bash
python -m unittest discover -s tests -v
```

Tests cover money conservation, paise rounding, discounts, item-based allocation, invalid assignments, email input, onboarding, sample loading, changing splits and confirmation invalidation. A mocked SMTP test verifies the message and recipient without sending email.

## Design choices worth understanding

**The AI does not decide the debt.** Gemini turns a picture into editable data. Python calculates the settlement. A confident-looking AI response cannot silently change anyone's share.

**A line total is not a unit price.** Quantity is deliberately kept in the item label. This avoids multiplying a receipt line twice.

**Confirmation follows the actual recap.** Changing amounts or names creates a new confirmation control. An old checked box cannot approve a new settlement.

**Equal and item-based splits have different rules.** Equal mode divides the final bill equally. Item mode apportions each item among its selected owners, then distributes net adjustments in proportion to their item shares. Remainder paise use a deterministic table order.

**The recap is deterministic.** The assignment's free-form AI summary is replaced with exact reviewed amounts. Gemini still supplies both photo understanding and conversational explanation.

## Limits and next steps

- INR only; one receipt, one full-bill payer, and up to 12 people. No partial-payments ledger, refunds, or money transfer integration.
- OCR can be wrong. The printed-total check catches arithmetic mismatches, not every misread item. The user must inspect the receipt.
- Temporary browser-session state; no database or cross-device history. Hosting logs and external provider retention are outside the app's session policy.
- Uploaded photos are resized and stripped of EXIF before transmission. Image/text data goes to Gemini only on analysis; chat includes the current settlement and recent messages. Sending a recap shares it with Gmail and the selected recipient.
- The access code and per-session cooldown suit a controlled coursework demo, not a production public email service. A production version needs authenticated accounts, verified recipient ownership, durable rate limits and abuse monitoring.
- SMTP acceptance means the sender accepted the message, not confirmed inbox delivery. Some hosting networks block SMTP; check the deployed email flow. If blocked, adapt `send_email` to an HTTPS transactional-email provider before submitting.
- API quotas, model availability, Gmail App Password eligibility, and deployment require your accounts. Real Gemini and Gmail requests were not executed during preparation.

## References and provenance

Adapted from the supplied MacroSnap workshop's onboarding → multimodal AI → delivery pattern. AfterTab adds reviewable structured data, deterministic settlement, receipt reconciliation, and a custom visual identity. AI assistance was used to prepare this implementation; understand and adapt it, and follow your course's disclosure rules. Do not claim unperformed user research or live tests.

Official references:
- https://googleapis.github.io/python-genai/
- https://ai.google.dev/gemini-api/docs/image-understanding
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app
- https://docs.streamlit.io/develop/concepts/connections/secrets-management
