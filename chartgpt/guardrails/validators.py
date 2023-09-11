import json
import os
from typing import Any, Callable, Dict, List, Optional, Union

from google.api_core.exceptions import BadRequest
from google.cloud import bigquery
from google.oauth2 import service_account
from guardrails import Validator, register_validator
from guardrails.validators import EventDetail


@register_validator(name="bug-free-bigquery-sql", data_type="sql")
class BugFreeBigQuerySQL(Validator):
    """Validate that there are no BigQuery SQL syntactic bugs in the generated code.

    This is a very minimal implementation that uses the Pypi `sqlvalidator` package
    to check if the SQL query is valid. You can implement a custom SQL validator
    that uses a database connection to check if the query is valid.

    The `GCP_SERVICE_ACCOUNT` credentials environment variable must be set.

    - Name for `format` attribute: `bug-free-bigquery-sql`
    - Supported data types: `sql`
    - Programmatic fix: None
    """

    def __init__(
        self,
        on_fail: Optional[Callable] = None,
    ):
        super().__init__(on_fail=on_fail)
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(os.environ["GCP_SERVICE_ACCOUNT"], strict=False)
        )
        client = bigquery.Client(credentials=credentials)
        self._client = client

    def _validate_sql(self, sql: str) -> List[str]:
        """Validate the BigQuery SQL using a BigQuery dry run."""
        try:
            query_job = self._client.query(
                sql, job_config=bigquery.QueryJobConfig(dry_run=True)
            )
            errors = [err["message"] for err in query_job.errors]
        except Exception as e:
            errors = [str(e)]
        print(sql)
        print(errors)
        return errors

    def validate(self, key: str, value: Any, schema: Union[Dict, List]) -> Dict:
        errors = self._validate_sql(value)
        print(errors)
        if len(errors) > 0:
            raise EventDetail(
                key,
                value,
                schema,
                ". ".join(errors),
                None,
            )

        return schema
