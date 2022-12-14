# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import google.cloud.bigquery as bigquery
import pandas as pd
from google.oauth2 import service_account

from streamlit.runtime.connection import register_data_type

# Main docs: https://cloud.google.com/python/docs/reference/bigquery/latest
# Auth docs: https://googleapis.dev/python/google-auth/latest/user-guide.html


class BigQueryAdapter:
    def __init__(self, st):
        st.runtime.connection.register_data_type(
            "google.cloud.bigquery.job.query.QueryJob",
            "pandas.core.frame.DataFrame",
            self.convert_to_dataframe,
        )

    def connect(self, credentials=None) -> bigquery.client.Client:
        """
        Returns the BigQuery connection & cursor used to perform queries
        """
        creds = service_account.Credentials.from_service_account_info(credentials)
        client = bigquery.Client(credentials=creds)

        return client

    def is_connected(self, client: bigquery.client.Client) -> bool:
        """Test if an BigQuery connection is active"""
        # BigQuery client will always make a connection even if closed.
        # See https://cloud.google.com/python/docs/reference/bigquery/latest/google.cloud.bigquery.client.Client#google_cloud_bigquery_client_Client_close
        return True

    def close(self, client: bigquery.client.Client) -> None:
        """
        Close the BigQuery connection and any cursors created from it.
        """
        client.close()

    def convert_to_dataframe(self, output) -> pd.DataFrame:
        return output.to_dataframe()
