import streamlit as st
import logging
import groq
import time
from enum import Enum

logger = logging.getLogger(__name__)

class ModelTier(Enum):
    """
    Enum representing different tiers of models for fallback and prioritization.
    """
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    FALLBACK = "fallback"

class ModelManager:
    """
    Manages AI model selection, fallback, and rate limits for generating analysis.
    Implements an agent-based approach for model management where the system 
    selects the best available model based on the retry count.
    """

    # Configuration for different model tiers
    MODEL_CONFIG = {
        ModelTier.PRIMARY: {
            "provider": "groq",
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 2000,
            "temperature": 0.7
        },
        ModelTier.SECONDARY: {
            "provider": "groq", 
            "model": "llama-3-8b-8192",
            "max_tokens": 2000,
            "temperature": 0.7
        },
        ModelTier.TERTIARY: {
            "provider": "groq",
            "model": "mixtral-8x7b-32768",
            "max_tokens": 2000, 
            "temperature": 0.7
        },
        ModelTier.FALLBACK: {
            "provider": "groq",
            "model": "gemma-7b-it",
            "max_tokens": 2000,
            "temperature": 0.7
        }
    }
    
    def __init__(self):
        """
        Initializes the ModelManager with a set of clients for each AI provider.
        The clients are initialized based on the configuration from MODEL_CONFIG.
        """
        self.clients = {}
        self._initialize_clients()

    def _initialize_clients(self):
        """
        Initializes API clients for each provider.
        The clients are set up to interface with the respective model providers (e.g., Groq).
        
        Raises:
            Exception: If there is an issue with initializing the provider client (e.g., API key issue).
        """
        try:
            self.clients["groq"] = groq.Groq(api_key=st.secrets["GROQ_API_KEY"])
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")

    def generate_analysis(self, data, system_prompt, retry_count=0):
        """
        Generates analysis using the best available model, with automatic fallback 
        to different models in case of failure. The model selection is tiered based 
        on the retry count.

        Args:
            data (str): The input data for which the analysis is to be generated.
            system_prompt (str): The system prompt to guide the model in generating the analysis.
            retry_count (int): The number of retries attempted, which determines the model tier.

        Returns:
            dict: A dictionary containing the success status and the generated content 
                  or an error message.
                  
        Retry Logic:
            - First attempt uses the primary model.
            - Second attempt uses the secondary model.
            - Third attempt uses the tertiary model.
            - Further attempts use the fallback model.
        """
        if retry_count > 3:
            return {"success": False, "error": "All models failed after multiple retries"}

        # Determine which model tier to use based on retry count
        if retry_count == 0:
            tier = ModelTier.PRIMARY
        elif retry_count == 1:
            tier = ModelTier.SECONDARY
        elif retry_count == 2:
            tier = ModelTier.TERTIARY
        else:
            tier = ModelTier.FALLBACK
            
        model_config = self.MODEL_CONFIG[tier]
        provider = model_config["provider"]
        model = model_config["model"]
        
        # Check if we have a client for this provider
        if provider not in self.clients:
            logger.error(f"No client available for provider: {provider}")
            return self.generate_analysis(data, system_prompt, retry_count + 1)
            
        try:
            client = self.clients[provider]
            logger.info(f"Attempting generation with {provider} model: {model}")
            
            if provider == "groq":
                # Call Groq API for analysis generation
                completion = client.chat.completions.create(
                    model=model,
                    messages=[ 
                        {"role": "system", "content": system_prompt}, 
                        {"role": "user", "content": str(data)}
                    ],
                    temperature=model_config["temperature"],
                    max_tokens=model_config["max_tokens"]
                )
                
                return {
                    "success": True,
                    "content": completion.choices[0].message.content,
                    "model_used": f"{provider}/{model}"
                }
                
        except Exception as e:
            error_message = str(e).lower()
            logger.warning(f"Model {model} failed: {error_message}")
            
            # Check for rate limit errors
            if "rate limit" in error_message or "quota" in error_message:
                # Wait briefly before retrying with a different model
                time.sleep(2)
            
            # Try next model in hierarchy
            return self.generate_analysis(data, system_prompt, retry_count + 1)
            
        return {"success": False, "error": "Analysis failed with all available models"}