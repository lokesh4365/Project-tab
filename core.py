"""Receipt validation and exact money arithmetic. No network or UI dependencies."""
from decimal import Decimal, ROUND_HALF_UP
import re


def cents(value):
    try:
        value = Decimal(str(value))
        if not value.is_finite() or abs(value) > 10_000_000:
            raise ValueError()
        return int((value * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    except Exception as exc:
        raise ValueError('Enter a finite amount under 10 million.') from exc


def money(value):
    return f'₹{value / 100:,.2f}'


def valid_email(value):
    return bool(re.fullmatch(r'[^\s@,;\r\n]+@[^\s@,;\r\n]+\.[^\s@,;\r\n]+', value))


def allocate(total, weights):
    """Largest-remainder apportionment; output always sums to input paise."""
    if total < 0 or not weights or any(w < 0 for w in weights) or sum(weights) <= 0:
        raise ValueError('A non-negative total and positive combined weight are required.')
    denominator = sum(weights)
    amounts = [total * w // denominator for w in weights]
    order = sorted(range(len(weights)), key=lambda i: (-(total * weights[i] % denominator), i))
    for i in order[:total - sum(amounts)]:
        amounts[i] += 1
    return amounts


def split_bill(rows, people, adjustment=0, by_item=False):
    if not people or len(set(people)) != len(people):
        raise ValueError('Add unique names for everyone at the table.')
    amounts = [0] * len(people)
    for row in rows:
        amount = cents(row['amount'])
        if amount < 0:
            raise ValueError('Item totals cannot be negative. Use the adjustment for discounts.')
        owners = row.get('owners', people) if by_item else people
        if not owners or any(p not in people for p in owners) or len(set(owners)) != len(owners):
            raise ValueError(f"Choose valid people for {row['item']}.")
        for person, share in zip(owners, allocate(amount, [1] * len(owners))):
            amounts[people.index(person)] += share
    base = sum(amounts)
    total = base + adjustment
    if total < 0 or base <= 0:
        raise ValueError('The item subtotal must be positive and the final total cannot be negative.')
    # Scale each person's consumption share so discounts never produce negative dues.
    return dict(zip(people, allocate(total, amounts if by_item else [1] * len(people))))


def summary_text(merchant, rows, adjustment, shares, payer):
    total = sum(shares.values())
    lines = ['AFTERTAB / THE TABLE IS SETTLED', merchant, '', 'Receipt']
    for row in rows:
        lines.append(f"• {row['item']}: {money(cents(row['amount']))}")
    lines += [f'Adjustments: {money(adjustment)}', f'Total: {money(total)}', '', 'Each person’s share']
    lines += [f'{p}: {money(v)}' for p, v in shares.items()]
    lines += ['', f'{payer} paid the bill.']
    lines += [f'{p} → {payer}: {money(v)}' for p, v in shares.items() if p != payer and v]
    lines += ['', 'Checked and confirmed in AfterTab. No payment has been made by this app.']
    return '\n'.join(lines)
