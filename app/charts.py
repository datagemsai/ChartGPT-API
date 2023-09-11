from typing import Optional

from app import db_charts


def get_chart(chart_id) -> Optional[dict]:
    """Get chart details for a specific chart_id"""
    chart = db_charts.document(chart_id).get()
    if chart.exists:
        return {"id": chart.id, **chart.to_dict()}
    else:
        return None
