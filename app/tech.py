from datetime import datetime, UTC


works_time = datetime.now(UTC)


def start_works(date: str) -> bool:
    global works_time
    try:
        works_time = datetime.strptime(date, "%d:%m:%Y.%H:%M:%S").astimezone(UTC)
    except ValueError:
        works_time = datetime.now(UTC)
        return False
    return True


def is_tech_works() -> bool:
    return works_time > datetime.now(UTC)


def create_tech_works(date: str) -> bool:
    global works_time
    try:
        works_time = datetime.strptime(date, "%d:%m:%Y.%H:%M:%S").astimezone(UTC)
    except ValueError:
        return False
    return True


def change_date_tech_works(date: str) -> bool:
    global works_time
    save_time = works_time
    try:
        works_time = datetime.strptime(date, "%d:%m:%Y.%H:%M:%S").astimezone(UTC)
    except ValueError:
        works_time = save_time
        return False
    return True


def end_tech_works() -> bool:
    global works_time
    works_time = datetime.now(UTC)
    return True
