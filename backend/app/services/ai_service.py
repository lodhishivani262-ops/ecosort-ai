"""EcoSort AI - AI Perception Service Abstraction and Gemini Provider (Stage 3).

Architectural Rule:
The AI perception layer is responsible solely for answering:
'What appears to be in this image or text?'
It extracts structured observations (item, material, condition, contamination, visual clues, confidence).
It does NOT make the final disposal decision or bin assignment (which is reserved for Stage 4).
"""

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.core.config import settings
from app.core.security import AppException
from app.schemas.classification import (
    ConfidenceLevel,
    ContaminationLevel,
    WastePerception,
)

logger = logging.getLogger("ecosort")

ECOSORT_PERCEPTION_SYSTEM_PROMPT = """
You are the perception component of EcoSort AI, a household waste segregation assistant aligned with UN Sustainable Development Goal 12.

Your sole responsibility is to identify and describe the primary visible or text-described household waste item.
You must NOT make the final disposal recommendation (e.g., do NOT mention bins, recycling rules, or disposal actions).

Analyze the input and return a JSON object adhering strictly to the schema:
1. item_name: Name of the primary/most prominent waste object (e.g., 'plastic water bottle', 'takeaway container', 'pizza box', 'AA battery').
2. material: Observable base material composition (e.g., 'plastic (PET)', 'polypropylene', 'cardboard', 'aluminum', 'glass', 'organic', 'lithium/metal', 'unknown').
3. condition: Observable physical state (e.g., 'clean', 'used', 'dirty', 'wet', 'dry', 'food-contaminated', 'liquid-filled', 'broken', 'damaged', 'unknown').
4. contamination: Level of visible or described contamination ('NONE', 'LOW', 'MEDIUM', 'HIGH', 'UNKNOWN').
5. visual_clues: Up to 4 concise visual/textual observations (e.g., 'transparent cylindrical body', 'grease stain on base'). Empty list if none.
6. confidence: Controlled rating ('HIGH', 'MEDIUM', 'LOW').
   - Must use 'LOW' if the item is blurry, dark, obscured, ambiguous, or if material cannot be clearly determined.
7. uncertainty_reason: Explain why if confidence is LOW or features are ambiguous (e.g., 'object is blurry and partially obscured'). Set to null if clear.
8. is_safety_sensitive: Set to true if the item is a battery, electronics, hazardous chemical, medical sharp, aerosol can, or broken glass. Otherwise false.

Scope: The MVP analyzes the primary/most prominent waste item.
Do not invent details that are not visible or stated. If evidence is lacking, use 'unknown' and lower confidence.
"""


class BaseAIService(ABC):
    """Abstract interface defining the visual and textual perception capabilities.

    Ensures decoupling between the FastAPI routing layer and specific AI providers.
    """

    @abstractmethod
    async def analyze_image(
        self, image_bytes: bytes, filename: str, mime_type: str = "image/jpeg"
    ) -> WastePerception:
        """Analyzes raw image bytes and returns structured perception observations."""
        pass

    @abstractmethod
    async def analyze_text(self, text: str) -> WastePerception:
        """Analyzes text description and returns structured perception observations."""
        pass


class GeminiAIService(BaseAIService):
    """Multimodal AI Perception Service using the official Google Gemini SDK.

    Provides structured observations with retry management, timeout bounds,
    and sanitized exception handling.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        max_retries: Optional[int] = None,
        client: Optional[genai.Client] = None,
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.AI_MODEL
        self.timeout_seconds = timeout_seconds or settings.AI_TIMEOUT_SECONDS
        self.max_retries = max_retries or settings.AI_MAX_RETRIES
        self._provided_client = client
        self._client = client

    def _get_client(self) -> genai.Client:
        """Returns or lazily instantiates the Gemini API client bound to the current event loop."""
        if self._provided_client is not None:
            return self._provided_client

        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self._client is not None and getattr(self, "_loop", None) == current_loop:
            return self._client

        if not self.api_key or not self.api_key.strip():
            logger.error("Gemini API key is not configured.")
            raise AppException(
                code="AI_API_KEY_MISSING",
                message="AI provider is not configured. Please set GEMINI_API_KEY in environment variables.",
                status_code=503,
            )

        self._client = genai.Client(api_key=self.api_key)
        self._loop = current_loop
        return self._client

    async def _call_gemini_with_retries(self, contents: list) -> WastePerception:
        """Executes a multimodal request with structured JSON schema, timeouts, and retries."""
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=WastePerception,
            system_instruction=ECOSORT_PERCEPTION_SYSTEM_PROMPT,
            temperature=0.1,  # Low temperature for deterministic, consistent perception
        )

        models_to_try = [self.model_name]
        for fallback in ["gemini-3.5-flash-lite", "gemini-3.5-flash"]:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_error = None
        for attempt in range(1, self.max_retries + 2):
            client = self._get_client()
            model_to_use = models_to_try[(attempt - 1) % len(models_to_try)]
            try:
                # Wrap network call in strict timeout bounds
                response = await asyncio.wait_for(
                    client.aio.models.generate_content(
                        model=model_to_use,
                        contents=contents,
                        config=config,
                    ),
                    timeout=self.timeout_seconds,
                )

                if not response or not response.text:
                    raise AppException(
                        code="AI_EMPTY_RESPONSE",
                        message="AI perception service returned an empty response.",
                        status_code=502,
                    )

                # Parse and validate structured output
                try:
                    data = json.loads(response.text)
                    perception = WastePerception.model_validate(data)
                    return perception
                except (json.JSONDecodeError, Exception) as parse_err:
                    logger.error(f"Failed to parse structured JSON from AI output: {parse_err}")
                    raise AppException(
                        code="AI_PARSING_ERROR",
                        message="Failed to parse structured observation from AI response.",
                        status_code=502,
                    )

            except asyncio.TimeoutError:
                last_error = AppException(
                    code="AI_TIMEOUT",
                    message=f"AI perception service timed out after {self.timeout_seconds} seconds.",
                    status_code=504,
                )
                logger.warning(f"Gemini API timeout on attempt {attempt}/{self.max_retries + 1}")

            except genai_errors.APIError as api_err:
                status_code = getattr(api_err, "code", 500)
                err_message = str(api_err)
                logger.warning(f"Gemini API error (attempt {attempt}): {status_code} - {err_message}")

                # Non-retryable authentication errors
                if status_code in (401, 403) or "API_KEY_INVALID" in err_message:
                    raise AppException(
                        code="AI_AUTH_FAILED",
                        message="Authentication with AI provider failed. Please check credentials.",
                        status_code=502,
                    )
                # Rate limit from provider
                elif status_code == 429 or "RESOURCE_EXHAUSTED" in err_message:
                    raise AppException(
                        code="AI_RATE_LIMITED",
                        message="Upstream AI service rate limit reached. Please wait a moment and try again.",
                        status_code=429,
                    )
                # Retryable server-side failures (5xx, connection drops, or model availability 404)
                elif status_code >= 500 or status_code == 404:
                    last_error = AppException(
                        code="AI_SERVICE_UNAVAILABLE",
                        message="The AI service is temporarily unavailable. Please try again.",
                        status_code=503,
                    )
                else:
                    raise AppException(
                        code="AI_PROVIDER_ERROR",
                        message="Upstream AI provider encountered an error processing the request.",
                        status_code=502,
                    )

            except AppException:
                # Re-raise domain exceptions directly
                raise

            except Exception as unhandled_err:
                logger.error(f"Unexpected error calling Gemini API: {unhandled_err}", exc_info=True)
                if self._provided_client is None:
                    self._client = None
                last_error = AppException(
                    code="AI_SERVICE_UNAVAILABLE",
                    message="The AI service encountered an unexpected error. Please try again.",
                    status_code=503,
                )

            # Apply exponential backoff before retry attempt
            if attempt <= self.max_retries:
                backoff_time = 0.5 * (2 ** (attempt - 1))
                logger.info(f"Retrying AI request in {backoff_time:.1f}s (attempt {attempt + 1})...")
                await asyncio.sleep(backoff_time)

        # Retries exhausted
        if last_error:
            raise last_error
        raise AppException(
            code="AI_SERVICE_UNAVAILABLE",
            message="AI service failed after maximum retry attempts.",
            status_code=503,
        )

    async def analyze_image(
        self, image_bytes: bytes, filename: str, mime_type: str = "image/jpeg"
    ) -> WastePerception:
        """Analyzes an uploaded image using Gemini multimodal vision."""
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        prompt = (
            "Analyze this uploaded image of household waste. "
            "Identify the primary/most prominent waste item, its material, physical condition, "
            "contamination level, observable visual clues, and safety sensitivity."
        )
        return await self._call_gemini_with_retries([prompt, image_part])

    async def analyze_text(self, text: str) -> WastePerception:
        """Analyzes a text description of household waste."""
        prompt = (
            f"Analyze this text description of a household waste item: '{text}'. "
            "Identify the item, likely base material, physical condition, "
            "contamination level, descriptive clues, and safety sensitivity."
        )
        return await self._call_gemini_with_retries([prompt])


class MockAIService(BaseAIService):
    """Deterministic Mock Service for offline testing, local dev, and test suites."""

    async def analyze_image(
        self, image_bytes: bytes, filename: str, mime_type: str = "image/jpeg"
    ) -> WastePerception:
        """Simulates multimodal image perception based on filename cues."""
        lower_name = filename.lower()

        if "battery" in lower_name:
            return WastePerception(
                item_name="Alkaline AA Battery",
                material="lithium/metal casing",
                condition="used / intact",
                contamination=ContaminationLevel.NONE,
                visual_clues=["Cylindrical metallic cell", "Positive contact nipple visible"],
                confidence=ConfidenceLevel.HIGH,
                uncertainty_reason=None,
                is_safety_sensitive=True,
            )
        elif "blurry" in lower_name or "dark" in lower_name:
            return WastePerception(
                item_name="Unidentified Object",
                material="unknown",
                condition="unknown",
                contamination=ContaminationLevel.UNKNOWN,
                visual_clues=["Blurry shape", "Low lighting preventing edge detection"],
                confidence=ConfidenceLevel.LOW,
                uncertainty_reason="The object is blurry and partially obscured; material cannot be determined reliably.",
                is_safety_sensitive=False,
            )
        elif "pizza" in lower_name or "greasy" in lower_name:
            return WastePerception(
                item_name="Cardboard Pizza Box",
                material="corrugated cardboard",
                condition="food-contaminated",
                contamination=ContaminationLevel.HIGH,
                visual_clues=["Square cardboard box", "Visible grease and melted cheese residue on base"],
                confidence=ConfidenceLevel.HIGH,
                uncertainty_reason=None,
                is_safety_sensitive=False,
            )
        else:
            return WastePerception(
                item_name="Plastic Water Bottle",
                material="plastic (PET-1)",
                condition="empty",
                contamination=ContaminationLevel.LOW,
                visual_clues=["Transparent plastic body", "Standard 28mm threaded neck", "Plastic cap attached"],
                confidence=ConfidenceLevel.HIGH,
                uncertainty_reason=None,
                is_safety_sensitive=False,
            )

    async def analyze_text(self, text: str) -> WastePerception:
        """Simulates textual item perception based on keyword heuristics."""
        lower = text.lower()

        if any(w in lower for w in ["battery", "accumulator", "cell"]):
            return WastePerception(
                item_name="Lithium-Ion / Alkaline Battery",
                material="lithium/metal",
                condition="used",
                contamination=ContaminationLevel.NONE,
                visual_clues=["Described as battery cell"],
                confidence=ConfidenceLevel.HIGH,
                uncertainty_reason=None,
                is_safety_sensitive=True,
            )
        elif any(w in lower for w in ["greasy", "pizza", "sauce", "stain", "food"]):
            return WastePerception(
                item_name="Food-Contaminated Paper Container",
                material="paper / cardboard",
                condition="food-contaminated",
                contamination=ContaminationLevel.HIGH,
                visual_clues=["Described with food stains and grease"],
                confidence=ConfidenceLevel.HIGH,
                uncertainty_reason=None,
                is_safety_sensitive=False,
            )
        elif any(w in lower for w in ["blurry", "unknown", "something", "weird", "unclear"]):
            return WastePerception(
                item_name="Unknown Waste Item",
                material="unknown",
                condition="unknown",
                contamination=ContaminationLevel.UNKNOWN,
                visual_clues=[],
                confidence=ConfidenceLevel.LOW,
                uncertainty_reason="Text description is ambiguous and lacks material details.",
                is_safety_sensitive=False,
            )
        elif any(w in lower for w in ["bottle", "carton", "jar", "can"]):
            return WastePerception(
                item_name="Plastic Beverage Bottle",
                material="plastic (PET)",
                condition="clean / empty",
                contamination=ContaminationLevel.NONE,
                visual_clues=["Described as beverage container"],
                confidence=ConfidenceLevel.HIGH,
                uncertainty_reason=None,
                is_safety_sensitive=False,
            )
        else:
            return WastePerception(
                item_name=text.strip().title(),
                material="general household material",
                condition="used",
                contamination=ContaminationLevel.LOW,
                visual_clues=[f"Described as '{text.strip()}'"],
                confidence=ConfidenceLevel.MEDIUM,
                uncertainty_reason=None,
                is_safety_sensitive=False,
            )


# Global service instance for dependency injection
_ai_service_instance: Optional[BaseAIService] = None


def get_ai_service() -> BaseAIService:
    """Dependency provider for FastAPI route handlers."""
    global _ai_service_instance
    if _ai_service_instance is not None:
        return _ai_service_instance

    if settings.AI_PROVIDER.lower() == "gemini":
        _ai_service_instance = GeminiAIService()
    else:
        _ai_service_instance = MockAIService()

    return _ai_service_instance


def set_ai_service(service: Optional[BaseAIService]) -> None:
    """Allows test fixtures to set or reset the AI service implementation."""
    global _ai_service_instance
    _ai_service_instance = service
