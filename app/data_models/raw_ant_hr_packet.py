from pydantic import BaseModel
from moose_lib import Key

class raw_ant_hr_packet(BaseModel):
    device_id: Key[int]
    packet_count: int
    ant_hr_packet: list[int]