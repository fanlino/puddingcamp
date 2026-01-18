from datetime import date, time
from typing import Annotated

from fastapi_storages import StorageFile
from sqlmodel import SQLModel, Field
from pydantic import AwareDatetime, EmailStr, AfterValidator, PlainSerializer, WithJsonSchema

from appserver.apps.calendar.enums import AttendanceStatus

# StorageFile을 문자열로 직렬화하고 JSON 스키마는 string으로 정의
StorageFileStr = Annotated[
    StorageFile,
    PlainSerializer(lambda x: str(x), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
from appserver.libs.collections.sort import deduplicate_and_sort
from pydantic import model_validator


class CalendarOut(SQLModel):
    topics: list[str]
    description: str


class CalendarDetailOut(CalendarOut):
    host_id: int
    google_calendar_id: str
    created_at: AwareDatetime
    updated_at: AwareDatetime


Topics = Annotated[list[str], AfterValidator(deduplicate_and_sort)]


class CalendarCreateIn(SQLModel):
    topics: Topics = Field(min_length=1, description="게스트와 나눌 주제들")
    description: str = Field(min_length=1, description="게스트에게 보여줄 설명")
    google_calendar_id: EmailStr = Field(description="Google Calendar ID")


class CalendarUpdateIn(SQLModel):
    topics: Topics | None = Field(
        default=None,
        min_length=1,
        description="게스트와 나눌 주제들",
    )
    description: str | None = Field(
        default=None,
        min_length=10,
        description="게스트에게 보여줄 설명",
    )
    google_calendar_id: EmailStr | None = Field(
        default=None,
        min_length=20,
        description="Google Calendar ID",
    )


def validate_weekdays(weekdays: list[int]) -> list[int]:
    weekday_range = range(7)
    for weekday in weekdays:
        if weekday not in weekday_range:
            raise ValueError(f"요일 값은 0부터 6까지의 값이어야 합니다. 현재 값: {weekday}")
    return weekdays


Weekdays = Annotated[list[int], AfterValidator(validate_weekdays)]


class TimeSlotOut(SQLModel):
    start_time: time
    end_time: time
    weekdays: list[int]
    created_at: AwareDatetime
    updated_at: AwareDatetime


class TimeSlotCreateIn(SQLModel):
    start_time: time
    end_time: time
    weekdays: Weekdays

    @model_validator(mode="after")
    def validate_weekdays(self):
        if self.start_time >= self.end_time:
            raise ValueError("시작 시간은 종료 시간보다 빨라야 합니다.")
        return self


class BookingCreateIn(SQLModel):
    when: date
    topic: str
    description: str
    time_slot_id: int


class BookingFileOut(SQLModel):
    id: int
    file: StorageFileStr

    model_config = {"arbitrary_types_allowed": True}


class BookingOut(SQLModel):
    id: int
    when: date
    topic: str
    description: str
    time_slot: TimeSlotOut
    attendance_status: AttendanceStatus
    files: list[BookingFileOut]
    created_at: AwareDatetime
    updated_at: AwareDatetime


class HostBookingStatusUpdateIn(SQLModel):
    attendance_status: AttendanceStatus


class SimpleBookingOut(SQLModel):
    when: date
    time_slot: TimeSlotOut


class HostBookingUpdateIn(SQLModel):
    when: date | None = Field(default=None, description="예약 일자")
    time_slot_id: int | None = Field(default=None, description="타임슬롯 ID")


class GuestBookingUpdateIn(SQLModel):
    topic: str | None = Field(default=None, description="예약 주제")
    description: str | None = Field(default=None, description="예약 설명")
    when: date | None = Field(default=None, description="예약 일자")
    time_slot_id: int | None = Field(default=None, description="타임슬롯 ID")
