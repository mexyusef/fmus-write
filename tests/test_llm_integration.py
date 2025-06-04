#!/usr/bin/env python3
"""
Test script to verify the LLM integration works correctly.
This follows the HOW-TO-USE.md instructions.
"""
import sys
import logging
from fmus_write.llm.base import LLMMessage
from fmus_write.llm.providers.gemini import GeminiProvider
from fmus_write.llm.providers.provider_map import PROVIDER_MAP

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("LLM_TEST")

def test_direct_provider_usage():
    """Test direct usage of a provider as described in HOW-TO-USE.md"""
    logger.info("Testing direct provider usage")

    try:
        # Create the provider
        provider = GeminiProvider()
        logger.info("Created GeminiProvider instance")

        # Create a message
        message = LLMMessage(role="user", content="Write a very short poem about AI.")

        # Generate a response
        logger.info("Calling generate_response with a test message")
        response = provider.generate_response([message])

        # Output the response
        logger.info("Response received:")
        print("\n======= RESPONSE =======")
        print(response)
        print("=======================\n")

        return True
    except Exception as e:
        logger.error(f"Error during direct provider test: {e}", exc_info=True)
        return False

def list_available_providers():
    """List all available providers from the provider map"""
    logger.info("Available LLM providers:")
    for provider_name in PROVIDER_MAP.keys():
        logger.info(f" - {provider_name}")

def main():
    """Main test function"""
    logger.info("Starting LLM integration test")
    list_available_providers()

    result = test_direct_provider_usage()
    if result:
        logger.info("✅ Test completed successfully")
        return 0
    else:
        logger.error("❌ Test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
