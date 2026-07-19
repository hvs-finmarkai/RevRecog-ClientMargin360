from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from datetime import date, datetime


class CurrencyError(Exception):
    pass


class UnsupportedCurrencyError(CurrencyError):
    pass


class ExchangeRateNotFoundError(CurrencyError):
    pass


@dataclass
class Currency:
    code: str
    name: str
    symbol: str
    decimal_places: int = 2


@dataclass
class ConvertedAmount:
    original_amount: Decimal
    converted_amount: Decimal
    from_currency: str
    to_currency: str
    exchange_rate: Decimal
    rate_date: date


SUPPORTED_CURRENCIES = {
    "INR": Currency(code="INR", name="Indian Rupee", symbol="\u20b9", decimal_places=2),
    "USD": Currency(code="USD", name="US Dollar", symbol="$", decimal_places=2),
    "EUR": Currency(code="EUR", name="Euro", symbol="\u20ac", decimal_places=2),
    "GBP": Currency(code="GBP", name="British Pound", symbol="\u00a3", decimal_places=2),
    "SGD": Currency(code="SGD", name="Singapore Dollar", symbol="S$", decimal_places=2),
    "AED": Currency(code="AED", name="UAE Dirham", symbol="\u062f.\u0625", decimal_places=2),
    "JPY": Currency(code="JPY", name="Japanese Yen", symbol="\u00a5", decimal_places=0),
}

DEFAULT_RATES_TO_INR = {
    "USD": Decimal("83.50"),
    "EUR": Decimal("91.20"),
    "GBP": Decimal("106.50"),
    "SGD": Decimal("62.30"),
    "AED": Decimal("22.73"),
    "JPY": Decimal("0.56"),
    "INR": Decimal("1.00"),
}


class CurrencyService:

    def __init__(self, rate_provider=None):
        self._rate_provider = rate_provider
        self._cache = {}

    def convert(self, amount: Decimal, from_currency: str, to_currency: str, date_val: Optional[date] = None) -> ConvertedAmount:
        if isinstance(amount, (int, float, str)):
            amount = Decimal(str(amount))

        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        self._validate_currency(from_currency)
        self._validate_currency(to_currency)

        if from_currency == to_currency:
            return ConvertedAmount(
                original_amount=amount,
                converted_amount=amount,
                from_currency=from_currency,
                to_currency=to_currency,
                exchange_rate=Decimal("1.00"),
                rate_date=date_val or date.today()
            )

        rate = self.get_exchange_rate(from_currency, to_currency, date_val)
        converted = (amount * rate).quantize(
            Decimal("0.01") if SUPPORTED_CURRENCIES[to_currency].decimal_places == 2 else Decimal("1"),
            rounding=ROUND_HALF_UP
        )

        return ConvertedAmount(
            original_amount=amount,
            converted_amount=converted,
            from_currency=from_currency,
            to_currency=to_currency,
            exchange_rate=rate,
            rate_date=date_val or date.today()
        )

    def get_exchange_rate(self, from_currency: str, to_currency: str, date_val: Optional[date] = None) -> Decimal:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        self._validate_currency(from_currency)
        self._validate_currency(to_currency)

        if from_currency == to_currency:
            return Decimal("1.00")

        rate_date = date_val or date.today()

        if self._rate_provider:
            try:
                rate = self._rate_provider.get_rate(from_currency, to_currency, rate_date)
                if rate:
                    return rate
            except Exception:
                pass

        cached_rate = self._get_cached_rate(from_currency, to_currency, rate_date)
        if cached_rate:
            return cached_rate

        rate = self._get_static_rate(from_currency, to_currency)
        self._cache_rate(from_currency, to_currency, rate_date, rate)
        return rate

    def get_supported_currencies(self) -> list:
        return list(SUPPORTED_CURRENCIES.values())

    def format_amount(self, amount: Decimal, currency: str) -> str:
        if isinstance(amount, (int, float, str)):
            amount = Decimal(str(amount))

        currency = currency.upper()
        self._validate_currency(currency)

        curr = SUPPORTED_CURRENCIES[currency]

        if curr.decimal_places == 0:
            formatted_number = f"{int(amount):,}"
        else:
            quantized = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            formatted_number = f"{quantized:,.2f}"

        if currency == "INR":
            formatted_number = self._format_indian_number(amount, curr.decimal_places)

        return f"{curr.symbol}{formatted_number}"

    def _validate_currency(self, currency_code: str):
        if currency_code not in SUPPORTED_CURRENCIES:
            raise UnsupportedCurrencyError(
                f"Currency '{currency_code}' is not supported. Supported: {list(SUPPORTED_CURRENCIES.keys())}"
            )

    def _get_static_rate(self, from_currency: str, to_currency: str) -> Decimal:
        if from_currency == "INR":
            to_inr_rate = DEFAULT_RATES_TO_INR.get(to_currency)
            if to_inr_rate and to_inr_rate != Decimal("0"):
                return (Decimal("1") / to_inr_rate).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
            raise ExchangeRateNotFoundError(f"No rate found for INR to {to_currency}")

        if to_currency == "INR":
            rate = DEFAULT_RATES_TO_INR.get(from_currency)
            if rate:
                return rate
            raise ExchangeRateNotFoundError(f"No rate found for {from_currency} to INR")

        from_to_inr = DEFAULT_RATES_TO_INR.get(from_currency)
        to_to_inr = DEFAULT_RATES_TO_INR.get(to_currency)

        if from_to_inr and to_to_inr and to_to_inr != Decimal("0"):
            return (from_to_inr / to_to_inr).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

        raise ExchangeRateNotFoundError(f"No rate found for {from_currency} to {to_currency}")

    def _get_cached_rate(self, from_currency: str, to_currency: str, rate_date: date) -> Optional[Decimal]:
        key = f"{from_currency}_{to_currency}_{rate_date.isoformat()}"
        return self._cache.get(key)

    def _cache_rate(self, from_currency: str, to_currency: str, rate_date: date, rate: Decimal):
        key = f"{from_currency}_{to_currency}_{rate_date.isoformat()}"
        self._cache[key] = rate

    def _format_indian_number(self, amount: Decimal, decimal_places: int) -> str:
        if decimal_places == 0:
            integer_part = str(int(amount))
            decimal_part = ""
        else:
            quantized = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            parts = str(quantized).split(".")
            integer_part = parts[0]
            decimal_part = f".{parts[1]}" if len(parts) > 1 else ".00"

        is_negative = integer_part.startswith("-")
        if is_negative:
            integer_part = integer_part[1:]

        if len(integer_part) <= 3:
            formatted = integer_part
        else:
            last_three = integer_part[-3:]
            remaining = integer_part[:-3]
            groups = []
            while remaining:
                groups.insert(0, remaining[-2:])
                remaining = remaining[:-2]
            formatted = ",".join(groups) + "," + last_three

        result = formatted + decimal_part
        if is_negative:
            result = "-" + result
        return result
