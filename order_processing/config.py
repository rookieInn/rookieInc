"""Configuration models for the e-commerce order processing pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace, asdict
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(slots=True)
class ColumnMapping:
    """Canonical column names used by the pipeline."""

    order_id: str = "order_id"
    customer_id: str = "customer_id"
    order_datetime: str = "order_datetime"
    order_amount: str = "order_amount"
    currency: str = "currency"
    ip_address: str = "ip_address"
    phone_number: str = "phone_number"
    shipping_address: str = "shipping_address"
    tracking_number: str = "tracking_number"
    carrier: str = "carrier"
    sku_list: str = "sku_list"
    payment_method: str = "payment_method"
    order_status: str = "order_status"


@dataclass(slots=True)
class CleaningConfig:
    """Parameters for data cleaning and enrichment."""

    phone_default_region: str = "CN"
    phone_extension_column: Optional[str] = None
    phone_preserve_country_code: bool = True
    address_fields: tuple[str, ...] = ("shipping_address",)
    address_uppercase: bool = False
    address_whitespace_normalization: bool = True
    min_address_length: int = 10
    enable_tracking_imputation: bool = True
    tracking_match_keys: tuple[str, ...] = (
        "order_id",
        "customer_id",
        "shipping_address",
        "carrier",
    )
    tracking_max_reference_age_days: int = 30


@dataclass(slots=True)
class RuleThresholdConfig:
    """Thresholds for rule-based anomaly detection."""

    small_order_amount: float = 20.0
    high_frequency_orders_per_day: int = 8
    consecutive_small_order_minutes: int = 120
    ip_unique_account_threshold: int = 3
    ip_daily_order_threshold: int = 50
    high_value_order_threshold: float = 5000.0
    location_mismatch_confidence: float = 0.8
    ip_multi_account_confidence: float = 0.9
    high_frequency_confidence: float = 0.85


@dataclass(slots=True)
class IsolationForestConfig:
    """Parameters for the Isolation Forest anomaly model."""

    enabled: bool = True
    contamination: float = 0.01
    n_estimators: int = 300
    max_samples: str | int = "auto"
    max_features: float = 1.0
    random_state: int = 42
    bootstrap: bool = False


@dataclass(slots=True)
class AnomalyConfig:
    """Aggregated anomaly detection configuration."""

    rules: RuleThresholdConfig = field(default_factory=RuleThresholdConfig)
    isolation_forest: IsolationForestConfig = field(default_factory=IsolationForestConfig)
    rolling_window_days: int = 7
    minimum_orders_for_model: int = 200


@dataclass(slots=True)
class PipelineConfig:
    """Top-level configuration for the order processing pipeline."""

    columns: ColumnMapping = field(default_factory=ColumnMapping)
    cleaning: CleaningConfig = field(default_factory=CleaningConfig)
    anomaly: AnomalyConfig = field(default_factory=AnomalyConfig)
    chunk_size: int = 50_000
    timezone: str = "Asia/Shanghai"

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "PipelineConfig":
        """Construct a config object from a dict, performing deep merging."""

        def merge_dataclass(instance, updates: Dict[str, Any]):
            data = {}
            for key, value in updates.items():
                current = getattr(instance, key)
                if hasattr(current, "__dataclass_fields__") and isinstance(value, dict):
                    data[key] = merge_dataclass(current, value)
                else:
                    data[key] = value
            return replace(instance, **data)

        base = cls()
        merged = merge_dataclass(base, payload)
        return merged

    @classmethod
    def from_json_file(cls, path: str | Path) -> "PipelineConfig":
        """Load configuration from a JSON file."""

        with Path(path).expanduser().open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        return cls.from_dict(payload)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the config to a dictionary."""

        return asdict(self)

    def to_json(self, path: str | Path, *, indent: int = 2) -> None:
        """Persist the configuration to disk as JSON."""

        with Path(path).expanduser().open("w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=indent, ensure_ascii=False)


def load_config(path: Optional[str | Path]) -> PipelineConfig:
    """Helper that returns the default config or loads from disk if path provided."""

    if path is None:
        return PipelineConfig()
    return PipelineConfig.from_json_file(path)

