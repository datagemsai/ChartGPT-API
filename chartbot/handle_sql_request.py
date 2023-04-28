
from typing import List
from dataclasses import asdict
import inspect
from chartbot.base import get_sql_result, completion

extract_prompt = """Reproduce the SQL statement from the following, exactly as written:

{sql}

```sql
"""


def process_sql_requests(eng, sql_requests: List):
    results = []
    for request in sql_requests:
        q = request["question"]
        prompt = extract_prompt.format(sql=q)
        prompt = inspect.cleandoc(prompt)
        # TODO 2023-04-24: move from prints to proper logging.
        # print("\nINPUT PROMPT TO QUERYING SQL IN process_sql_requests: \n{prompt}\n\nEND OF PROMPT")
        resp = completion(prompt)
        sql = resp  # resp.json()["choices"][0]["text"].split("```")[0]
        sql = sql.strip().strip("```")
        print(sql)
        qr = get_sql_result(eng, sql)
        request["sql_result"] = asdict(qr)
        results.append(request)
    return results
