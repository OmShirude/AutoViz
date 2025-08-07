import logging
from django.conf import settings

from .llm_handler import LLMHandler
from .chart_creator import ChartCreator
from .system_prompt_generator import SystemPromptGenerator
from .agents import ChartBuilderAgent

logger = logging.getLogger(__name__)

class QueryToDashboard:
    """
    Main service class to process a user query and create a dashboard chart.
    This class now acts as a high-level orchestrator for the simplified process.
    """
    _prompt_generator = SystemPromptGenerator()
    _prompt_cache = {}  # Cache for the generated DB schema string

    def __init__(self, user_query: str):
        self.user_query = user_query
        # Initialize handlers and agents. In a real app, these might be singletons
        # or injected dependencies.
        self.llm_handler = LLMHandler()
        self.chart_builder = ChartBuilderAgent(self.llm_handler)
        self.chart_creator = ChartCreator()

    def _get_db_schema(self) -> str:
        """
        Retrieves the database schema string, using a cache to avoid
        regenerating it for every request.
        """
        db_url = settings.DB_URL
        if db_url not in self._prompt_cache:
            logger.info(f"Generating new DB schema for {db_url}")
            self._prompt_cache[db_url] = self._prompt_generator.fetch_db_schema(db_url)
        return self._prompt_cache[db_url]

    def process_query(self) -> dict:
        """
        Processes the user query to generate and create a chart.
        """
        try:
            # Step 1: Get the database schema
            db_schema = self._get_db_schema()
            if "Error" in db_schema:
                return {"error": "Could not retrieve database schema."}

            # Step 2: Use the ChartBuilderAgent to get the final payload
            # This single method call replaces the entire multi-agent chain.
            final_payload = self.chart_builder.generate_chart_config(
                user_query=self.user_query,
                db_schema=db_schema
            )

            if "error" in final_payload:
                logger.error(f"ChartBuilderAgent failed: {final_payload['error']}")
                return final_payload

            # Step 3: Create the chart in Superset
            chart_creation_result = self.chart_creator.create_chart(final_payload)

            if "error" in chart_creation_result:
                logger.error(f"ChartCreator failed: {chart_creation_result['error']}")
                return chart_creation_result

            return {
                "chart_url": chart_creation_result["url"],
                "chart_id": chart_creation_result["id"],
                "viz_type": final_payload.get("viz_type"),
            }

        except Exception as e:
            logger.critical(f"Fatal error in process_query: {e}", exc_info=True)
            return {"error": f"An unexpected error occurred: {str(e)}"}
