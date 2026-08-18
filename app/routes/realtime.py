"""
Live Monitoring routes: the simulated real-time page plus its two small
JSON polling endpoints.

  GET /live-monitor              — page; marks the user's unread alerts read
  GET /api/live-monitor/feed     — JSON for the page's own chart/panel/log polling
  GET /api/alerts/unread-count   — tiny JSON for the navbar badge, polled from
                                    every authenticated page

Badge-reset choice (documented per the feature spec's "pick the simpler
one" note): the unread badge clears when the user visits /live-monitor,
not via a separate explicit-dismiss control. Only warning/critical
severity readings count as "alerts" for the badge and the alerts log;
'ok' readings are stored for the chart but never counted as alerts.
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

from app.models_db import db, SensorReading

realtime_bp = Blueprint('realtime', __name__)

ALERT_SEVERITIES = ('warning', 'critical')
CHART_HISTORY_LIMIT = 30
ALERT_LOG_LIMIT = 10


@realtime_bp.route('/live-monitor')
@login_required
def live_monitor():
    """
    Live Monitoring page. Visiting this page marks all of the current
    user's unread alerts as read, clearing the navbar badge.
    """
    (SensorReading.query
        .filter_by(user_id=current_user.id, is_read=False)
        .filter(SensorReading.severity.in_(ALERT_SEVERITIES))
        .update({'is_read': True}, synchronize_session=False))
    db.session.commit()

    return render_template('live_monitor.html')


def _serialize_reading(reading):
    return {
        'id': reading.id,
        'created_at': reading.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'predicted_efficiency': round(reading.predicted_efficiency, 4),
        'severity': reading.severity,
        'maintenance_recommendation': reading.maintenance_recommendation,
        'is_read': reading.is_read,
    }


@realtime_bp.route('/api/live-monitor/feed')
@login_required
def api_feed():
    """
    JSON feed powering the Live Monitoring page: recent readings for the
    chart, the single latest reading, and a short recent-alerts log.
    """
    recent = (SensorReading.query
              .filter_by(user_id=current_user.id)
              .order_by(SensorReading.created_at.desc())
              .limit(CHART_HISTORY_LIMIT)
              .all())
    recent = list(reversed(recent))  # chronological order for the chart

    latest = recent[-1] if recent else None

    recent_alerts = (SensorReading.query
                      .filter_by(user_id=current_user.id)
                      .filter(SensorReading.severity.in_(ALERT_SEVERITIES))
                      .order_by(SensorReading.created_at.desc())
                      .limit(ALERT_LOG_LIMIT)
                      .all())

    return jsonify({
        'readings': [_serialize_reading(r) for r in recent],
        'latest': _serialize_reading(latest) if latest else None,
        'alerts': [_serialize_reading(a) for a in recent_alerts],
    })


@realtime_bp.route('/api/alerts/unread-count')
@login_required
def api_unread_count():
    """
    Tiny JSON endpoint for the navbar badge (polled from every authenticated
    page). Returns the unread alert count and the highest severity among
    them, so the badge can be colored amber (warning-only) or red (any
    critical present).
    """
    unread = (SensorReading.query
              .filter_by(user_id=current_user.id, is_read=False)
              .filter(SensorReading.severity.in_(ALERT_SEVERITIES))
              .all())

    count = len(unread)
    max_severity = 'critical' if any(r.severity == 'critical' for r in unread) else (
        'warning' if count else None
    )

    return jsonify({'count': count, 'severity': max_severity})
