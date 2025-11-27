
SHORTCUTS_TABLE_NAME = "user_shortcuts"

CREATE_SHORTCUTS_TABLE_SQL = f"""
    CREATE TABLE IF NOT EXISTS {SHORTCUTS_TABLE_NAME} (
        user_id BIGINT NOT NULL,
        command VARCHAR(255) NOT NULL,
        city VARCHAR(255) NOT NULL,
        created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, command)
    )
"""

SELECT_SHORTCUTS_SQL = f"""
    SELECT command, city
    FROM {SHORTCUTS_TABLE_NAME}
    WHERE user_id = %s
    ORDER BY created_at DESC, command ASC
"""

UPSERT_SHORTCUTS_SQL = f"""
    INSERT INTO {SHORTCUTS_TABLE_NAME} (user_id, command, city)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE
        city = VALUES(city),
        created_at = CURRENT_TIMESTAMP
"""
