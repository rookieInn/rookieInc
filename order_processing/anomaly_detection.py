"""Anomaly detection logic for cleaned ecommerce order datasets."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import phonenumbers
from phonenumbers import geocoder
from sklearn.ensemble import IsolationForest

from .config import AnomalyConfig, ColumnMapping


@dataclass(slots=True)
class AnomalyDetectionResult:
    """Container for anomaly detection outputs."""

    anomalies: pd.DataFrame
    features: pd.DataFrame
    model_scores: Optional[pd.Series]


class PhoneRegionResolver:
    """Resolve region information from phone numbers, with caching."""

    def __init__(self, default_region: str = "CN", locale: str = "zh-cn") -> None:
        self.default_region = default_region
        self.locale = locale
        self._cache: Dict[str, Optional[str]] = {}

    def resolve(self, phone_number: object) -> Optional[str]:
        if phone_number is None:
            return None
        if isinstance(phone_number, float) and np.isnan(phone_number):
            return None

        key = str(phone_number).strip()
        if not key or key.lower() in {"nan", "none"}:
            return None
        if key in self._cache:
            return self._cache[key]

        try:
            parsed = phonenumbers.parse(key, self.default_region)
        except phonenumbers.NumberParseException:
            try:
                parsed = phonenumbers.parse(key, None)
            except phonenumbers.NumberParseException:
                self._cache[key] = None
                return None

        if not phonenumbers.is_valid_number(parsed):
            self._cache[key] = None
            return None

        description = geocoder.description_for_number(parsed, self.locale)
        if not description:
            description = geocoder.country_name_for_number(parsed, self.locale)

        normalized = normalize_region_name(description) if description else None
        self._cache[key] = normalized
        return normalized


PROVINCE_KEYWORDS = [
    "北京",
    "上海",
    "天津",
    "重庆",
    "河北",
    "山西",
    "辽宁",
    "吉林",
    "黑龙江",
    "江苏",
    "浙江",
    "安徽",
    "福建",
    "江西",
    "山东",
    "河南",
    "湖北",
    "湖南",
    "广东",
    "广西",
    "海南",
    "四川",
    "贵州",
    "云南",
    "西藏",
    "陕西",
    "甘肃",
    "青海",
    "宁夏",
    "新疆",
    "香港",
    "澳门",
    "台湾",
]


class AddressRegionResolver:
    """Extract Chinese province/city information from address strings."""

    def __init__(self) -> None:
        self.patterns = [re.compile(keyword) for keyword in PROVINCE_KEYWORDS]

    def resolve(self, address: object) -> Optional[str]:
        if address is None:
            return None

        text = str(address)
        if not text.strip():
            return None
        lowered = text.lower()
        if lowered in {"nan", "none"}:
            return None

        for keyword, pattern in zip(PROVINCE_KEYWORDS, self.patterns):
            if pattern.search(text):
                return normalize_region_name(keyword)
        return None


def normalize_region_name(name: Optional[str]) -> Optional[str]:
    if name is None:
        return None
    text = str(name)
    if not text:
        return None
    text = text.replace("自治区", "").replace("壮族", "").replace("回族", "").replace("维吾尔", "")
    text = text.replace("省", "").replace("市", "").replace("特别行政区", "")
    text = text.replace("地区", "")
    return text.strip()


class OrderAnomalyDetector:
    """Detect anomalous orders using heuristic rules and tree-based models."""

    def __init__(self, config: AnomalyConfig, columns: ColumnMapping) -> None:
        self.config = config
        self.columns = columns
        self.phone_resolver = PhoneRegionResolver()
        self.address_resolver = AddressRegionResolver()

    def detect(self, data: pd.DataFrame) -> AnomalyDetectionResult:
        df = data.copy()
        order_id_col = self.columns.order_id
        datetime_col = self.columns.order_datetime
        amount_col = self.columns.order_amount
        ip_col = self.columns.ip_address
        phone_col = self.columns.phone_number
        address_col = self.columns.shipping_address

        if datetime_col in df:
            df[datetime_col] = pd.to_datetime(df[datetime_col], errors="coerce")
        else:
            df[datetime_col] = pd.NaT

        if amount_col in df:
            df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")
        else:
            df[amount_col] = np.nan

        records: List[Dict[str, object]] = []

        self._detect_high_frequency_small_orders(df, records)
        self._detect_ip_multi_account(df, records)
        self._detect_location_mismatch(df, records)

        features, model_scores, model_records = self._run_isolation_forest(df)
        if model_records:
            records.extend(model_records)

        anomalies_df = pd.DataFrame.from_records(records)
        if not anomalies_df.empty:
            anomalies_df = anomalies_df.sort_values(by=["confidence", order_id_col], ascending=[False, True])

        return AnomalyDetectionResult(
            anomalies=anomalies_df,
            features=features,
            model_scores=model_scores,
        )

    def _detect_high_frequency_small_orders(self, df: pd.DataFrame, records: List[Dict[str, object]]) -> None:
        amount_col = self.columns.order_amount
        datetime_col = self.columns.order_datetime
        customer_col = self.columns.customer_id
        order_id_col = self.columns.order_id
        rules = self.config.rules

        if amount_col not in df or customer_col not in df or datetime_col not in df:
            return

        small_amount_mask = df[amount_col] <= rules.small_order_amount
        df_small = df[small_amount_mask & df[datetime_col].notna()].copy()
        if df_small.empty:
            return

        df_small["order_date"] = df_small[datetime_col].dt.date
        daily_counts = (
            df_small.groupby([customer_col, "order_date"])[order_id_col]
            .transform("count")
            .rename("daily_small_order_count")
        )
        df_small = df_small.assign(daily_small_order_count=daily_counts.values)

        high_frequency_mask = df_small["daily_small_order_count"] >= rules.high_frequency_orders_per_day
        if high_frequency_mask.any():
            for _, row in df_small[high_frequency_mask].iterrows():
                details = (
                    f"客户 {row[customer_col]} 在 {row['order_date']} 内产生"
                    f" {int(row['daily_small_order_count'])} 笔小额订单"
                )
                records.append(
                    {
                        order_id_col: row[order_id_col],
                        "anomaly_type": "high_frequency_small_orders",
                        "confidence": self.config.rules.high_frequency_confidence,
                        "score": float(row["daily_small_order_count"]),
                        "details": details,
                        "suggestion": "建议人工核查该账号的下单行为，并确认支付方式。",
                    }
                )

        # Rolling window for consecutive small orders within specified minutes
        window_minutes = rules.consecutive_small_order_minutes
        if window_minutes <= 0:
            return

        df_sorted = df_small.sort_values(datetime_col)

        def rolling_counts(group: pd.DataFrame) -> pd.Series:
            if group.empty:
                return pd.Series(dtype=float, index=group.index)
            times = group[datetime_col].values
            counts = np.ones(len(group), dtype=int)
            start = 0
            for i in range(len(group)):
                while times[i] - times[start] > np.timedelta64(window_minutes, "m"):
                    start += 1
                counts[i] = i - start + 1
            return pd.Series(counts, index=group.index)

        rolling = df_sorted.groupby(customer_col, dropna=False).apply(rolling_counts)
        if isinstance(rolling.index, pd.MultiIndex):
            rolling.index = rolling.index.get_level_values(-1)
        df_small = df_small.join(rolling.rename("window_small_order_count"), how="left")
        intense_mask = df_small["window_small_order_count"] >= rules.high_frequency_orders_per_day
        if intense_mask.any():
            for _, row in df_small[intense_mask].iterrows():
                details = (
                    f"客户 {row[customer_col]} 在 {window_minutes} 分钟内连续产生"
                    f" {int(row['window_small_order_count'])} 笔小额订单"
                )
                records.append(
                    {
                        order_id_col: row[order_id_col],
                        "anomaly_type": "burst_small_orders",
                        "confidence": min(0.99, self.config.rules.high_frequency_confidence + 0.05),
                        "score": float(row["window_small_order_count"]),
                        "details": details,
                        "suggestion": "建议限制该账号下单频率或触发验证码验证。",
                    }
                )

    def _detect_ip_multi_account(self, df: pd.DataFrame, records: List[Dict[str, object]]) -> None:
        ip_col = self.columns.ip_address
        customer_col = self.columns.customer_id
        order_id_col = self.columns.order_id
        rules = self.config.rules

        if ip_col not in df or customer_col not in df:
            return

        df["ip_order_count_flag"] = df.groupby(ip_col)[order_id_col].transform("count")
        df["ip_unique_account_count"] = df.groupby(ip_col)[customer_col].transform("nunique")

        high_volume_mask = (df["ip_order_count_flag"] >= rules.ip_daily_order_threshold) | (
            df["ip_unique_account_count"] >= rules.ip_unique_account_threshold
        )

        if not high_volume_mask.any():
            return

        for _, row in df[high_volume_mask].iterrows():
            details = (
                f"IP {row[ip_col]} 关联 {int(row['ip_unique_account_count'])} 个账号，"
                f"订单量 {int(row['ip_order_count_flag'])} 笔"
            )
            records.append(
                {
                    order_id_col: row[order_id_col],
                    "anomaly_type": "ip_multi_account",
                    "confidence": self.config.rules.ip_multi_account_confidence,
                    "score": float(row["ip_unique_account_count"]),
                    "details": details,
                    "suggestion": "建议核查该 IP，可能存在羊毛党或批量注册行为。",
                }
            )

    def _detect_location_mismatch(self, df: pd.DataFrame, records: List[Dict[str, object]]) -> None:
        phone_col = self.columns.phone_number
        address_col = self.columns.shipping_address
        order_id_col = self.columns.order_id
        customer_col = self.columns.customer_id

        if phone_col not in df or address_col not in df:
            return

        phone_regions = df[phone_col].apply(self.phone_resolver.resolve)
        address_regions = df[address_col].apply(self.address_resolver.resolve)

        mismatch_mask = (
            phone_regions.notna()
            & address_regions.notna()
            & (phone_regions != address_regions)
        )

        if mismatch_mask.any():
            for idx, row in df[mismatch_mask].iterrows():
                details = (
                    f"手机号归属地 {phone_regions.loc[idx]} 与地址 {address_regions.loc[idx]} 不一致"
                )
                records.append(
                    {
                        order_id_col: row[order_id_col],
                        "anomaly_type": "location_mismatch",
                        "confidence": self.config.rules.location_mismatch_confidence,
                        "score": 1.0,
                        "details": details,
                        "suggestion": "建议人工复核收货信息，必要时联系用户二次确认。",
                    }
                )

    def _run_isolation_forest(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, Optional[pd.Series], List[Dict[str, object]]]:
        if not self.config.isolation_forest.enabled:
            return pd.DataFrame(index=df.index), None, []

        if df.shape[0] < self.config.minimum_orders_for_model:
            features = self._build_feature_matrix(df)
            return features, None, []

        features = self._build_feature_matrix(df)
        model = IsolationForest(
            contamination=self.config.isolation_forest.contamination,
            n_estimators=self.config.isolation_forest.n_estimators,
            max_samples=self.config.isolation_forest.max_samples,
            max_features=self.config.isolation_forest.max_features,
            random_state=self.config.isolation_forest.random_state,
            bootstrap=self.config.isolation_forest.bootstrap,
        )

        model.fit(features)
        decision_scores = model.decision_function(features)
        anomaly_flags = model.predict(features)

        raw_scores = -decision_scores
        normalized_scores = (raw_scores - raw_scores.min()) / (raw_scores.max() - raw_scores.min() + 1e-9)
        model_scores = pd.Series(normalized_scores, index=df.index, name="anomaly_score")

        order_id_col = self.columns.order_id
        records: List[Dict[str, object]] = []
        for idx in df.index[anomaly_flags == -1]:
            score = float(model_scores.loc[idx])
            confidence = min(0.99, 0.5 + 0.5 * score)
            details = (
                f"隔离森林模型判定异常，分值 {score:.3f}"
            )
            records.append(
                {
                    order_id_col: df.at[idx, order_id_col],
                    "anomaly_type": "ai_outlier",
                    "confidence": confidence,
                    "score": score,
                    "details": details,
                    "suggestion": "建议重点核查订单支付、物流信息。",
                }
            )

        return features, model_scores, records

    def _build_feature_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        order_id_col = self.columns.order_id
        datetime_col = self.columns.order_datetime
        amount_col = self.columns.order_amount
        customer_col = self.columns.customer_id
        ip_col = self.columns.ip_address

        features = pd.DataFrame(index=df.index)

        features["order_amount"] = df[amount_col].fillna(0.0)
        features["log_order_amount"] = np.log1p(features["order_amount"].clip(lower=0))

        if customer_col in df:
            features["customer_order_count"] = (
                df.groupby(customer_col)[order_id_col].transform("count").fillna(0)
            )
            features["customer_amount_mean"] = (
                df.groupby(customer_col)[amount_col].transform("mean").fillna(0)
            )
            features["customer_amount_std"] = (
                df.groupby(customer_col)[amount_col].transform("std").fillna(0).replace({np.nan: 0})
            )
        else:
            features["customer_order_count"] = 0
            features["customer_amount_mean"] = 0
            features["customer_amount_std"] = 0

        if ip_col in df:
            features["ip_order_count"] = df.groupby(ip_col)[order_id_col].transform("count").fillna(0)
        else:
            features["ip_order_count"] = 0

        if datetime_col in df and customer_col in df:
            df_sorted = df.sort_values(datetime_col)
            df_sorted["hours_since_prev_tmp"] = (
                df_sorted.groupby(customer_col, dropna=False)[datetime_col]
                .diff()
                .dt.total_seconds()
                .div(3600.0)
            )
            fallback = (
                df_sorted.groupby(customer_col, dropna=False)["hours_since_prev_tmp"]
                .transform(lambda s: s[s.notna()].median())
                .fillna(24.0)
            )
            df_sorted["hours_since_prev_tmp"] = (
                df_sorted["hours_since_prev_tmp"].fillna(fallback).fillna(24.0)
            )
            features["hours_since_prev"] = df_sorted["hours_since_prev_tmp"].reindex(df.index).fillna(24.0)
        else:
            features["hours_since_prev"] = 24.0

        features = features.fillna(0.0)
        return features

