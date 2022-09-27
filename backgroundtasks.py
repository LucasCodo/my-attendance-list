import threading
import schedule
import time

def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

def clean_invalid_tokens(tokens:dict):
    alive = {}
    for token in tokens.values():
        if token.is_valid():
            alive.update(token)
    tokens.clear()
    tokens.update(alive)



stop_run_continuously = run_continuously()
if __name__ == "__main__":
    time.sleep(10)
    stop_run_continuously.set()
