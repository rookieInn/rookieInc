"""Unit tests for the order processing pipeline."""

from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

from order_processing import OrderProcessingPipeline, PipelineConfig
from order_processing.anomaly_detection import OrderAnomalyDetector
from order_processing.data_cleaning import OrderDataCleaner


def _sample_raw_orders() -> pd.DataFrame:
    rows = []
    # Customer C1 - three small orders to trigger frequency rule
    for i in range(3):
        hour = f"{8 + i:02d}"
        rows.append(
            {
                "order_id": f"C1-O{i}",
                "customer_id": "C1",
                "order_datetime": f"2025-11-02 {hour}:00:00",
                "order_amount": 18.0,
                "currency": "CNY",
                "ip_address": "9.9.9.9",
                "phone_number": "01012345678",
                "shipping_address": "上海市浦东新区张江高科技园区",
                "tracking_number": "",
                "carrier": "SF",
                "sku_list": "SKU-1",
                "payment_method": "wechat",
                "order_status": "paid",
            }
        )

    # Customer C2 shares IP 9.9.9.9 to trigger multi-account rule
    rows.append(
        {
            "order_id": "C2-O1",
            "customer_id": "C2",
            "order_datetime": "2025-11-02 11:00:00",
            "order_amount": 320.0,
            "currency": "CNY",
            "ip_address": "9.9.9.9",
            "phone_number": "02198765432",
            "shipping_address": "上海市杨浦区",
            "tracking_number": "",
            "carrier": "SF",
            "sku_list": "SKU-2",
            "payment_method": "alipay",
            "order_status": "paid",
        }
    )

    # Customer C3 with matching tracking number already provided
    rows.append(
        {
            "order_id": "C3-O1",
            "customer_id": "C3",
            "order_datetime": "2025-11-02 12:30:00",
            "order_amount": 880.0,
            "currency": "CNY",
            "ip_address": "5.5.5.5",
            "phone_number": "+8613812345678",
            "shipping_address": "北京市海淀区",
            "tracking_number": "YT123",
            "carrier": "YTO",
            "sku_list": "SKU-3",
            "payment_method": "alipay",
            "order_status": "shipped",
        }
    )

    return pd.DataFrame(rows)


def _historical_orders() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "order_id": "HIST-1",
                "customer_id": "C1",
                "order_datetime": "2025-10-31 10:00:00",
                "order_amount": 35.0,
                "currency": "CNY",
                "ip_address": "1.1.1.1",
                "phone_number": "01087654321",
                "shipping_address": "上海市浦东新区张江高科技园区",
                "tracking_number": "SF-TRACK-001",
                "carrier": "SF",
            },
            {
                "order_id": "HIST-2",
                "customer_id": "C2",
                "order_datetime": "2025-10-30 09:00:00",
                "order_amount": 120.0,
                "currency": "CNY",
                "ip_address": "2.2.2.2",
                "phone_number": "02199887766",
                "shipping_address": "上海市杨浦区",
                "tracking_number": "SF-TRACK-002",
                "carrier": "SF",
            },
        ]
    )


def _patched_resolvers():
    phone_stub = SimpleNamespace(
        resolve=lambda value: "北京" if "010" in str(value) else "上海"
    )
    address_stub = SimpleNamespace(
        resolve=lambda value: "上海" if "上海" in str(value) else "北京"
    )
    return phone_stub, address_stub


def test_data_cleaning_normalizes_and_imputes_tracking():
    config = PipelineConfig()
    cleaner = OrderDataCleaner(config.cleaning, config.columns)

    raw_df = _sample_raw_orders()
    historical_df = _historical_orders()

    result = cleaner.clean(raw_df, historical_orders=historical_df)

    # Phone normalization
    assert result.data.loc[0, "phone_number"].startswith("+86")
    assert result.data.loc[0, "phone_number_validation_status"] in {"valid", "corrected"}

    # Tracking number imputation for C1 order
    imputed_order = result.data.loc[result.data["order_id"] == "C1-O0"].iloc[0]
    assert imputed_order["tracking_number"] == "SF-TRACK-001"
    assert imputed_order.get("tracking_number_imputation_source") == "customer_carrier_match"

    # Original raw value preserved
    assert "phone_number_raw" in result.data.columns
    assert result.tracking_imputations is not None
    assert not result.tracking_imputations.empty


def test_anomaly_detector_rules_trigger():
    config = PipelineConfig()
    config.anomaly.rules.small_order_amount = 20.0
    config.anomaly.rules.high_frequency_orders_per_day = 3
    config.anomaly.rules.consecutive_small_order_minutes = 90
    config.anomaly.rules.ip_unique_account_threshold = 2
    config.anomaly.rules.ip_daily_order_threshold = 2

    detector = OrderAnomalyDetector(config.anomaly, config.columns)
    phone_stub, address_stub = _patched_resolvers()
    detector.phone_resolver = phone_stub
    detector.address_resolver = address_stub

    cleaned_df = _sample_raw_orders()

    result = detector.detect(cleaned_df)
    anomaly_types = set(result.anomalies["anomaly_type"].unique())

    assert "high_frequency_small_orders" in anomaly_types
    assert "ip_multi_account" in anomaly_types
    assert "location_mismatch" in anomaly_types


def test_pipeline_run_creates_outputs(tmp_path):
    config = PipelineConfig()
    config.anomaly.rules.small_order_amount = 20.0
    config.anomaly.rules.high_frequency_orders_per_day = 3
    config.anomaly.rules.consecutive_small_order_minutes = 90
    config.anomaly.rules.ip_unique_account_threshold = 2
    config.anomaly.rules.ip_daily_order_threshold = 2
    # Lower model minimum to allow AI detection on tiny dataset during tests
    config.anomaly.minimum_orders_for_model = 5

    pipeline = OrderProcessingPipeline(config)
    phone_stub, address_stub = _patched_resolvers()
    pipeline.detector.phone_resolver = phone_stub
    pipeline.detector.address_resolver = address_stub

    raw_df = _sample_raw_orders()
    hist_df = _historical_orders()

    raw_path = tmp_path / "raw.csv"
    hist_path = tmp_path / "hist.csv"
    clean_path = tmp_path / "cleaned.csv"
    anomaly_path = tmp_path / "anomalies.csv"

    raw_df.to_csv(raw_path, index=False)
    hist_df.to_csv(hist_path, index=False)

    result = pipeline.run_to_files(
        raw_orders_path=raw_path,
        cleaned_output_path=clean_path,
        anomaly_report_path=anomaly_path,
        historical_orders_path=hist_path,
    )

    assert clean_path.exists()
    assert anomaly_path.exists()
    assert result.cleaning_stats["tracking_imputed"] >= 1
    assert not result.anomalies.empty

    cleaned_output = pd.read_csv(clean_path)
    anomaly_output = pd.read_csv(anomaly_path)

    assert "phone_number_validation_status" in cleaned_output.columns
    assert "tracking_number" in cleaned_output.columns
    assert not anomaly_output.empty
    assert {"order_id", "anomaly_type", "confidence", "suggestion"}.issubset(
        anomaly_output.columns
    )

