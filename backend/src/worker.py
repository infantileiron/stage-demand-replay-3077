import logging
import time
from pathlib import Path
from src.utils.database import init_db
from src.utils.queue import dequeue
from src.services.run import process
from src.services.schedule import run_due

logging.basicConfig(level=logging.INFO)

def main():
    init_db()
    while True:
        Path("/tmp/stage-worker-heartbeat").touch()
        try:
            run_due()
            ident=dequeue()
            if ident is not None: process(ident)
        except Exception:
            logging.exception("Worker queue error; retrying")
            time.sleep(2)

if __name__=="__main__": main()
