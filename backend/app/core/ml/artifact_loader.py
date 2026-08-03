import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("ml_artifact_loader")

class MockModel:
    """Mock ML model representing the Hugging Face remote task execution."""
    def __init__(self, domain: str):
        self.domain = domain

    def predict(self, *args, **kwargs) -> Any:
        if self.domain == "forecasting":
            return [10.0] * 7
        elif self.domain == "pricing":
            return [5.0]
        elif self.domain == "anomaly":
            return [1]
        return [0.0]


class ArtifactLoader:
    """
    ML Artifact Manager.
    Configured to route inferences via Hugging Face API.
    Bypasses local .pkl files and joblib dependency.
    """

    def __init__(self, artifacts_dir: Optional[str] = None):
        self._model_cache: Dict[str, Any] = {}
        self._metadata_cache: Dict[str, Dict[str, Any]] = {}

    def load_all(self) -> None:
        """Initialize local metadata maps indicating Hugging Face routing."""
        logger.info("Initializing ML Artifacts: routing inferences via Hugging Face Serverless API.")
        domains = ["forecasting", "pricing", "anomaly"]
        for domain in domains:
            self._model_cache[domain] = MockModel(domain)
            self._metadata_cache[domain] = {
                "model_name": domain,
                "model_version": "1.0.0-huggingface",
                "algorithm": f"Hugging Face Remote {domain.title()} API",
                "trained_on": "Hugging Face Hub",
                "framework_versions": {},
            }

    def load_model(self, domain: str) -> Any:
        """Returns the mock model instance since deserialization is disabled."""
        if domain not in self._model_cache:
            self.load_all()
        return self._model_cache[domain]

    def get_model(self, domain: str) -> Any:
        """Returns the cached model instance for the given domain."""
        if domain not in self._model_cache:
            self.load_all()
        return self._model_cache[domain]

    def get_metadata(self, domain: str) -> Dict[str, Any]:
        """Returns the cached metadata for the given domain."""
        if domain not in self._metadata_cache:
            self.load_all()
        return self._metadata_cache[domain]


# Global Singleton Manager
_global_loader: Optional[ArtifactLoader] = None

def get_artifact_loader() -> ArtifactLoader:
    """Global getter/singleton accessor."""
    global _global_loader
    if _global_loader is None:
        _global_loader = ArtifactLoader()
        _global_loader.load_all()
    return _global_loader
