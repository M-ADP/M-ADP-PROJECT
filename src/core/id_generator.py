import os
from datetime import datetime, timedelta, timezone

from sonyflake import Sonyflake


def _machine_id() -> int:
    try:
        return int(os.getenv("SONYFLAKE_MACHINE_ID", "0"))
    except ValueError:
        return 0


def _kst_midnight_today() -> datetime:
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst)
    return datetime(
        year=now_kst.year,
        month=now_kst.month,
        day=now_kst.day,
        tzinfo=kst,
    )


_generator = Sonyflake(
    machine_id=_machine_id(),
    start_time=_kst_midnight_today(),
)

def generate_sonyflake_id() -> str:
    return str(_generator.next_id())
