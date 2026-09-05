import os
import tempfile
import pytest
from app.config import Settings


def test_secrets_file_loader():
    with tempfile.TemporaryDirectory() as tmpdir:
        gemini_secret_path = os.path.join(tmpdir, "gemini_key.txt")
        jwt_secret_path = os.path.join(tmpdir, "jwt_secret.txt")

        with open(gemini_secret_path, "w", encoding="utf-8") as f:
            f.write("secret-gemini-key-12345\n")

        with open(jwt_secret_path, "w", encoding="utf-8") as f:
            f.write("mounted-jwt-secret-67890\n")

        # Instantiate settings with custom file paths
        s = Settings(
            gemini_api_key="",
            jwt_secret="super-secret-aisle-key-change-in-production-12345",
            gemini_api_key_file=gemini_secret_path,
            jwt_secret_file=jwt_secret_path,
        )

        assert s.gemini_api_key == "secret-gemini-key-12345"
        assert s.jwt_secret == "mounted-jwt-secret-67890"
