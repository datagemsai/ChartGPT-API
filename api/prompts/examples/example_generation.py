# %%
from dataclasses import dataclass, asdict
import os
from typing import List, Optional

import chartgpt_client
from chartgpt_client.exceptions import ApiException

configuration = chartgpt_client.Configuration(host=os.environ["CHARTGPT_API_HOST"])
configuration.api_key["ApiKeyAuth"] = os.environ["CHARTGPT_API_KEY"]

# %%
data_sources = {
    # 'bigquery/chartgpt-staging/metaquants_nft_finance_aggregator/p2p_and_p2pool_loan_data_borrow': [
    #     # 'Perform exploratory data analysis.',
    #     'Plot the average APR for the NFTfi protocol in the past 6 months.',
    #     'Plot a bar chart of the USD lending volume for all protocols.',
    #     'Plot a stacked area chart of the USD lending volume for all protocols.',
    # ],
    'bigquery/chartgpt-staging/real_estate/usa_real_estate_listings_synthetic': [
        # 'What is the average sale duration of furnished vs. unfurnished properties over time?',
        # 'Which states offer the best value for money in terms of house size? Show this on a map.',
        # 'What is the most common feedback term for houses in New York?',
        # 'Which cities had the highest USD sale volume in 2022?',
        # 'For properties that have had more than 10 viewings, how long, on average, does it take to sell them?',
        # 'What percentage of website visits for properties with 3 bedrooms and above convert into actual property viewings?',
        # 'What combination of bedrooms and bathrooms had the highest average web visits in October 2022 in Los Angeles?',
        'Based on the number of bedrooms and the zip code, what is the average selling price of similar properties in the past 6 months?',
        'For properties listed on our website, how does the number of website visits correlate with the number of physical property viewings?',
        'Which properties have had more than 50% of their total viewings in the past 3 days, indicating a recent surge in interest?',
        'Do properties with furnishings typically have a higher number of viewings or faster sales compared to unfurnished properties?',
        'Based on zip code and the number of bedrooms, what is the best day of the week to list a property to maximize website visits?',
        'What percentage of website visits for a property convert into actual physical viewings? How does this vary by zip code or number of bedrooms?',
        'In which zip codes do we have an oversupply or undersupply of properties with a specific number of bedrooms?',
        'For properties that have had more than 10 viewings, how long, on average, does it take to sell them? Does this duration change when considering the number of bedrooms or furnishing status?',
        'For properties with feedback from viewings, what common characteristics or features are frequently mentioned as positives or negatives, and how do these feedback points correlate with the number of bedrooms or furnishings?',
        'Are there specific months or seasons where properties in certain zip codes or with a certain number of bedrooms are viewed or sold more frequently?',
    ],
    # 'bigquery/chartgpt-staging/aviation/airport_operations': [
    #     'Plot average Taxi times (before and after) for each gate',
    #     'Plot the passenger arrivals by terminal over time',
    #     'Which gates had on average the largest volume of baggage in September?',
    #     'From our historical gate usage data, which gates are most frequently delayed in turning over for incoming flights during morning rush hours (6:30 am - 9:30 am)?',
    #     'Given 2022 seasonal fluctuations, what volume of baggage can we anticipate between December 15th and December 31st?',
    # ],
    # 'bigquery/chartgpt-staging/finance/private_equity': [
    #     'Can you show me the month-over-month performance of Tech sector ETFs in my clients’ portfolios compared to the NASDAQ index over the past year?',
    #     'Given the recent hikes in interest rates, how have the bond holdings in my portfolios been impacted compared to benchmark Treasury yields?',
    #     'From our internal data, which asset class has consistently outperformed the S&P 500 for clients in the 45-55 age bracket over the last five years?',
    #     'Considering recent global macroeconomic shifts, how did emerging market equities in our portfolios perform relative to the MSCI Emerging Markets Index last quarter?',
    #     'Which clients had the highest exposure to the Energy sector during the last oil price crash, and how did their portfolios fare against the broader market?',
    #     'Using our internal transaction data, can we identify clients who have consistently adjusted their portfolio ahead of major market movements in the past two years?',
    #     'Given the projected GDP growth in Asian markets, how might the Asian-Pacific equities in our managed portfolios be impacted over the next six months?',
    #     'Analyzing the past five years, during which month do we typically see the highest volume of buy/sell transactions, and can we anticipate similar trends this year?',
    #     'How did the real estate investment trusts (REITs) in our portfolios perform during the last housing market fluctuation compared to the benchmark REIT index?',
    #     'Considering the ongoing trade discussions, how might the multinational corporations in our portfolios be affected, based on their historical sensitivity to such news?',
    # ]
}

# %%
def ask_chartgpt(question, data_source_url) -> Optional[chartgpt_client.Response]:
    with chartgpt_client.ApiClient(configuration) as api_client:
        api_instance = chartgpt_client.DefaultApi(api_client)
        try:
            api_request = chartgpt_client.Request(
                messages=[
                    {
                        "content": question,
                        "role": "user",
                    }
                ],
                output_type="any",
                data_source_url=data_source_url,
            )
            return api_instance.api_request_ask_chartgpt(api_request)
        except ApiException as e:
            print(e)
            return None
        except Exception as e:
            print(e)
            return None

# %%
import datetime

timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
generated_examples_folder = os.path.join(os.path.dirname(__file__), f"example_generation_outputs/examples_generated_{timestamp}")
os.makedirs(generated_examples_folder, exist_ok=True)

# %%
@dataclass
class GeneratedExample:
    passed: bool
    data_source_url: str
    question: str
    response_time: float
    number_of_attempts: int
    number_of_outputs: int
    number_of_errors: int
    sql_query: Optional[str]
    sample_rows: Optional[List]
    python_code: Optional[str]

# %%
import csv

examples_generated_csv = os.path.join(generated_examples_folder, f"examples_generated_{timestamp}.csv")

# Write header row
with open(examples_generated_csv, "w", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=GeneratedExample.__annotations__.keys())
    writer.writeheader()

# %%
results = []
for data_source_url, questions in data_sources.items():
    for question in questions:
        try:
            api_response = ask_chartgpt(question=question, data_source_url=data_source_url)
            
            if api_response:
                response_time = api_response.finished_at - api_response.created_at
                number_of_attempts = len(api_response.attempts)
                number_of_outputs = len(api_response.outputs)
                number_of_errors = number_of_attempts + len(api_response.errors)

                outputs: List[chartgpt_client.Output] = api_response.outputs
                # Sort outputs by index and created_at time
                outputs = sorted(outputs, key=lambda x: (x.index, x.created_at))

                # Filter outputs and find sql_query and python_code
                sql_query = None
                sample_rows = None
                python_code = None
                for output in outputs:
                    if output.type == chartgpt_client.OutputType.SQL_QUERY.value:
                        sql_query = output.value
                    elif output.type == chartgpt_client.OutputType.PANDAS_DATAFRAME.value and not sample_rows:
                        sample_rows = output.value
                    elif output.type == chartgpt_client.OutputType.PYTHON_CODE.value:
                        python_code = output.value
                
                passed = number_of_attempts < 10

                print(f"Passed: {passed}")
                print(f"Data Source: {data_source_url}")
                print(f"Question: {question}")
                print(f"Response Time: {response_time}")
                print(f"Number of Attempts: {number_of_attempts}")
                print(f"Number of Outputs: {len(outputs)}")
                print(f"Number of Errors: {number_of_errors}")
                print(f"SQL Query: {sql_query}")
                print(f"Sample Rows: {sample_rows}")
                print(f"Python Code: {python_code}")
                print()

                generated_example = GeneratedExample(
                    passed=passed,
                    data_source_url=data_source_url,
                    question=question,
                    response_time=response_time,
                    number_of_attempts=number_of_attempts,
                    number_of_outputs=number_of_outputs,
                    number_of_errors=number_of_errors,
                    sql_query=sql_query,
                    sample_rows=sample_rows,
                    python_code=python_code,
                )
                results.append(generated_example)

                with open(examples_generated_csv, "a", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=asdict(generated_example).keys())
                    writer.writerow(asdict(generated_example))
        except Exception as e:
            print(e)
            print()
            continue
# %%
# with open(examples_generated_csv, "a", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=GeneratedExample.__annotations__.keys())
#     writer.writerows([asdict(result) for result in results])

# %%
successful_results = [generated_example for generated_example in results if generated_example.passed]

# %%
examples_generated_toml = os.path.join(generated_examples_folder, f"examples_generated_{timestamp}.toml")

with open(examples_generated_toml, "w", encoding="utf-8") as f:
    for result in successful_results:
        f.write(f"[[examples]]\n")
        f.write(f"data_source_url = \"{result.data_source_url}\"\n")
        f.write(f"query = \"{result.question}\"\n")
        f.write(f"sql = \"\"\"\n")
        if result.sql_query:
            f.write(f"{result.sql_query}\n")
        f.write(f"\"\"\"\n")
        f.write(f"code = \"\"\"\n")
        if result.python_code:
            f.write(f"{result.python_code}\n")
        f.write(f"\"\"\"\n")
        f.write(f"\n")

# %%
import shutil

shutil.copyfile(
    os.path.join(os.path.dirname(__file__), "examples_generated.toml"),
    os.path.join(generated_examples_folder, "examples_input.toml")
)
