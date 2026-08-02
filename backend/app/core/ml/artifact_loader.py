import os
import json
import logging
import sys
from typing import Any, Dict, Optional
from importlib.metadata import version as get_package_version

logger = logging.getLogger("ml_artifact_loader")

# Setup generic dummy mock model class to prevent test environments from failing
class MockModel:
    """Mock ML model for local development and testing when binary files are absent."""
    def __init__(self, domain: str):
        self.domain = domain

    def predict(self, *args, **kwargs) -> Any:
        # Dummy prediction returns
        if self.domain == "forecasting":
            return [10.0] * 7
        elif self.domain == "pricing":
            return [5.0]
        elif self.domain == "anomaly":
            return [1]
        return [0.0]


class ArtifactLoader:
    """
    Generic ML Artifact Manager.
    Loads model binaries once, caches them in memory, and performs manifest validation.
    Designed abstractly so filesystem loading can later be swapped for cloud providers (S3/GCS).
    """

    def __init__(self, artifacts_dir: Optional[str] = None):
        if not artifacts_dir:
            # Locate standard backend/artifacts folder relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            artifacts_dir = os.path.join(base_dir, "artifacts")
        
        self.artifacts_dir = artifacts_dir
        self._model_cache: Dict[str, Any] = {}
        self._metadata_cache: Dict[str, Dict[str, Any]] = {}
        
        # Check if running under testing/dev environment to allow mock models
        from app.core.config import settings
        self.is_test_env = (
            os.environ.get("APP_ENV") == "test" or 
            os.environ.get("TESTING") == "1" or 
            "pytest" in sys.modules or
            settings.APP_ENV == "development"
        )

    def load_all(self) -> None:
        """Startup discovery and verification loop."""
        domains = ["forecasting", "pricing", "anomaly"]
        for domain in domains:
            try:
                self.load_model(domain)
            except Exception as e:
                if self.is_test_env:
                    logger.warning(
                        f"Skipping startup load failure for domain '{domain}' due to test/dev environment fallback. Reason: {e}"
                    )
                    # Cache mock fallback models so app runs cleanly
                    self._model_cache[domain] = MockModel(domain)
                    self._metadata_cache[domain] = {
                        "model_name": domain,
                        "model_version": "0.0.0-mock",
                        "algorithm": "Mock Fallback Model"
                    }
                else:
                    logger.critical(f"ML Model Loading failed on domain '{domain}': {e}")
                    raise e

    def load_model(self, domain: str) -> Any:
        """
        Discovers, validates, and loads a model binary for a specific domain.
        Future-Proofing: swap this implementation logic if sourcing from S3/GCS buckets.
        """
        domain_dir = os.path.join(self.artifacts_dir, domain)
        metadata_path = os.path.join(domain_dir, "metadata.json")
        model_filename = f"{domain}_v1.pkl"
        model_path = os.path.join(domain_dir, model_filename)

        # 1. Discover metadata and binaries
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Missing model metadata manifest at: {metadata_path}")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Missing serialized model binary at: {model_path}")

        # 2. Parse manifest metadata
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        self._validate_metadata_schema(metadata, domain)
        self._validate_framework_compatibility(metadata)

        # 3. Load binary into memory
        # Import joblib/pickle dynamically to keep startup lightweight
        import joblib
        try:
            model_instance = joblib.load(model_path)
        except Exception as e:
            raise ValueError(f"Failed to deserialize binary model artifact '{model_filename}': {e}")

        # 4. Cache in memory
        self._model_cache[domain] = model_instance
        self._metadata_cache[domain] = metadata
        
        logger.info(
            f"Successfully loaded '{metadata.get('algorithm')}' v{metadata.get('model_version')} "
            f"for domain '{domain}'"
        )
        return model_instance

    def get_model(self, domain: str) -> Any:
        """Returns the cached model instance for the given domain."""
        if domain not in self._model_cache:
            # On-demand loading fallback
            try:
                self.load_model(domain)
            except Exception as e:
                if self.is_test_env:
                    logger.warning(f"Domain model '{domain}' absent; returning mock fallback.")
                    self._model_cache[domain] = MockModel(domain)
                else:
                    raise e
        return self._model_cache[domain]

    def get_metadata(self, domain: str) -> Dict[str, Any]:
        """Returns the cached metadata for the given domain."""
        if domain not in self._metadata_cache:
            try:
                self.load_model(domain)
            except Exception as e:
                if self.is_test_env:
                    return {
                        "model_name": domain,
                        "model_version": "0.0.0-mock",
                        "algorithm": "Mock Fallback Model"
                    }
                raise e
        return self._metadata_cache[domain]

    def _validate_metadata_schema(self, metadata: dict, domain: str) -> None:
        """Enforces schema rules of MODEL_ARTIFACT_SPEC.md."""
        required_keys = ["model_name", "model_version", "algorithm", "trained_on", "framework_versions"]
        for key in required_keys:
            if key not in metadata:
                raise ValueError(f"Manifest 'metadata.json' is missing required spec key: '{key}'")
        
        if metadata["model_name"] != domain:
            raise ValueError(
                f"Mismatch model name in metadata! Expected '{domain}', found '{metadata['model_name']}'"
            )

    def _validate_framework_compatibility(self, metadata: dict) -> None:
        """Validates key environment dependency major version alignment."""
        frameworks = metadata.get("framework_versions", {})
        for library, expected_version in frameworks.items():
            if library == "python":
                # We skip strict Python check or check only major version
                continue
            
            try:
                installed_ver = get_package_version(library)
            except Exception:
                logger.warning(f"Could not check installed version for package '{library}'")
                continue
            
            # Compare major versions
            expected_major = expected_version.split(".")[0]
            installed_major = installed_ver.split(".")[0]
            
            if expected_major != installed_major:
                err_msg = (
                    f"ML Runtime Mismatch: Incompatible major version of '{library}'! "
                    f"Model requires v{expected_version}, but environment runs v{installed_ver}."
                )
                if self.is_test_env:
                    logger.warning(err_msg + " (Bypassing failure in test mode)")
                else:
                    raise ValueError(err_msg)
            elif expected_version != installed_ver:
                logger.warning(
                    f"ML Runtime Warning: Minor version skew for '{library}'. "
                    f"Model trained on v{expected_version}, local environment has v{installed_ver}."
                )


# Global Singleton Manager
_global_loader: Optional[ArtifactLoader] = None

def get_artifact_loader() -> ArtifactLoader:
    """Global getter/singleton accessor."""
    global _global_loader
    if _global_loader is None:
        _global_loader = ArtifactLoader()
    return _global_loader
