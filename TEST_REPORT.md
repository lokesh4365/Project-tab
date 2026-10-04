# Verification report

Run on 3 October 2026 with Python 3.12 and the exact dependency versions in requirements.txt.

- 10 automated tests passed using `python -m unittest discover -s tests -v`.
- Money allocation tested across 1,000 totals for conservation.
- Equal sample split: ₹777 / 3 = ₹259 each.
- Item allocation, proportionate tax, large discount, invalid owners and invalid amounts checked.
- Streamlit AppTest completed onboarding, sample loading, item mode, ownership changes, review confirmation and tip changes. A change to the recap correctly invalidated confirmation.
- SMTP mocked: exact preview text and single recipient passed to the sender. No actual email was sent.
- Local Streamlit server started successfully.

Not verified: live Gemini extraction/chat, real Gmail delivery, external deployment, or screenshot-based visual QA. Browser installation failed in the preparation environment, so desktop/mobile appearance should be inspected during deployment. Source CSS includes a mobile breakpoint, but this is not a claim of visual verification.

No GitHub repository, public app link, or course submission has been created by this package.
