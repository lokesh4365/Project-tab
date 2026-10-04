"""Small, replaceable boundaries for Gemini and SMTP."""
import json
import smtplib
import ssl
from email.message import EmailMessage
from io import BytesIO
from PIL import Image, ImageOps
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from prompts import EXTRACT_PROMPT, CHAT_PROMPT
from core import valid_email


class ReceiptItem(BaseModel):
    item: str = Field(max_length=120)
    amount: float = Field(ge=0, le=10_000_000)


class Receipt(BaseModel):
    merchant: str = Field(max_length=120)
    currency: str
    items: list[ReceiptItem] = Field(max_length=100)
    adjustment: float
    printed_total: float | None
    notes: list[str]


def image_bytes(raw):
    if len(raw) > 8 * 1024 * 1024:
        raise ValueError('Please upload an image smaller than 8 MB.')
    with Image.open(BytesIO(raw)) as source:
        if source.width * source.height > 25_000_000:
            raise ValueError('Please use a photo under 25 megapixels.')
        picture = ImageOps.exif_transpose(source).convert('RGB')
        picture.thumbnail((1800, 1800))
        output = BytesIO()
        picture.save(output, format='JPEG', quality=88)
        return output.getvalue()  # Re-encoding also strips location/EXIF metadata.


def extract_receipt(key, model, text='', photo=None):
    parts = [text[:6000] or 'Read this receipt.']
    if photo:
        parts.append(types.Part.from_bytes(data=image_bytes(photo), mime_type='image/jpeg'))
    with genai.Client(api_key=key, http_options=types.HttpOptions(timeout=45000)) as client:
        response = client.models.generate_content(model=model, contents=parts,
            config=types.GenerateContentConfig(system_instruction=EXTRACT_PROMPT,
                response_mime_type='application/json', response_schema=Receipt, temperature=0))
    if not response.text:
        raise ValueError('No readable receipt returned. Try a clearer photo.')
    return Receipt.model_validate_json(response.text).model_dump()


def ask_receipt(key, model, context, history, question):
    contents = []
    for message in history[-12:]:
        contents.append(types.Content(role='model' if message['role'] == 'assistant' else 'user',
            parts=[types.Part.from_text(text=message['content'])]))
    contents.append(types.Content(role='user', parts=[types.Part.from_text(text=question[:2000])]))
    with genai.Client(api_key=key, http_options=types.HttpOptions(timeout=45000)) as client:
        response = client.models.generate_content(model=model, contents=contents,
            config=types.GenerateContentConfig(system_instruction=CHAT_PROMPT + '\nCurrent confirmed data:\n' + context,
                temperature=0.3, max_output_tokens=700))
    if not response.text:
        raise ValueError('Empty response. Please try again.')
    return response.text


def send_email(sender, password, recipient, body):
    if not valid_email(recipient) or not valid_email(sender):
        raise ValueError('Enter one valid email address.')
    message = EmailMessage()
    message['Subject'] = 'Your AfterTab bill split'
    message['From'] = sender
    message['To'] = recipient
    message.set_content(body)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ssl.create_default_context(), timeout=20) as server:
        server.login(sender, password)
        refused = server.send_message(message)
        if refused:
            raise ValueError('The email provider did not accept this recipient.')
