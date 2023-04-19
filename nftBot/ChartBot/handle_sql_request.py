
from typing import List
import sqlalchemy
from dataclasses import asdict
from .base import get_sql_result, completion

extract_prompt = """Reproduce the SQL statement from the following, exactly as written:

{sql}

```sql
"""


def process_sql_requests(eng, sql_requests: List):
    results = []
    for request in sql_requests:
        q = request["question"]
        resp = completion(extract_prompt.format(sql=q))
        sql = resp  # resp.json()["choices"][0]["text"].split("```")[0]
        sql = sql.strip().strip("```")
        print(sql)
        qr = get_sql_result(eng, sql)
        request["sql_result"] = asdict(qr)
        results.append(request)
    return results
