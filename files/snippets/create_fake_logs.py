# Uses low-level SQL to create many changelogs (50M by default)
# flake8: noqa

from itertools import batched

entry = ("changelog", "content", "admin", vs.get_time())
query = "INSERT INTO changelog (type, content, author, time) VALUES (?, ?, ?, ?)"
batch_size = vs.database["transactions"]["batch_size"]
log_size = 50_000_000

env.log("info", f"Starting to create Fake Changelogs ({log_size} logs)")

with env.timer("Create Fake Changelogs"):
    changelogs = (entry for _ in range(log_size))
    cursor = db.session.connection().connection.cursor()
    for batch in batched(changelogs, batch_size):
        cursor.executemany(query, batch)
    db.session.commit()
