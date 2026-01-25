import os
from datetime import datetime, timedelta, timezone
from sonyflake import Sonyflake


class IdGenerator:
    _generator: Sonyflake | None = None

    @classmethod
    def _init_generator(cls):
        if cls._generator is not None:
            return

        cls._generator = Sonyflake(
            machine_id=cls._machine_id(),
            start_time=cls._kst_midnight_today(),
        )

    @staticmethod
    def _machine_id() -> int:
        try:
            return int(os.getenv("SONYFLAKE_MACHINE_ID", "0"))
        except ValueError:
            return 0

    @staticmethod
    def _kst_midnight_today() -> datetime:
        kst = timezone(timedelta(hours=9))
        now_kst = datetime.now(kst)
        return datetime(
            year=now_kst.year,
            month=now_kst.month,
            day=now_kst.day,
            tzinfo=kst,
        )

    @classmethod
    def generate_sonyflake_id(cls) -> str:
        cls._init_generator()
        return str(cls._generator.next_id())
