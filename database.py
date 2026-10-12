from datetime import datetime
import psycopg
from settings import DATABASE_URL

def get_connection() -> psycopg.Connection:
    return psycopg.connect(DATABASE_URL)

def save_measurement(
    device_id: str,
    measured_at: datetime,
    x: float,
    y: float,
    z: float,
) -> dict:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO measurements
                    (device_id, measured_at, x, y, z)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, device_id, measured_at, x, y, z;
                """,
                (device_id, measured_at, x, y, z),
            )

            row = cursor.fetchone()

    return {
        "id": row[0],
        "device_id": row[1],
        "measured_at": row[2],
        "x": row[3],
        "y": row[4],
        "z": row[5],
    }

def get_device_statistics(
        device_id: str,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
) -> dict:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    MIN(x),
                    MAX(x),
                    COUNT(x),
                    SUM(x),
                    percentile_cont(0.5)
                        WITHIN GROUP (ORDER BY x),

                    MIN(y),
                    MAX(y),
                    COUNT(y),
                    SUM(y),
                    percentile_cont(0.5)
                        WITHIN GROUP (ORDER BY y),

                    MIN(z),
                    MAX(z),
                    COUNT(z),
                    SUM(z),
                    percentile_cont(0.5)
                        WITHIN GROUP (ORDER BY z)
                FROM measurements
                WHERE device_id = %s
                  AND (
                      %s::timestamptz IS NULL
                      OR measured_at >= %s::timestamptz
                  )
                  AND (
                      %s::timestamptz IS NULL
                      OR measured_at <= %s::timestamptz
                  );
                """,
                (device_id, start_at, start_at, end_at, end_at),
            )

            row = cursor.fetchone()

    return {
        "device_id": device_id,
        "x": {
            "min": row[0],
            "max": row[1],
            "count": row[2],
            "sum": row[3],
            "median": row[4],
        },
        "y": {
            "min": row[5],
            "max": row[6],
            "count": row[7],
            "sum": row[8],
            "median": row[9],
        },
        "z": {
            "min": row[10],
            "max": row[11],
            "count": row[12],
            "sum": row[13],
            "median": row[14],
        },
    }

def save_user(name: str) -> dict:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (name)
                VALUES (%s)
                RETURNING id, name;
                """,
                (name,),
            )
            row = cursor.fetchone()
    return {
        "id": row[0],
        "name": row[1],
    }

def save_device(device_id: str, user_id: int) -> dict:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO devices (id, user_id)
                VALUES (%s, %s)
                RETURNING id, user_id;
                """,
                (device_id, user_id),
            )

            row = cursor.fetchone()
    return {
        "id": row[0],
        "user_id": row[1],
    }

def user_exists(user_id: int)-> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM users
                    WHERE id = %s
                );
                """,
                (user_id,),
            )

            row = cursor.fetchone()

    return row[0]


def get_user_statistics(
        user_id: int,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
) -> dict:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    MIN(x),
                    MAX(x),
                    COUNT(x),
                    SUM(x),
                    percentile_cont(0.5)
                        WITHIN GROUP (ORDER BY x),

                    MIN(y),
                    MAX(y),
                    COUNT(y),
                    SUM(y),
                    percentile_cont(0.5)
                        WITHIN GROUP (ORDER BY y),

                    MIN(z),
                    MAX(z),
                    COUNT(z),
                    SUM(z),
                    percentile_cont(0.5)
                        WITHIN GROUP (ORDER BY z)
                FROM measurements
                JOIN devices ON measurements.device_id = devices.id
                WHERE devices.user_id = %s
                  AND (
                      %s::timestamptz IS NULL
                      OR measured_at >= %s::timestamptz
                  )
                  AND (
                      %s::timestamptz IS NULL
                      OR measured_at <= %s::timestamptz
                  );
                """,
                (user_id, start_at, start_at, end_at, end_at),
            )

            row = cursor.fetchone()

    return {
        "user_id": user_id,
        "x": {
            "min": row[0],
            "max": row[1],
            "count": row[2],
            "sum": row[3],
            "median": row[4],
        },
        "y": {
            "min": row[5],
            "max": row[6],
            "count": row[7],
            "sum": row[8],
            "median": row[9],
        },
        "z": {
            "min": row[10],
            "max": row[11],
            "count": row[12],
            "sum": row[13],
            "median": row[14],
        },
    }

def get_user_device_ids(user_id: int) -> list[str]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM devices
                WHERE user_id = %s
                ORDER BY id;
                """,
                (user_id,),
            )

            rows = cursor.fetchall()

    return [row[0] for row in rows]

def device_exists(device_id: str) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM devices
                    WHERE id = %s
                );
                """,
                (device_id,),
            )

            row = cursor.fetchone()

    return row[0]