from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, StringConstraints, FiniteFloat
from datetime import UTC,datetime
from typing import Annotated
from psycopg.errors import ForeignKeyViolation,UniqueViolation

from database import (
    device_exists,
    get_device_statistics,
    get_user_device_ids,
    get_user_statistics,
    save_device,
    save_measurement,
    save_user,
    user_exists,
)

app = FastAPI()

class Izmereniya(BaseModel):
    x: FiniteFloat
    y: FiniteFloat
    z: FiniteFloat

class UserCreate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=100,
        ),
    ]

class DeviceCreate(BaseModel):
    id: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=100,
        ),
    ]
    user_id: int = Field(gt=0)


def validate_period(
    start_at: datetime | None,
    end_at: datetime | None,
) -> None:
    if start_at is not None and start_at.utcoffset() is None:
        raise HTTPException(
            status_code=422,
            detail="У start_at нужно указать часовой пояс, например Z или +03:00",
        )

    if end_at is not None and end_at.utcoffset() is None:
        raise HTTPException(
            status_code=422,
            detail="У end_at нужно указать часовой пояс, например Z или +03:00",
        )

    if (
        start_at is not None
        and end_at is not None
        and start_at > end_at
    ):
        raise HTTPException(
            status_code=422,
            detail="Начало периода не может быть позже конца",
        )

@app.get("/", tags = ["Проверка"])
def read_root():
    return {"message:": "the service is working"}

@app.post("/devices/{device_id}/measurements", status_code=201)
def create_izmereniya(device_id: str, measurement: Izmereniya):
    measured_at = datetime.now(UTC)

    try:
        return save_measurement(
            device_id=device_id,
            measured_at=measured_at,
            x=measurement.x,
            y=measurement.y,
            z=measurement.z,
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=404,
            detail="Устройство с таким идентификатором не найдено",
        )

@app.get("/devices/{device_id}/statistics")
def read_device_statistics(
    device_id: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
):
    validate_period(start_at=start_at, end_at=end_at)

    if not device_exists(device_id=device_id):
        raise HTTPException(
            status_code=404,
            detail="Устройство с таким идентификатором не найдено",
        )

    return get_device_statistics(
        device_id=device_id,
        start_at=start_at,
        end_at=end_at,
    )

@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    return save_user(name=user.name)


@app.post("/devices", status_code=201)
def create_device(device: DeviceCreate):
    try:
        return save_device(
            device_id=device.id,
            user_id=device.user_id,
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=404,
            detail="Пользователь с таким идентификатором не найден!",
        )
    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Устройство с таким идентификатором уже существует!!",
        )


@app.get("/users/{user_id}/statistics")
def read_user_statistics(
    user_id: int,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
):
    validate_period(start_at=start_at, end_at=end_at)

    if not user_exists(user_id=user_id):
        raise HTTPException(
            status_code=404,
            detail="Пользователь с таким идентификатором не найден",
        )

    return get_user_statistics(
        user_id=user_id,
        start_at=start_at,
        end_at=end_at,
    )

@app.get("/users/{user_id}/devices/statistics")
def read_user_devices_statistics(
    user_id: int,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
):
    validate_period(start_at=start_at, end_at=end_at)

    if not user_exists(user_id=user_id):
        raise HTTPException(
            status_code=404,
            detail="Пользователь с таким идентификатором не найден",
        )

    device_ids = get_user_device_ids(user_id=user_id)

    devices_statistics = []

    for device_id in device_ids:
        statistics = get_device_statistics(
            device_id=device_id,
            start_at=start_at,
            end_at=end_at,
        )

        devices_statistics.append(statistics)

    return {
        "user_id": user_id,
        "devices": devices_statistics,
    }