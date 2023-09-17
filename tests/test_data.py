from api.utils import get_tables_summary
from api.connectors.bigquery import bigquery_client


def test_tables_summary():
    tables_summary = get_tables_summary(
        client=bigquery_client,
    )
    assert tables_summary

    tables_summary = get_tables_summary(
        client=bigquery_client,
        data_source_url="bigquery/chartgpt-staging/metaquants_nft_finance_aggregator",
    )
    assert tables_summary

    tables_summary = get_tables_summary(
        client=bigquery_client,
        data_source_url="bigquery/chartgpt-staging/metaquants_nft_finance_aggregator/p2p_and_p2pool_loan_data_borrow",
    )
    assert tables_summary
