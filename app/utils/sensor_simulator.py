"""
Synthetic sensor reading generator for the Live Monitoring feature.

Why simulated: this is an academic project with no physical IoT hardware
available. Per the project guide's "real-time data" feedback, this module
stands in for a real sensor feed by periodically generating one plausible
reading per user and scoring it through the exact same inference path the
rest of the app already uses (ml/predict.py, app/utils/maintenance_rules.py).
Nothing here duplicates preprocessing or maintenance-threshold logic.

Because this consumes the identical raw feature schema as the manual
prediction form and CSV upload, swapping this generator for a real IoT
data source later (e.g. an MQTT/HTTP ingest endpoint) would not require
any change to the prediction or alerting logic below it.

Feature ranges are NOT uniform random noise. Each numeric feature is
sampled from a normal distribution using the actual mean/std observed in
data/train_cleaned.csv (the cleaned dataset the model was trained on),
clipped to that same dataset's observed min/max so generated values never
fall outside the real, historically-observed range.
"""

import random
from pathlib import Path

from ml.predict import predict_single
from app.utils.maintenance_rules import get_maintenance_recommendation

# mean/std/min/max per numeric feature, taken directly from
# data/train_cleaned.csv (see PROJECT_CONTEXT.md for the exact figures).
NUMERIC_FEATURE_STATS = {
    'temperature':        {'mean': 25.00, 'std': 11.78, 'min': 0.0,   'max': 90.0},
    'irradiance':         {'mean': 503.24, 'std': 239.67, 'min': 0.0,  'max': 1537.81},
    'humidity':           {'mean': 50.07, 'std': 28.62, 'min': 0.01,  'max': 99.995},
    'panel_age':          {'mean': 17.51, 'std': 9.84,  'min': 0.001, 'max': 35.0},
    'maintenance_count':  {'mean': 4.01,  'std': 1.95,  'min': 0.0,   'max': 15.0},
    'soiling_ratio':       {'mean': 0.699, 'std': 0.168, 'min': 0.400, 'max': 0.9999},
    'voltage':            {'mean': 15.92, 'std': 15.92, 'min': 0.0,   'max': 100.0},
    'current':            {'mean': 1.71,  'std': 1.12,  'min': 0.0,   'max': 7.32},
    'module_temperature': {'mean': 29.92, 'std': 11.83, 'min': 0.0,   'max': 65.0},
    'cloud_coverage':     {'mean': 49.85, 'std': 28.16, 'min': 0.0,   'max': 100.0},
    'wind_speed':         {'mean': 7.41,  'std': 4.32,  'min': 0.0,   'max': 15.0},
    'pressure':           {'mean': 1012.98, 'std': 10.01, 'min': 970.0, 'max': 1053.0},
}

# Real observed category values (data/train.csv), same choices already used
# by the manual prediction form in app/routes/predict.py.
STRING_ID_CHOICES = ['A1', 'B2', 'C3', 'D4']
ERROR_CODE_CHOICES = ['E00', 'E01', 'E02', 'missing']
INSTALLATION_TYPE_CHOICES = ['fixed', 'tracking', 'dual-axis', 'missing']

_MODEL_PATH = str(Path(__file__).resolve().parent.parent.parent / 'models' / 'best_model.joblib')
_DATA_PATH = str(Path(__file__).resolve().parent.parent.parent / 'data' / 'train_cleaned.csv')


def generate_synthetic_reading():
    """
    Build one plausible raw sensor reading dict, shaped exactly like the
    manual prediction form's raw input (see NUMERIC_FEATURES/CATEGORICAL_FEATURES
    in app/routes/predict.py) so it can be passed straight into predict_single().
    """
    reading = {}
    for name, stats in NUMERIC_FEATURE_STATS.items():
        value = random.gauss(stats['mean'], stats['std'])
        value = max(stats['min'], min(stats['max'], value))
        if name == 'maintenance_count':
            value = round(value)
        reading[name] = value

    reading['string_id'] = random.choice(STRING_ID_CHOICES)
    reading['error_code'] = random.choice(ERROR_CODE_CHOICES)
    reading['installation_type'] = random.choice(INSTALLATION_TYPE_CHOICES)
    return reading


def score_reading(raw_reading):
    """
    Run one raw reading through the existing inference + maintenance-rules
    path and return (efficiency, recommendation, severity).

    Deliberately reuses ml.predict.predict_single and
    maintenance_rules.get_maintenance_recommendation rather than
    reimplementing either, so this feature can never drift out of sync
    with the rest of the app's prediction/alerting behaviour.
    """
    efficiency = predict_single(raw_reading, model_path=_MODEL_PATH, data_path=_DATA_PATH)
    recommendation, severity = get_maintenance_recommendation(
        predicted_efficiency=efficiency,
        soiling_ratio=raw_reading['soiling_ratio'],
        panel_age=raw_reading['panel_age'],
    )
    return efficiency, recommendation, severity


def simulate_tick(app):
    """
    One simulation cycle: generate + score + store one reading for every
    registered user. Called on a timer by app/utils/realtime_scheduler.py.

    Scope note: Flask sessions aren't queryable from a background thread,
    so "each logged-in user's virtual panel" is implemented here as every
    registered User row, not just users with a currently-open browser tab.
    This keeps the feature simple and demo-able without a live session
    tracker, which would be out of scope for this request.
    """
    from app.models_db import db, User, SensorReading

    with app.app_context():
        users = User.query.all()
        for user in users:
            try:
                raw_reading = generate_synthetic_reading()
                efficiency, recommendation, severity = score_reading(raw_reading)

                entry = SensorReading(user_id=user.id, severity=severity)
                entry.set_input_data(raw_reading)
                entry.predicted_efficiency = efficiency
                entry.maintenance_recommendation = recommendation
                db.session.add(entry)
            except Exception as exc:
                # One user's bad reading must never stop the tick for everyone else.
                app.logger.warning(f'Sensor simulator failed for user {user.id}: {exc}')

        db.session.commit()
