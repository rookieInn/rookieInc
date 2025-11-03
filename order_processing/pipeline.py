"""Order processing pipeline orchestration module."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from .anomaly_detection import OrderAnomalyDetector
from .config import PipelineConfig
from .data_cleaning import OrderDataCleaner


@dataclass(slots=True)
class PipelineResult:
    """Aggregated result for a pipeline execution."""

    cleaned_data: pd.DataFrame
    cleaning_stats: Dict[str, int]
    anomalies: pd.DataFrame
    anomaly_features: pd.DataFrame
    anomaly_scores: Optional[pd.Series]
    tracking_imputations: Optional[pd.DataFrame]


class OrderProcessingPipeline:
    """Coordinate data loading, cleaning and anomaly detection."""

    def __init__(self, config: Optional[PipelineConfig] = None) -> None:
        self.config = config or PipelineConfig()
        self.cleaner = OrderDataCleaner(self.config.cleaning, self.config.columns)
        self.detector = OrderAnomalyDetector(self.config.anomaly, self.config.columns)

    def run(
        self,
        raw_orders: str | Path | pd.DataFrame,
        *,
        historical_orders: Optional[str | Path | pd.DataFrame] = None,
    ) -> PipelineResult:
        raw_df = self._load_dataframe(raw_orders)
        historical_df = self._load_dataframe(historical_orders) if historical_orders is not None else None

        cleaning_result = self.cleaner.clean(raw_df, historical_orders=historical_df)
        anomaly_result = self.detector.detect(cleaning_result.data)

        return PipelineResult(
            cleaned_data=cleaning_result.data,
            cleaning_stats=cleaning_result.stats,
            anomalies=anomaly_result.anomalies,
            anomaly_features=anomaly_result.features,
            anomaly_scores=anomaly_result.model_scores,
            tracking_imputations=cleaning_result.tracking_imputations,
        )

    def run_to_files(
        self,
        *,
        raw_orders_path: str | Path,
        cleaned_output_path: str | Path,
        anomaly_report_path: str | Path,
        historical_orders_path: Optional[str | Path] = None,
    ) -> PipelineResult:
        result = self.run(
            raw_orders=raw_orders_path,
            historical_orders=historical_orders_path,
        )

        self._ensure_parent(cleaned_output_path)
        self._ensure_parent(anomaly_report_path)

        result.cleaned_data.to_csv(cleaned_output_path, index=False)
        result.anomalies.to_csv(anomaly_report_path, index=False)

        return result

    @staticmethod
    def _load_dataframe(source: str | Path | pd.DataFrame | None) -> Optional[pd.DataFrame]:
        if source is None:
            return None
        if isinstance(source, pd.DataFrame):
            return source.copy()

        path = Path(source).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Data source not found: {path}")

        if path.suffix.lower() == ".parquet":
            try:
                return pd.read_parquet(path)
            except ImportError as exc:
                raise RuntimeError(
                    "Reading Parquet files requires the pyarrow or fastparquet package"
                ) from exc
        return pd.read_csv(path)

    @staticmethod
    def _ensure_parent(path: str | Path) -> None:
        parent = Path(path).expanduser().parent
        parent.mkdir(parents=True, exist_ok=True)

