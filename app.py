"""AfterTab — photograph, check, split, send. Run: streamlit run app.py"""
import copy
import hashlib
import hmac
import os
import time
from pathlib import Path
import streamlit as st
from core import cents, money, split_bill, summary_text, valid_email
from services import extract_receipt, ask_receipt, send_email

st.set_page_config(page_title='AfterTab · leave the maths at the table', page_icon='🧾', layout='wide')
st.markdown('''<style>
.block-container{max-width:1160px;padding-top:2rem;padding-bottom:4rem}
h1,h2,h3{letter-spacing:-.045em} h1{font-family:Georgia,serif;font-size:4.3rem!important;line-height:1.05!important}
.brand{font-size:15px;font-weight:800;letter-spacing:.16em}.eyebrow{color:#BD4B2E;font-size:12px;letter-spacing:.16em;font-weight:700;margin:2rem 0 1rem}
.hero-note{font-size:18px;color:#617267;max-width:540px;line-height:1.6}
.stButton button{border-radius:8px} div[data-testid="stMetric"]{background:#eee9df;padding:18px;border-radius:10px}
footer{visibility:hidden}.receipt-card{background:#fffdf7;padding:28px;border:1px dashed #aaa28d;border-radius:3px;transform:rotate(2deg);box-shadow:8px 12px 0 #e7e0d1;font-family:monospace;margin:24px}
.receipt-card p{display:flex;justify-content:space-between;font-size:14px}.receipt-card h3{text-align:center;font-family:monospace;letter-spacing:.07em}
@media(max-width:640px){h1{font-size:2.8rem!important}.block-container{padding-top:1rem}.receipt-card{margin:15px 4px}}
</style>''', unsafe_allow_html=True)


def secret(name, default=''):
    try:
        return str(st.secrets.get(name, os.getenv(name, default)))
    except FileNotFoundError:
        return os.getenv(name, default)


def set_receipt(receipt, demo=False):
    st.session_state.receipt = copy.deepcopy(receipt)
    st.session_state.demo = demo
    st.session_state.revision = st.session_state.get('revision', 0) + 1
    st.session_state.history = []
    st.session_state.pop('confirmed_digest', None)


SAMPLE = {'merchant': 'Beach Road Canteen · sample', 'currency': 'INR',
          'items': [{'item': 'Paneer wrap × 2', 'amount': 280.0},
                    {'item': 'Chicken sandwich', 'amount': 190.0},
                    {'item': 'Cold coffee × 3', 'amount': 270.0}],
          'adjustment': 37.0, 'printed_total': 777.0,
          'notes': ['Fictional sample receipt. Prices are for demonstration only.']}
key = secret('GEMINI_API_KEY')
model = secret('GEMINI_MODEL', 'gemini-2.5-flash')
access = secret('APP_ACCESS_CODE')

st.markdown('<div class="brand">AFTERTAB <span style="float:right;font-weight:400;letter-spacing:0">A little less “who owes what?”</span></div>', unsafe_allow_html=True)
st.divider()
if 'profile' not in st.session_state:
    left, right = st.columns([1.25, 1], gap='large')
    with left:
        st.markdown('<div class="eyebrow">GOOD FOOD. CLEAN SPLITS.</div>', unsafe_allow_html=True)
        st.title('Keep the memories.\nSplit the bill.')
        st.markdown('<p class="hero-note">One receipt, a few friends, and no awkward calculator handover. Check the details. Give everyone their share.</p>', unsafe_allow_html=True)
        with st.form('welcome'):
            name = st.text_input('What should we call you?', placeholder='Your first name', max_chars=40)
            email = st.text_input('Your email · optional', placeholder='For your confirmed split', max_chars=160)
            code = st.text_input('Demo access code', type='password') if access else ''
            submitted = st.form_submit_button('Start a table →', type='primary')
        if submitted:
            if not name.strip():
                st.warning('Add your name to start.')
            elif email and not valid_email(email):
                st.warning('Check that email, or leave it blank.')
            elif access and not hmac.compare_digest(code, access):
                st.error('That access code doesn’t match.')
            else:
                st.session_state.profile = {'name': name.strip(), 'email': email.strip()}
                st.rerun()
    with right:
        st.markdown('''<div class="receipt-card"><h3>THE EVENING, SORTED</h3><p style="justify-content:center">BEACH ROAD · TABLE 03</p><hr><p><span>Wraps & good conversation</span><span>280</span></p><p><span>One more sandwich</span><span>190</span></p><p><span>Coffee for the road</span><span>270</span></p><hr><p><span>Subtotal</span><span>740</span></p><p><span>Tax</span><span>37</span></p><p><b>TOTAL</b><b>₹777</b></p><hr><p style="justify-content:center">3 FRIENDS. ₹259 EACH.</p><p style="justify-content:center">No mental maths required.</p></div>''', unsafe_allow_html=True)
    st.caption('01  Add a receipt     /     02  Check & split     /     03  Send the recap')
    st.stop()

profile = st.session_state.profile
with st.sidebar:
    st.subheader('Your table')
    st.write(f"Started by {profile['name']}")
    st.caption('Receipts and conversations stay in this browser session. A refresh may clear them.')
    st.caption('Photos/text go to Google only when you analyse them. Email goes through Gmail only when you press Send. No payments are processed.')
    st.caption('INR receipts only · up to 12 people · one bill at a time')
    if st.button('Leave table / clear session'):
        st.session_state.clear()
        st.rerun()

st.header('The table, at a glance.')
st.caption('Read the receipt. Fix the small things. Leave with a fair split.')
with st.expander('01 / Add a receipt', expanded='receipt' not in st.session_state):
    input_col, sample_col = st.columns([2, 1])
    with input_col:
        photo = st.file_uploader('Receipt photo', type=['png', 'jpg', 'jpeg'])
        text = st.text_area('Or type the bill', placeholder='Two wraps ₹280, coffee ₹270, sandwich ₹190, tax ₹37. Total ₹777.', max_chars=6000)
        st.caption('Use a clear, cropped receipt. Remove card numbers or personal details first.')
        if st.button('Read my receipt', type='primary', disabled=not key):
            if not photo and not text.strip():
                st.warning('Add a photo or some bill details first.')
            elif time.time() - st.session_state.get('last_ai', 0) < 5:
                st.warning('Please wait a few seconds before trying again.')
            else:
                st.session_state.last_ai = time.time()
                try:
                    with st.spinner('Picking out the useful details…'):
                        receipt = extract_receipt(key, model, text, photo.getvalue() if photo else None)
                    if receipt['currency'].upper() not in ('INR', '₹', 'RS', 'RS.'):
                        st.warning('This version supports INR only. Please use an Indian rupee receipt.')
                    elif not receipt['items']:
                        st.warning('No readable items found. Try a clearer image or type the bill.')
                    else:
                        set_receipt(receipt)
                        st.rerun()
                except Exception:
                    st.error('Couldn’t read that receipt. Check the image, API key/model access and quota, then retry. Your existing bill is safe.')
    with sample_col:
        st.subheader('Just looking around?')
        st.write('Try a fictional evening at a Beach Road café. No API key needed.')
        if st.button('Load sample table →'):
            set_receipt(SAMPLE, True)
            st.rerun()
        if not key:
            st.info('Sample mode is ready. Add a Gemini key in app secrets to analyse your own receipts.')

if 'receipt' not in st.session_state:
    st.stop()
r = st.session_state.receipt
rev = st.session_state.revision
if st.session_state.demo:
    st.info('SAMPLE TABLE · This is fictional data, not an AI analysis of your upload.')
for note in r.get('notes', []):
    st.caption(note)

st.subheader('02 / Check & split')
st.caption('Amounts below are line totals. If the receipt says “2 coffees — ₹180”, enter ₹180, not ₹360.')
merchant = st.text_input('Place', r['merchant'], key=f'merchant{rev}', max_chars=120)
people_text = st.text_input('Who was there? · separate names with commas', f"{profile['name']}, Friend 1, Friend 2", key=f'people{rev}', max_chars=300)
people = [p.strip() for p in people_text.split(',') if p.strip()]
if not 1 <= len(people) <= 12 or len(set(people)) != len(people):
    st.warning('Use 1–12 different names, separated by commas.')
    st.stop()
rows = st.data_editor(r['items'], num_rows='dynamic', hide_index=True, width='stretch',
    column_config={'item': st.column_config.TextColumn('What was ordered', required=True, max_chars=120),
                   'amount': st.column_config.NumberColumn('Line total · ₹', min_value=0.0, max_value=10000000.0, step=0.01, required=True)}, key=f'items{rev}')
rows = [dict(row) for row in rows if row.get('item') and row.get('amount') is not None]
a, b, c = st.columns(3)
with a:
    adjustment = st.number_input('Tax + fees − discounts · ₹', value=float(r['adjustment']), step=0.01, key=f'adj{rev}')
with b:
    tip = st.number_input('Extra tip · ₹', min_value=0.0, value=0.0, step=10.0, key=f'tip{rev}')
with c:
    payer = st.selectbox('Who paid the full bill?', people)
mode = st.radio('Split style', ['Everyone equally', 'By what we ordered'], horizontal=True)
if mode == 'By what we ordered':
    st.caption('Select everyone who shared each line. Taxes, discounts and tip follow each person’s item share.')
    for i, row in enumerate(rows):
        row['owners'] = st.multiselect(f"{row['item']} · {money(cents(row['amount']))}", people, default=people,
            key=f'owners{rev}-{i}-{hashlib.sha256(people_text.encode()).hexdigest()[:8]}')
try:
    adj = cents(adjustment)
    tip_cents = cents(tip)
    shares = split_bill(rows, people, adj + tip_cents, mode == 'By what we ordered')
except (ValueError, TypeError):
    st.warning('Check item amounts and assignments. Every item needs a person, and the subtotal must be positive.')
    st.stop()
total = sum(shares.values())
x, y, z = st.columns(3)
x.metric('THE WHOLE TABLE', money(total))
y.metric('PEOPLE', len(people))
z.metric('YOUR SHARE', money(shares.get(profile['name'], 0)) if profile['name'] in shares else 'Not in split')
if r.get('printed_total') is not None:
    difference = total - tip_cents - cents(r['printed_total'])
    if difference:
        st.warning(f"Receipt check: your edited total before the extra tip differs from the printed total by {money(difference)}. Review the rows and adjustments.")
    else:
        st.success('Receipt check: items + adjustments match the printed total.')
st.dataframe([{'Person': p, 'Share': money(v), 'Transfer': 'Already paid' if p == payer else f'{money(v)} → {payer}'} for p, v in shares.items()], hide_index=True, width='stretch')
st.caption('Any leftover paise go in table order. Shares always add up exactly to the bill.')
body = summary_text(merchant, rows, adj + tip_cents, shares, payer)
digest = hashlib.sha256(body.encode()).hexdigest()
confirmed = st.checkbox('I checked the receipt, names and amounts.', key=f'confirmed-{digest}')

st.subheader('03 / Keep the recap')
with st.expander('Preview the exact message', expanded=True):
    st.code(body, language=None)
col1, col2 = st.columns(2)
with col1:
    st.download_button('Download recap .txt', body, file_name='aftertab-split.txt', mime='text/plain', disabled=not confirmed)
with col2:
    recipient = st.text_input('Email this recap to yourself', value=profile['email'], max_chars=160)
    sender, password = secret('GMAIL_ADDRESS'), secret('GMAIL_APP_PASSWORD')
    if not sender or not password:
        st.caption('Email needs Gmail sender credentials in app secrets. Download is available now.')
    if st.button('Send this recap to my email', disabled=not (confirmed and sender and password)):
        delivery_id = hashlib.sha256((recipient + body).encode()).hexdigest()
        if not valid_email(recipient):
            st.warning('Enter one valid email address.')
        elif delivery_id == st.session_state.get('last_delivery'):
            st.info('This exact recap was already accepted for sending in this session.')
        elif time.time() - st.session_state.get('last_send', 0) < 60:
            st.warning('Please wait a minute between email attempts.')
        else:
            st.session_state.last_send = time.time()
            try:
                with st.spinner('Sending your recap…'):
                    send_email(sender, password, recipient, body)
                st.session_state.last_delivery = delivery_id
                st.success('Gmail accepted your recap for delivery. Check your inbox or spam folder.')
            except Exception:
                st.error('Email could not be confirmed. Check your inbox before retrying, then verify the sender App Password. You can still download the recap.')

st.divider()
st.subheader('A question before you go?')
st.caption('Ask about the current bill or how a split works. Change amounts in the controls above.')
for message in st.session_state.get('history', []):
    with st.chat_message(message['role']):
        st.write(message['content'])
question = st.chat_input('“How are the taxes shared?”', disabled=not key, max_chars=2000)
if question:
    history = st.session_state.get('history', [])
    try:
        with st.spinner('Checking the table…'):
            answer = ask_receipt(key, model, body, history, question)
        st.session_state.history = (history + [{'role': 'user', 'content': question}, {'role': 'assistant', 'content': answer}])[-20:]
        st.rerun()
    except Exception:
        st.error('The assistant couldn’t reply. Check model access and quota, then try again. Your split is unchanged.')
if not key:
    st.caption('Connect Gemini to enable receipt questions. Sample calculations do not use AI.')
