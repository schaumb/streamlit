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

import os

import google.auth as auth
import google.oauth2.credentials as oauth2
from google.cloud import bigquery


class BigQueryAdapter:
    # Main docs: https://cloud.google.com/python/docs/reference/bigquery/latest
    # DBAPI docs: https://cloud.google.com/python/docs/reference/bigquery/latest/google.cloud.bigquery.dbapi
    def connect(self, project, credentials, credentials_path: str) -> (bigquery.Client):
        """
        Returns the BigQuery connection & cursor used to perform queries
        """
        # TODO: Sort out main auth options - https://googleapis.dev/python/google-auth/latest/user-guide.html
        if project and credentials:
            # WIP: User Credentials option

            # Pass the OAuth2 Credentials (specifically access token) to use for this client
            oauth_credentials = oauth2.Credentials(credentials)
            Client = bigquery.Client(project=project, credentials=oauth_credentials)

        elif credentials_path:
            # WIP: Service account private key files option

            # Set the env var to the path of the JSON file containing the service account key
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            credentials, project = auth.default()
            Client = bigquery.Client(project=project, credentials=credentials)

        else:
            # WIP: Application default credentials
            credentials, project = auth.default()
            Client = bigquery.Client(project=project, credentials=credentials)

        connection = bigquery.dbapi.Connection(Client)
        cursor = connection.cursor()
        return connection, cursor

    def is_connected(self, connection: bigquery.dbapi.Connection) -> bool:
        """Test if an BigQuery connection is active"""
        try:
            # Per docs: This is a no-op, but for consistency raises an error if connection is closed
            # https://cloud.google.com/python/docs/reference/bigquery/latest/google.cloud.bigquery.dbapi.Connection#google_cloud_bigquery_dbapi_Connection_commit
            connection.commit()
            return True
        except Exception:
            return False

    def close(self, connection: bigquery.dbapi.Connection) -> None:
        """
        Close the BigQuery connection and any cursors created from it.
        """
        connection.close()
