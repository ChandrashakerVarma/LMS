# app/utils/attendance_anomaly_detector.py

def detect_anomaly(similarity, gps_score, avg_time_diff):
    score = 0

    # 1. Face similarity anomaly
    if similarity < 0.48:      # very low match
        score += 40

    # 2. GPS anomaly
    if gps_score < 0.4:        # far from office geofence
        score += 30

    # 3. Time anomaly (user normally does not check-in this early/late)
    if avg_time_diff > 60:     # 60 minutes deviation
        score += 30

    # Final risk levels
    if score >= 60:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"
