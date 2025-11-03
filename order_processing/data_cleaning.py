"""Data cleaning utilities for the e-commerce order processing pipeline."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException, PhoneNumberFormat

from .config import CleaningConfig, ColumnMapping


@dataclass(slots=True)
class CleaningResult:
    """Return object for the cleaning stage."""

    data: pd.DataFrame
    stats: Dict[str, int]
    tracking_imputations: Optional[pd.DataFrame]


def _normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


class TrackingNumberImputer:
    """Fill missing tracking numbers using historical order data."""

    def __init__(
        self,
        historical_orders: pd.DataFrame,
        *,
        config: CleaningConfig,
        columns: ColumnMapping,
    ) -> None:
        self.historical_orders = historical_orders.copy() if historical_orders is not None else None
        self.config = config
        self.columns = columns
        self._prepare()

    def _prepare(self) -> None:
        if self.historical_orders is None or self.historical_orders.empty:
            self.by_order: Dict[str, str] = {}
            self.by_customer_carrier: Dict[Tuple[str, str], str] = {}
            self.by_address_carrier: Dict[Tuple[str, str], str] = {}
            return

        orders = self.historical_orders
        track_col = self.columns.tracking_number
        order_id_col = self.columns.order_id
        customer_col = self.columns.customer_id
        carrier_col = self.columns.carrier
        address_col = self.columns.shipping_address

        orders = orders.copy()
        if track_col in orders:
            valid_mask = orders[track_col].notna() & (orders[track_col].astype(str).str.strip() != "")
            orders = orders[valid_mask]

        # Ensure string type for keys to avoid mismatches.
        for col in (order_id_col, customer_col, carrier_col, address_col, track_col):
            if col in orders:
                orders[col] = orders[col].astype(str, errors="ignore")

        # Recent orders are more reliable for imputation.
        timestamp_col = self.columns.order_datetime
        if timestamp_col in orders:
            orders[timestamp_col] = pd.to_datetime(orders[timestamp_col], errors="coerce")
            max_age = timedelta(days=self.config.tracking_max_reference_age_days)
            cutoff = pd.Timestamp(datetime.now()) - max_age
            orders = orders[(orders[timestamp_col].isna()) | (orders[timestamp_col] >= cutoff)]

        self.by_order = (
            orders.set_index(order_id_col)[track_col].to_dict()
            if order_id_col in orders and not orders.empty
            else {}
        )

        if customer_col in orders and carrier_col in orders:
            self.by_customer_carrier = (
                orders.sort_values(timestamp_col if timestamp_col in orders else order_id_col)
                .dropna(subset=[customer_col, carrier_col])
                .drop_duplicates(subset=[customer_col, carrier_col], keep="last")
                .set_index([customer_col, carrier_col])[track_col]
                .to_dict()
            )
        else:
            self.by_customer_carrier = {}

        if address_col in orders and carrier_col in orders:
            self.by_address_carrier = (
                orders.dropna(subset=[address_col, carrier_col])
                .drop_duplicates(subset=[address_col, carrier_col], keep="last")
                .set_index([address_col, carrier_col])[track_col]
                .to_dict()
            )
        else:
            self.by_address_carrier = {}

    def impute(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        if not self.config.enable_tracking_imputation or not (
            self.by_order or self.by_customer_carrier or self.by_address_carrier
        ):
            if self.columns.tracking_number in data.columns:
                data[self.columns.tracking_number] = data[self.columns.tracking_number].replace({"": np.nan})
            return data, pd.DataFrame(columns=["order_id", "tracking_number", "source"])

        df = data.copy()
        track_col = self.columns.tracking_number
        df[track_col] = df[track_col].replace({"": np.nan})

        records: List[Dict[str, str]] = []

        for idx, row in df[df[track_col].isna()].iterrows():
            tracking_number, source = self._lookup_tracking(row)
            if tracking_number is not None:
                df.at[idx, track_col] = tracking_number
                records.append(
                    {
                        "order_id": str(row.get(self.columns.order_id, idx)),
                        "tracking_number": tracking_number,
                        "source": source,
                        "row_index": idx,
                        "confidence": self._confidence_from_source(source),
                    }
                )

        imputation_log = pd.DataFrame.from_records(
            records,
            columns=["order_id", "tracking_number", "source", "row_index", "confidence"],
        )
        if not imputation_log.empty:
            source_column = f"{track_col}_imputation_source"
            if source_column not in df.columns:
                df[source_column] = np.nan
            df.loc[imputation_log["row_index"].tolist(), source_column] = imputation_log["source"].values
        return df, imputation_log

    def _lookup_tracking(self, row: pd.Series) -> Tuple[Optional[str], Optional[str]]:
        order_id = row.get(self.columns.order_id)
        if pd.notna(order_id):
            order_id = str(order_id)
            if order_id in self.by_order:
                return self.by_order[order_id], "order_id_match"

        customer_id = row.get(self.columns.customer_id)
        carrier = row.get(self.columns.carrier)
        if pd.notna(customer_id) and pd.notna(carrier):
            key = (str(customer_id), str(carrier))
            if key in self.by_customer_carrier:
                return self.by_customer_carrier[key], "customer_carrier_match"

        address = row.get(self.columns.shipping_address)
        if pd.notna(address) and pd.notna(carrier):
            key = (str(address), str(carrier))
            if key in self.by_address_carrier:
                return self.by_address_carrier[key], "address_carrier_match"

        return None, None

    @staticmethod
    def _confidence_from_source(source: Optional[str]) -> float:
        mapping = {
            "order_id_match": 0.99,
            "customer_carrier_match": 0.85,
            "address_carrier_match": 0.75,
        }
        if source is None:
            return 0.0
        return mapping.get(source, 0.5)


class OrderDataCleaner:
    """Perform data cleaning and enrichment for raw order data."""

    def __init__(self, config: CleaningConfig, columns: ColumnMapping) -> None:
        self.config = config
        self.columns = columns

    def clean(
        self,
        data: pd.DataFrame,
        *,
        historical_orders: Optional[pd.DataFrame] = None,
    ) -> CleaningResult:
        df = data.copy()

        phone_stats = self._normalize_phone_numbers(df)
        address_stats = self._normalize_addresses(df)

        tracking_log = None
        if self.config.enable_tracking_imputation and historical_orders is not None:
            imputer = TrackingNumberImputer(
                historical_orders,
                config=self.config,
                columns=self.columns,
            )
            df, tracking_log = imputer.impute(df)
            if tracking_log is not None and not tracking_log.empty:
                flag_column = f"{self.columns.tracking_number}_imputed"
                if flag_column not in df.columns:
                    df[flag_column] = False
                imputed_indices = tracking_log["row_index"].tolist()
                df.loc[imputed_indices, flag_column] = True
                tracking_log = tracking_log.drop(columns=["row_index"], errors="ignore")

        stats = {
            "phone_valid": phone_stats.get("valid", 0),
            "phone_corrected": phone_stats.get("corrected", 0),
            "phone_invalid": phone_stats.get("invalid", 0),
            "addresses_normalized": address_stats.get("normalized", 0),
            "addresses_flagged_short": address_stats.get("too_short", 0),
            "tracking_imputed": 0 if tracking_log is None else len(tracking_log),
        }

        return CleaningResult(data=df, stats=stats, tracking_imputations=tracking_log)

    def _normalize_phone_numbers(self, df: pd.DataFrame) -> Dict[str, int]:
        column = self.columns.phone_number
        if column not in df.columns:
            return {}

        default_region = self.config.phone_default_region
        extension_column = self.config.phone_extension_column
        stats = {"valid": 0, "corrected": 0, "invalid": 0}

        normalized_values: List[Optional[str]] = []
        statuses: List[str] = []

        if f"{column}_raw" not in df.columns:
            df[f"{column}_raw"] = df[column]

        for idx, value in df[column].items():
            extension = None
            if extension_column and extension_column in df.columns:
                extension = df.at[idx, extension_column]

            normalized, status = self._normalize_phone_value(value, default_region, extension)
            normalized_values.append(normalized)
            statuses.append(status)
            stats[status] = stats.get(status, 0) + 1

        df[column] = normalized_values
        df[f"{column}_validation_status"] = statuses
        return stats

    def _normalize_phone_value(
        self,
        value: object,
        default_region: str,
        extension: Optional[object] = None,
    ) -> Tuple[Optional[str], str]:
        if pd.isna(value):
            return None, "invalid"

        raw = str(value).strip()
        if not raw:
            return None, "invalid"

        # Remove non-digit characters except leading +
        if raw.startswith("+"):
            cleaned = "+" + re.sub(r"[^0-9]", "", raw[1:])
        else:
            cleaned = re.sub(r"[^0-9]", "", raw)

        if not cleaned:
            return None, "invalid"

        try:
            parsed = phonenumbers.parse(cleaned, default_region)
        except NumberParseException:
            try:
                parsed = phonenumbers.parse(cleaned, None)
            except NumberParseException:
                return None, "invalid"

        if not phonenumbers.is_valid_number(parsed):
            return None, "invalid"

        formatted = phonenumbers.format_number(parsed, PhoneNumberFormat.E164)

        if extension:
            formatted = f"{formatted} x{extension}" if extension else formatted

        if formatted == raw:
            return formatted, "valid"
        return formatted, "corrected"

    def _normalize_addresses(self, df: pd.DataFrame) -> Dict[str, int]:
        stats = {"normalized": 0, "too_short": 0}
        for field in self.config.address_fields:
            if field not in df.columns:
                continue

            normalized_values: List[Optional[str]] = []
            statuses: List[str] = []

            raw_column = f"{field}_raw"
            if raw_column not in df.columns:
                df[raw_column] = df[field]

            for value in df[field].fillna(""):
                normalized, status = self._normalize_address_value(value)
                normalized_values.append(normalized)
                statuses.append(status)
                stats[status] = stats.get(status, 0) + 1

            df[field] = normalized_values
            df[f"{field}_cleaning_status"] = statuses

        return stats

    def _normalize_address_value(self, value: object) -> Tuple[Optional[str], str]:
        if pd.isna(value):
            return None, "too_short"

        text = str(value).strip()
        if not text:
            return None, "too_short"

        if self.config.address_whitespace_normalization:
            text = _normalize_whitespace(text)

        punctuation_map = {
            "\uFF0C": ",",  # full-width comma
            "\u3002": ".",  # ideographic full stop
            "\uFF1B": ";",  # full-width semicolon
            "\uFF1A": ":",  # full-width colon
        }
        for source, target in punctuation_map.items():
            text = text.replace(source, target)

        if self.config.address_uppercase:
            text = text.upper()

        status = "normalized"
        if len(text) < self.config.min_address_length:
            status = "too_short"

        return text, status

