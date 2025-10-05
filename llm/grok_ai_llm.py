import logging
import os
import threading
from typing import Any, Dict, List, Optional

import requests

from llm.llm_abstract_class import LLMInterface


logger = logging.getLogger(__name__)


class GrokAiLLM(LLMInterface):
    """LLMInterface implementation relying on xAI's Grok API."""

    _instance = None
    _instance_lock = threading.Lock()

    _session: Optional[requests.Session] = None
    _session_lock = threading.Lock()
    _session_api_key: str | None = None

    API_URL = "https://api.x.ai/v1/messages"
    MODEL = "grok-2-mini"
    REQUEST_TIMEOUT = (3.05, 30)  # (connect timeout, read timeout)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self.api_key = os.environ.get("GROK_API_KEY")
        if not self.api_key:
            raise ValueError("GROK_API_KEY environment variable is not set")

        self.session = self._get_or_create_session(self.api_key)
        self.base_messages: List[Dict[str, Any]] = [{"role": "system", "content": self.llm_context}]
        self.messages: List[Dict[str, Any]] = list(self.base_messages)

        self._initialized = True

    @classmethod
    def _get_or_create_session(cls, api_key: str) -> requests.Session:
        if cls._session is None or cls._session_api_key != api_key:
            with cls._session_lock:
                if cls._session is None or cls._session_api_key != api_key:
                    session = requests.Session()
                    session.headers.update(
                        {
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                        }
                    )
                    cls._session = session
                    cls._session_api_key = api_key
        assert cls._session is not None
        return cls._session

    def add_configuration_file_to_prompt(self, configuration_file):
        self._append_system_message(
            f"""Ce fichier te permet de prendre connaissance, de la configuration d'un des manager de service auquel tu as accès.
        Tu peux t'en servir pour prendre connaissance de toute la configuration dont tu pourrais avoir besoin
        {configuration_file}"""
        )

    def add_manager_file_to_prompt(self, manager_file):
        self._append_system_message(
            f"""Ce fichier te permet de prendre connaissance, du manager de service auquel tu as accès
        Tu peux l'utiliser pour t'aider à reconnaître la commande vocale à exécuter etc... chaque méthode documentée est utilisable etc...
        {manager_file}"""
        )

    def _append_system_message(self, content: str) -> None:
        message = {"role": "system", "content": content}
        self.base_messages.append(message)
        self.messages.append({"role": "system", "content": content})

    def interpret_request(self, request):
        self.messages.append({"role": "user", "content": request})

        payload = {"model": self.MODEL, "messages": self.messages}
        try:
            response = self.session.post(self.API_URL, json=payload, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Grok API request failed: %s", exc, exc_info=True)
            raise

        answer = self._extract_answer(response.json())
        self.messages.append({"role": "assistant", "content": answer})
        return answer

    @staticmethod
    def _extract_answer(response_json: Dict[str, Any]) -> str:
        choices = response_json.get("choices")
        if not choices:
            raise ValueError("Invalid Grok response: missing choices")

        message = choices[0].get("message", {})
        content = message.get("content")

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts: List[str] = []
            for part in content:
                if isinstance(part, dict):
                    text = part.get("text") or part.get("output_text")
                    if text:
                        parts.append(text)
                elif isinstance(part, str):
                    parts.append(part)
            if parts:
                return "".join(parts)

        if "output_text" in message:
            return message["output_text"]

        raise ValueError("Invalid Grok response: missing assistant content")

    def reset_conversation(self):
        self.messages = list(self.base_messages)
