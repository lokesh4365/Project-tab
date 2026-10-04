# AfterTab presentation notes

## A 90-second walkthrough

1. **Problem (10 seconds):** Explain the dinner-bill scenario in your own words. The goal is a checkable split, not just a chatbot response.
2. **Open a table (10 seconds):** Enter your name and optional email. Show the sample receipt if you have not yet configured live services. Say clearly when using sample data.
3. **Read and review (20 seconds):** Upload a real INR receipt, inspect the item totals and printed-total check. Fix a value if needed. Do not present the sample as live OCR.
4. **Split (20 seconds):** Show equal mode, then assign a dish to one person. Explain that taxes and discounts follow consumption in item mode.
5. **Ask (10 seconds):** Ask how tax is shared. Show that conversation cannot modify the settlement directly.
6. **Deliver (20 seconds):** Check the exact recap, confirm it, and send it to your own email. Show actual arrival only if received. Otherwise explain the observed failure honestly.

## Questions you should be able to answer

**Why this project?** It turns messy information from a photo into an action people can verify. Add your own real motivation; do not invent a story.

**Where is Gemini used?** `extract_receipt` requests a structured receipt. `ask_receipt` uses the current calculated recap and recent messages for explanations.

**Why separate prompts?** It keeps the model's job and constraints readable, without mixing them into UI logic.

**How does memory work?** Streamlit session state retains the profile, receipt and bounded chat history. The chat request includes recent turns; there is no permanent database.

**How do you avoid floating-point money errors?** Convert to integer paise with Decimal and half-up rounding. Largest-remainder allocation preserves the exact final total.

**What happens if OCR is wrong?** Users can edit the items. A comparison with the printed total highlights discrepancies before the recap is confirmed.

**What are the main limitations?** One payer and currency, no permanent history, fallible OCR, provider quotas, and no live-service test until configured with actual accounts.

## Before submitting

- [ ] Run the tests locally.
- [ ] Configure and verify Gemini with a real photo and follow-up question.
- [ ] Verify one real email arrives from the deployed app.
- [ ] Upload only source/configuration templates, never actual secrets.
- [ ] Open both the GitHub and Streamlit links in a fresh session.
- [ ] Share the demo access code privately if enabled.
- [ ] Include the two real links in the submission form.
- [ ] Follow the course's AI-assistance disclosure rules and explain every major function yourself.

## Useful personal improvements

Use your own receipt photo with private details removed, refine one piece of interface copy in your own voice, and choose a concrete extra feature you can implement and explain. Authenticity comes from understanding the tradeoffs and showing evidence that your version works.
