try:
    import datetime

    from pyzbar.pyzbar import decode
    from PIL import Image
    from urllib.parse import urlparse, parse_qs
    import time
    import webuntis
    from webuntis.objects import StudentObject

    from utils import otp_login
    import pyotp
    from rich.console import Console
    from pypresence import Presence

    console = Console()

    uri: str = decode(Image.open('login_qr.png'))[0].data.decode("utf-8")
    parsed_uri = urlparse(uri)
    login_data = parse_qs(parsed_uri.query)

    totp = pyotp.TOTP(login_data["key"][0], interval=30)

    with open(".appid") as f:
        presence_id = f.read()

    pres = Presence(presence_id)
    print("Connecting")
    pres.connect()
    print("Connected")

    while True:
        with otp_login(
                scname=login_data["school"][0],
                server="https://" + login_data["url"][0],
                username=login_data["user"][0],
                token=totp.now(),
                time=int(time.time() * 1000)
        ) as session:
            session: webuntis.Session
            myself: StudentObject
            for student in session.students():
                if student.name == login_data["user"][0]:
                    myself = student
                    break

            timetable_data = []

            own_timetable = session.timetable(start=datetime.date.today(), end=datetime.date.today(), student=myself)
            for entry in own_timetable:
                try:
                    timetable_data.append({
                        "start": entry.start,
                        "end": entry.end,
                        "type": "inschool",
                        "name": "In Class",
                        "teach": entry.teachers[0]
                    })

                except:
                    timetable_data.append({
                        "start": entry.start,
                        "end": entry.end,
                        "type": "cancelled",
                        "name": "Cancelled",
                        "teach": ""
                    })

            now = {
                "end": None,
                "type": "break",
                "name": "Break"
            }

            for entry in timetable_data:
                if entry["start"] < datetime.datetime.now() < entry["end"]:
                    now = entry
                    break

            if now["end"]:
                # noinspection PyTypeChecker
                pres.update(state=now["name"], large_image="logo", small_image=now["type"], end=entry["end"].timestamp())
            else:
                pres.update(state=now["name"], large_image="logo", small_image=now["type"])


        time.sleep(10)
except Exception as e:
    print(e)
    exec(open(__file__).read())
