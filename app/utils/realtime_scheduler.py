"""
Background scheduler for the simulated real-time sensor feed.

--------------------------------------------------------------------------
Guarding against duplicate schedulers (see requirement in the feature spec)
--------------------------------------------------------------------------
A naive `scheduler.start()` call inside create_app() would run twice in two
situations this project can hit:

1. Local dev with the Werkzeug debug reloader: Flask's debug server forks a
   parent "reloader" process plus a child process that serves requests.
   Both processes import and call create_app(). run.py already guards its
   own browser-auto-open the same way, so this module reuses that exact
   pattern: skip starting the scheduler unless WERKZEUG_RUN_MAIN == 'true'
   (i.e. we are the real serving child), or debug mode is off entirely.

2. Multiple gunicorn workers in production: today's render.yaml starts
   gunicorn with no `-w` flag, so it runs a single worker and this isn't
   currently an issue. But if a worker count is ever added later, each
   worker process would otherwise start its own copy of the scheduler,
   generating duplicate sensor readings per tick. To guard against that
   regardless of worker count, this module takes an OS-level, cross-process
   lock: it atomically creates a lock file under the Flask instance folder
   using O_CREAT|O_EXCL (fails if the file already exists). Only the first
   process/worker to win that race actually starts the scheduler; every
   other worker sees the lock already taken and skips silently. The lock
   file is removed on normal process exit via atexit. If a worker crashes
   without cleanup, the stale lock simply means the simulator won't restart
   until the lock file is removed manually — an acceptable tradeoff for a
   simulated demo feature, and not a correctness issue for the rest of the
   app.
--------------------------------------------------------------------------
"""

import atexit
import os

from apscheduler.schedulers.background import BackgroundScheduler

from app.utils.sensor_simulator import simulate_tick

_LOCK_FILENAME = '.sensor_scheduler.lock'


def _acquire_singleton_lock(app):
    """Return True if this process won the cross-process scheduler lock."""
    lock_path = os.path.join(app.instance_path, _LOCK_FILENAME)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
    except FileExistsError:
        return False

    def _release():
        try:
            os.remove(lock_path)
        except OSError:
            pass

    atexit.register(_release)
    return True


def start_scheduler(app):
    """
    Start the sensor-simulator background job for this Flask app, unless
    disabled or already running elsewhere (see module docstring).
    """
    if not app.config.get('ENABLE_SENSOR_SIMULATOR', True):
        return None

    # Dev-reloader guard (matches run.py's own browser-auto-open guard).
    if app.debug and os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return None

    # Cross-process/multi-worker guard.
    if not _acquire_singleton_lock(app):
        return None

    interval_seconds = app.config.get('SENSOR_SIM_INTERVAL_SECONDS', 10)

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        func=lambda: simulate_tick(app),
        trigger='interval',
        seconds=interval_seconds,
        id='sensor_simulator',
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait=False))

    app.extensions = getattr(app, 'extensions', {})
    app.extensions['sensor_scheduler'] = scheduler
    return scheduler
