import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from fastapi import HTTPException, status

from ..models.model import ModelCreate, Model


class ModelService:
    def __init__(self) -> None:
        self.models_file = Path(__file__).parent.parent / "data" / "models.json"
        self._ensure_models_file_exists()

    def _ensure_models_file_exists(self) -> None:
        if not self.models_file.exists():
            self.models_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.models_file, "w", encoding="utf-8") as f:
                json.dump({"models": []}, f, indent=2)

    def _load_models(self) -> List[Dict[str, Any]]:
        try:
            with open(self.models_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("models", [])
        except FileNotFoundError:
            self._ensure_models_file_exists()
            return []
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error reading models data",
            ) from exc

    def _save_models(self, models: List[Dict[str, Any]]) -> None:
        try:
            with open(self.models_file, "w", encoding="utf-8") as f:
                json.dump({"models": models}, f, indent=4, ensure_ascii=False)
        except OSError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error saving model data",
            ) from exc

    def create_model(self, model: ModelCreate) -> Model:
        models = self._load_models()
        now = datetime.utcnow().isoformat()

        new_model: Dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "name": model.name.strip(),
            "description": model.description.strip() if model.description else None,
            "user_id": model.user_id,
            "created_at": now,
            "updated_at": now,
        }

        models.append(new_model)
        self._save_models(models)

        return Model.model_validate(new_model)

    def list_models(self, user_id: str) -> List[Model]:
        models = self._load_models()
        user_models = [m for m in models if m.get("user_id") == user_id]
        return [Model.model_validate(model) for model in user_models]

