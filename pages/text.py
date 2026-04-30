from datetime import datetime
from zoneinfo import ZoneInfo

npt = "Asia/Kathmandu"
dt = datetime.now(ZoneInfo(npt))
print(dt.isoformat())