from psycopg2.extras import Json


def jsonify_needed_columns(record):
    """
    Wrapper for JSONB type columns.
    """
    if isinstance(record, list):
        return [jsonify_needed_columns(r) for r in record]
    elif isinstance(record, dict):
        return {
            key: Json(value) if isinstance(value, dict) else value
            for key, value in record.items()
        }
    else:
        return record
