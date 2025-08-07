from sqlalchemy import create_engine, inspect, text
import requests
from django.conf import settings
# from ...dashboard_app import config
# import dashboard_app.config as config  #  Import global token
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker
import json

class SystemPromptGenerator:
    def __init__(self):
        pass
        # self.superset_url = settings.SUPERSET_URL
        # self.headers = {"Authorization": f"Bearer {config.SUPERSET_ACCESS_TOKEN}", "Content-Type": "application/json"}

    def _fetch_superset_metadata(self)->str:
        """
        Retrieves Superset metadata including available datasets (without adding new ones).
        """
        ids = {"actors" : 24,
               "store" : 41,
               "address" : 25,
               "category" : 26,
               "city" : 29,
               "country" : 30,
               "customer" : 31,
               "film_actor" : 33,
               "film_category" : 34,
               "inventory" : 35,
               "language" : 36,
               "rental" : 39,
               "staff" : 40,
               "payment" : 38,
               "film" : 32,
               }
        s = ''
        for k, v in ids.items():
            s += f"Table name: {k}, Datasource id: {v}"
        return s
        # superset_info = []
        # # breakpoint()
        # superset_url = "http://localhost:5000"
        # login_url = f"{superset_url}/api/v1/security/login"

        # payload = {
        #     "username": "q",
        #     "password": "456",
        #     "provider": "db"
        # }
        # headers = {"Content-Type": "application/json"}
        # response = requests.post(login_url, json=payload, headers=headers)

        # if response.status_code == 200:
        #     access_token = response.json().get("access_token")
        #     # print("Access Token:", access_token)
        # else:
        #     return ("Failed to get access token:", response.text)

        # headers = {"Authorization": f"Bearer {access_token}"}
        # datasource_url = f"{superset_url}/api/v1/dataset/"

        # response = requests.get(datasource_url, headers=headers)

        # if response.status_code == 200:
        #     datasets = response.json()
        #     for dataset in datasets.get("result", []):
        #         superset_info.append(f"ID: {dataset['id']}, Name: {dataset['table_name']}, Type: {dataset['datasource_type']}")
        # else:
        #     return ("Failed to get datasource:", response.text)
        # try:
        #     response = requests.get(f"{self.superset_url}/api/v1/dataset/", headers=self.headers)
            
        #     if response.status_code != 200:
        #         return f"Superset API Error: {response.json()}"

        #     datasets = response.json().get("result", [])
        #     superset_metadata = "Available Superset Datasets:\n"

        #     for dataset in datasets:
        #         table_name = dataset.get("table_name", "Unknown Table")
        #         datasource_id = dataset.get("id")
        #         superset_metadata += f"- {table_name} (Datasource ID: {datasource_id})\n"

        #     return superset_metadata

        # except requests.exceptions.RequestException as e:
        #     return f"Superset API Connection Error: {str(e)}"

    def _fetch_db_schema(self, db_url:str)->str:
        """
        Retrieves Superset metadata including available datasets and their details.

        :return: A formatted string containing Superset datasource IDs and table mappings.
        """
        engine = create_engine(db_url)
        metadata = MetaData()
        metadata.reflect(bind=engine)
        inspector = inspect(engine)
        
        db_info = []
        db_info.append("Database Metadata:")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Tables & Columns
        for table_name in inspector.get_table_names():
            db_info.append(f"Table: {table_name}")
            columns = inspector.get_columns(table_name)
            for col in columns:
                db_info.append(f"  Column: {col['name']} ({col['type']})")
            
            # Primary Key
            pk = inspector.get_pk_constraint(table_name)
            if pk['constrained_columns']:
                db_info.append(f"  Primary Key: {pk['constrained_columns']}")
            
            # Foreign Keys
            fks = inspector.get_foreign_keys(table_name)
            for fk in fks:
                db_info.append(f"  Foreign Key: {fk['constrained_columns']} -> {fk['referred_table']}({fk['referred_columns']})")
            
            db_info.append("Table Row Counts & Sample Data:")
            row_count = session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            db_info.append(f"  {table_name}: {row_count} rows")
            result = session.execute(text(f"SELECT * FROM {table_name} LIMIT 1"))
            sample_data = result.fetchall()  # Get all rows from the query result
            if sample_data:
                sample_row = sample_data[0]  # Get the first row
                db_info.append(f"    Sample Row: {sample_row}")
            else:
                db_info.append(f"    No sample data available.")
        session.close()
            # Indexes
            # indexes = inspector.get_indexes(table_name)
            # for index in indexes:
            #     db_info.append(f"  Index: {index['name']} on {index['column_names']}")
            
            # Constraints
            # constraints = inspector.get_unique_constraints(table_name)
            # for constraint in constraints:
            #     db_info.append(f"  Unique Constraint: {constraint['column_names']}")                
        
        # Views
        # views = inspector.get_view_names()
        # if views:
        #     db_info.append("\nViews:")
        #     for view in views:
        #         db_info.append(f"  {view}")
        
        # Stored Procedures & Functions (if supported)
        # try:
        #     procedures = inspector.get_procedures()
        #     if procedures:
        #         db_info.append("\nStored Procedures & Functions:")
        #         for proc in procedures:
        #             db_info.append(f"  {proc['name']}")
        # except NotImplementedError:
        #     db_info.append("\nStored Procedures & Functions not supported by this dialect.")
        
        # Triggers (if available)
        # try:
        #     triggers = inspector.get_triggers()
        #     if triggers:
        #         db_info.append("\nTriggers:")
        #         for trigger in triggers:
        #             db_info.append(f"  {trigger}")
        # except NotImplementedError:
        #     db_info.append("\nTriggers not supported by this dialect.")
        
        return "".join(db_info)

    # Example Usage:
    # print(fetch_database_info("sqlite:///example.db"))


    def generate_prompt(self, db_url:str)->str:
        """
        Generates the final system prompt for the LLM, including DB schema and Superset metadata.

        :return: A formatted system prompt string."""
        params = {"slice_name": "Number of Actors with 'A' in Name","viz_type": "big_number_total","datasource_id": 25,"datasource_type": "table","params": "{ \"datasource\": \"25__table\", \"viz_type\": \"big_number_total\", \"metric\": { \"expressionType\": \"SIMPLE\", \"column\": { \"column_name\": \"actor_id\" }, \"aggregate\": \"COUNT\", \"label\": \"Total Actors\" }, \"adhoc_filters\": [ { \"clause\": \"WHERE\", \"expressionType\": \"SIMPLE\", \"subject\": \"first_name\", \"operator\": \"ILIKE\", \"comparator\": \"%A%\" } ], \"header_font_size\": 0.4, \"subheader_font_size\": 0.15, \"y_axis_format\": \"SMART_NUMBER\", \"time_format\": \"smart_date\", \"extra_form_data\": {}, \"dashboards\": [] }"}
        db_schema = self._fetch_db_schema(db_url)
        superset_metadata = self._fetch_superset_metadata()
        prompt =  ("""Using the given database schema and Superset metadata, generate only the params and query_context sections required for creating a chart in Apache Superset.  
            ### Database Schema:
            {db_schema}  
            ### Superset Metadata:
            {superset_metadata}  
            ### Instructions:
            - Do not select Pie chart.
            - Select the **appropriate chart type** based on the user's query.  
            - Ensure the chart is **fully configured** for clear visualization. If the user does not specify certain elements, include them automatically to make the chart presentable.  
            - Define the following **key elements** for the chart:
            - **Chart Type**: Choose the best visualization type based on the query.  
            - **Colors**: Set a visually distinct and meaningful color scheme.  
            - **Title & Labels**: Add a clear title and labels for axes.  
            - **Axes & Grid Lines**: Configure axes properly and enable grid lines if applicable.  
            - **Annotations & Tooltips**: If relevant, include annotations and tooltips for better insights.  
            - **Legend**: Enable and properly position the legend if needed.  
            - **Formatting**: Ensure numerical values, percentages, and dates are formatted properly.  
            - **Additional Enhancements**: If any crucial visualization settings are missing, **add them automatically** to improve the chart's clarity and effectiveness.  

            Your output must strictly contain **only** the JSON object required for the API request, formatted correctly with the required params and query_context sections. **Do not include any explanations or extra text.**
            ### **Example Input & Output**
            #### **User Query:**  
            *"Give me the number count of actors with 'A' in their name"*

            #### **Expected JSON Output:**
            {params_json}
            """.format(db_schema=db_schema, superset_metadata=superset_metadata, params_json=json.dumps(params))
        )


        return prompt
