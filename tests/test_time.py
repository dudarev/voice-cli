from datetime import datetime

from main import is_between, fromisoformat


def test_fromisoformat():
    assert fromisoformat("2023-03-05T23:45") == datetime(2023, 3, 5, 23, 45, 0)
    assert fromisoformat("2023-03-05T23:45", end_of_date_for_date=True) == datetime(
        2023, 3, 5, 23, 45, 0
    )
    assert fromisoformat("2023-03-05") == datetime(2023, 3, 5)
    assert fromisoformat("2023-03-05", end_of_date_for_date=True) == datetime(
        2023, 3, 6
    )


def test_is_between():
    dt = datetime(2023, 3, 5, 14, 18, 0)

    dt_1 = datetime(2023, 3, 4, 0, 0, 0)
    dt_2 = datetime(2023, 3, 5, 0, 0, 0)
    dt_3 = datetime(2023, 3, 5, 14, 17, 50)
    # dt is here
    dt_4 = datetime(2023, 3, 6, 0, 0, 0)

    assert is_between(dt_2, dt_4, dt) == True
    assert is_between(None, dt_4, dt) == True
    assert is_between(dt_2, None, dt) == True
    assert is_between(None, None, dt) == True
    assert is_between(dt_2, dt_2, dt) == False
    assert is_between(dt_2, dt_1, dt) == False
    assert is_between(dt_2, dt_3, dt) == False
