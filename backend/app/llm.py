import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.endpoint = settings.OPENAI_ENDPOINT
        self.model_name = settings.OPENAI_MODEL_NAME
        self.deployment_name = settings.OPENAI_DEPLOYMENT_NAME
        self.api_key = settings.OPENAI_API_KEY

        self.client = None
        if self.api_key and self.endpoint:
            try:
                self.client = OpenAI(
                    base_url=self.endpoint,
                    api_key=self.api_key,
                    timeout=30.0
                )
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")

    def is_configured(self) -> bool:
        return bool(self.client and self.api_key and "your_" not in self.api_key.lower())

    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        data_context_str: Optional[str] = None,
        policy_context_str: Optional[str] = None
    ) -> str:
        """
        Sends grounded context and messages to the NeoStats OpenAI LLM.
        Falls back gracefully with helpful error messages if unreachable.
        """
        if not self.is_configured():
            return (
                "⚠️ NeoStats LLM service is not configured or missing an API key in the environment. "
                "Retrieved data and policy context are available above, but automated LLM synthesis is paused."
            )

        # Build augmented prompt
        context_parts = []
        if data_context_str:
            context_parts.append(f"### OPERATIONAL DATABASE CONTEXT (Verified RideWise Records):\n{data_context_str}\n")
        if policy_context_str:
            context_parts.append(f"### VERIFIED POLICY DOCUMENTS CONTEXT:\n{policy_context_str}\n")

        full_context = "\n".join(context_parts)
        augmented_user_message = f"{full_context}\n\n### USER QUESTION:\n{user_message}" if context_parts else user_message

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add past turns
        if conversation_history:
            for turn in conversation_history[-4:]:
                messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})

        messages.append({"role": "user", "content": augmented_user_message})

        try:
            assert self.client is not None
            completion = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=0.2,
                max_tokens=800,
            )
            content = completion.choices[0].message.content
            return content.strip() if content else "No response returned by the language model."
        except Exception as e:
            logger.error(f"Error querying NeoStats LLM: {e}")
            err_str = str(e)
            if "timeout" in err_str.lower():
                return "The NeoStats LLM service timed out. Please retry your request in a moment."
            elif "429" in err_str or "rate limit" in err_str.lower():
                return "The NeoStats LLM rate limit was reached. Please wait a few seconds and try again."
            else:
                return (
                    f"RideWise Assist was able to query the records, but encountered an LLM provider issue: {err_str}.\n"
                    f"Please review the direct database and policy findings provided."
                )

# Singleton
llm_client = LLMClient()
