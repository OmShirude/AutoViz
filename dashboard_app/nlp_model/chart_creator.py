import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class ChartCreator:
    """
    Handles all interactions with the Apache Superset API.
    """
    def __init__(self):
        """
        Initializes the Chart Creator by authenticating with Superset.
        Credentials should be stored securely in Django settings, not hardcoded.
        """
        self.superset_url = settings.SUPERSET_URL
        self.headers = self._get_auth_headers()

    def _get_auth_headers(self) -> dict:
        """
        Authenticates with Superset and returns the necessary auth headers.
        This method can be extended to handle token refresh logic.
        """
        login_url = f"{self.superset_url}/api/v1/security/login"
        payload = {
            "username": settings.SUPERSET_USERNAME,
            "password": settings.SUPERSET_PASSWORD,
            "provider": "db"
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(login_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            
            access_token = response.json().get("access_token")
            if not access_token:
                logger.error("Authentication successful but no access token received from Superset.")
                return {}
            
            return {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        except requests.exceptions.RequestException as e:
            logger.critical(f"Failed to authenticate with Superset API at {login_url}: {e}")
            return {}

    def create_chart(self, chart_payload: dict) -> dict:
        """
        Creates a chart in Superset using the provided payload.

        :param chart_payload: A dictionary containing the full chart configuration.
        :return: A dictionary with the chart URL and ID, or an error message.
        """
        if not self.headers:
            return {"error": "Cannot create chart: Superset authentication failed."}

        create_url = f"{self.superset_url}/api/v1/chart/"
        
        try:
            response = requests.post(create_url, json=chart_payload, headers=self.headers, timeout=15)
            
            if response.status_code == 201:
                chart_id = response.json().get("id")
                chart_url = f"{self.superset_url}/superset/explore/?slice_id={chart_id}"
                logger.info(f"Successfully created chart {chart_id}")
                return {"url": chart_url, "id": chart_id}
            else:
                error_details = response.json().get("message", response.text)
                logger.error(f"Failed to create chart. Status: {response.status_code}. Details: {error_details}")
                return {"error": f"Superset API Error: {error_details}"}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to create chart failed: {e}")
            return {"error": f"Failed to connect to Superset: {str(e)}"}
