import json
import logging
from typing import Dict, Any, Optional

from .llm_handler import LLMHandler
from .prompts import (
    MAIN_SYSTEM_PROMPT,
    EXAMPLE_USER_QUERY,
    EXAMPLE_LLM_RESPONSE
)
from .config import SUPERSET_DATASOURCE_IDS

logger = logging.getLogger(__name__)


class ChartBuilderAgent:
    """
    This is the primary agent responsible for the entire process.
    It takes a user query and DB schema, makes a single call to the LLM,
    and returns a fully formed Superset chart configuration.
    """

    def __init__(self, llm_handler: LLMHandler):
        self.llm = llm_handler
        self.model = "gpt-4o-mini" # Or your preferred model

    def _get_system_prompt(self, db_schema: str) -> str:
        """Constructs the full system prompt for the LLM."""
        # This formats the main prompt template with the dynamic db_schema
        # and the static examples.
        return MAIN_SYSTEM_PROMPT.format(
            db_schema=db_schema,
            example_user_query=EXAMPLE_USER_QUERY,
            example_llm_response=json.dumps(EXAMPLE_LLM_RESPONSE, indent=2)
        )

    def _parse_llm_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Safely parses the JSON response from the LLM.
        Handles responses that might be wrapped in markdown code blocks.
        """
        if not response_text:
            logger.error("LLM returned an empty response.")
            return None

        # Clean potential markdown formatting
        if "```json" in response_text:
            clean_text = response_text.split("```json\n")[1].split("\n```")[0]
        else:
            clean_text = response_text

        try:
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from LLM response: {e}")
            logger.debug(f"Raw LLM response was: {response_text}")
            return None

    def generate_chart_config(self, user_query: str, db_schema: str) -> Dict[str, Any]:
        """
        Orchestrates the process of generating a chart configuration from a user query.

        Returns:
            A dictionary containing the final chart payload or an error message.
        """
        system_prompt = self._get_system_prompt(db_schema)

        try:
            # Step 1: Call the LLM to get the structured analysis and config
            llm_response_text = self.llm.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_query
            )

            # Step 2: Parse the response
            parsed_config = self._parse_llm_response(llm_response_text)

            if not parsed_config:
                return {"error": "Failed to get a valid configuration from the LLM."}

            # Step 3: Validate and finalize the payload
            # The LLM now provides the 'params' directly. We just need to ensure
            # the datasource_id is correctly set.
            table_name = parsed_config.get("datasource_table_name")
            if not table_name or table_name not in SUPERSET_DATASOURCE_IDS:
                return {"error": f"LLM returned an invalid or missing table name: '{table_name}'"}

            # Inject the datasource_id and type into the final payload
            final_payload = {
                "slice_name": parsed_config.get("slice_name", "Untitled Chart"),
                "viz_type": parsed_config.get("viz_type"),
                "params": json.dumps(parsed_config.get("params", {})),
                "datasource_id": SUPERSET_DATASOURCE_IDS[table_name],
                "datasource_type": "table"
            }
            
            # Basic validation
            if not final_payload["viz_type"] or not final_payload["params"]:
                 return {"error": "LLM response was missing 'viz_type' or 'params'."}

            return final_payload

        except Exception as e:
            logger.error(f"An unexpected error occurred in generate_chart_config: {e}", exc_info=True)
            return {"error": "An unexpected internal error occurred."}
