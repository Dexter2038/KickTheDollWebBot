from uuid import uuid4


def generate_room_id() -> str:
    return str(uuid4())
