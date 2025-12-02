"""
Attendance Anomaly Detection System
Adapted for your exact Attendance model structure
Uses Isolation Forest to detect unusual attendance patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Optional
from sqlalchemy.orm import Session


class AttendanceAnomalyDetector:
    """
    Detects anomalies in employee attendance patterns using:
    1. Isolation Forest (unsupervised ML)
    2. Statistical thresholds
    """
    
    def __init__(self, contamination: float = 0.1):
        """
        Args:
            contamination: Expected proportion of anomalies (0.1 = 10%)
        """
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.is_fitted = False
        self.user_stats = None
        
    def extract_features(self, attendance_records: List[Dict]) -> pd.DataFrame:
        """
        Extract features from YOUR attendance records for anomaly detection
        
        Features extracted:
        - Punch-in/out times (minutes from midnight)
        - Duration worked
        - Day of week patterns
        - Status patterns (Full Day, Half Day, Absent)
        """
        df = pd.DataFrame(attendance_records)
        
        if df.empty:
            return pd.DataFrame()
        
        # Convert to datetime
        df['punch_in'] = pd.to_datetime(df['punch_in'])
        df['punch_out'] = pd.to_datetime(df['punch_out'])
        df['attendance_date'] = pd.to_datetime(df['attendance_date'])
        
        # Feature engineering
        features = pd.DataFrame()
        
        # 1. Punch-in time (minutes from midnight)
        features['punch_in_minutes'] = (
            df['punch_in'].dt.hour * 60 + 
            df['punch_in'].dt.minute
        )
        
        # 2. Punch-out time (minutes from midnight)
        features['punch_out_minutes'] = (
            df['punch_out'].dt.hour * 60 + 
            df['punch_out'].dt.minute
        )
        
        # 3. Total worked minutes (from your field)
        features['total_worked_minutes'] = df['total_worked_minutes'].fillna(0)
        
        # 4. Day of week (0=Monday, 6=Sunday)
        features['day_of_week'] = df['attendance_date'].dt.dayofweek
        
        # 5. Is weekend
        features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
        
        # 6. Status encoding (Full Day=2, Half Day=1, Absent/Pending=0)
        status_map = {'Full Day': 2, 'Half Day': 1, 'Absent': 0, 'Pending': 0}
        features['status_encoded'] = df['status'].map(status_map).fillna(0)
        
        # 7. User-level aggregations
        features['user_id'] = df['user_id']
        features['attendance_date'] = df['attendance_date']
        features['id'] = df['id']
        
        return features
    
    def compute_user_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute per-user statistics for anomaly context
        """
        user_stats = df.groupby('user_id').agg({
            'punch_in_minutes': ['mean', 'std', 'min', 'max'],
            'punch_out_minutes': ['mean', 'std'],
            'total_worked_minutes': ['mean', 'std', 'min', 'max'],
            'status_encoded': ['mean']
        }).reset_index()
        
        user_stats.columns = [
            'user_id',
            'avg_punch_in', 'std_punch_in', 'min_punch_in', 'max_punch_in',
            'avg_punch_out', 'std_punch_out',
            'avg_worked_minutes', 'std_worked_minutes', 'min_worked_minutes', 'max_worked_minutes',
            'avg_status'
        ]
        
        return user_stats
    
    def calculate_anomaly_features(self, features: pd.DataFrame, 
                                   user_stats: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate deviation-based features for each attendance record
        """
        # Merge with user statistics
        features = features.merge(user_stats, on='user_id', how='left')
        
        # Calculate deviations
        features['punch_in_deviation'] = (
            (features['punch_in_minutes'] - features['avg_punch_in']) / 
            (features['std_punch_in'] + 1e-6)  # Avoid division by zero
        )
        
        features['worked_minutes_deviation'] = (
            (features['total_worked_minutes'] - features['avg_worked_minutes']) / 
            (features['std_worked_minutes'] + 1e-6)
        )
        
        # Binary flags
        features['is_very_early'] = (
            features['punch_in_minutes'] < features['min_punch_in'] - 30
        ).astype(int)
        
        features['is_very_late'] = (
            features['punch_in_minutes'] > features['max_punch_in'] + 30
        ).astype(int)
        
        features['is_short_duration'] = (
            features['total_worked_minutes'] < features['avg_worked_minutes'] * 0.7
        ).astype(int)
        
        features['is_long_duration'] = (
            features['total_worked_minutes'] > features['avg_worked_minutes'] * 1.3
        ).astype(int)
        
        return features
    
    def fit(self, attendance_records: List[Dict]) -> None:
        """
        Train the anomaly detection model on historical data
        """
        features_df = self.extract_features(attendance_records)
        
        if features_df.empty or len(features_df) < 10:
            raise ValueError("Need at least 10 records to train anomaly detector")
        
        # Compute user statistics
        user_stats = self.compute_user_statistics(features_df)
        
        # Calculate anomaly features
        features_df = self.calculate_anomaly_features(features_df, user_stats)
        
        # Select features for model
        model_features = [
            'punch_in_deviation',
            'worked_minutes_deviation',
            'day_of_week',
            'is_weekend',
            'is_very_early',
            'is_very_late',
            'is_short_duration',
            'is_long_duration',
            'status_encoded'
        ]
        
        X = features_df[model_features].fillna(0)
        
        # Standardize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.model.fit(X_scaled)
        self.is_fitted = True
        self.user_stats = user_stats
        
    def predict_anomalies(self, attendance_records: List[Dict]) -> List[Dict]:
        """
        Detect anomalies in attendance records
        
        Returns:
            List of dicts with anomaly information
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        features_df = self.extract_features(attendance_records)
        
        if features_df.empty:
            return []
        
        # Calculate anomaly features
        features_df = self.calculate_anomaly_features(features_df, self.user_stats)
        
        # Select features for model
        model_features = [
            'punch_in_deviation',
            'worked_minutes_deviation',
            'day_of_week',
            'is_weekend',
            'is_very_early',
            'is_very_late',
            'is_short_duration',
            'is_long_duration',
            'status_encoded'
        ]
        
        X = features_df[model_features].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Predict anomalies (-1 = anomaly, 1 = normal)
        predictions = self.model.predict(X_scaled)
        anomaly_scores = self.model.score_samples(X_scaled)  # Lower = more anomalous
        
        # Compile results
        results = []
        for idx, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
            if pred == -1:  # Anomaly detected
                record = attendance_records[idx]
                anomaly_info = {
                    'attendance_id': record.get('id'),
                    'user_id': record['user_id'],
                    'attendance_date': str(record['attendance_date']),
                    'is_anomaly': True,
                    'anomaly_score': float(score),
                    'severity': self._calculate_severity(score),
                    'reasons': self._identify_reasons(features_df.iloc[idx]),
                    'details': {
                        'punch_in': str(record['punch_in']),
                        'punch_out': str(record['punch_out']),
                        'total_worked_minutes': int(record.get('total_worked_minutes', 0)),
                        'status': record.get('status', 'Unknown'),
                        'expected_punch_in': float(features_df.iloc[idx]['avg_punch_in']),
                        'expected_worked_minutes': float(features_df.iloc[idx]['avg_worked_minutes'])
                    }
                }
                results.append(anomaly_info)
        
        return results
    
    def _calculate_severity(self, score: float) -> str:
        """
        Calculate severity based on anomaly score
        Lower scores = more severe anomalies
        """
        if score < -0.5:
            return 'high'
        elif score < -0.3:
            return 'medium'
        else:
            return 'low'
    
    def _identify_reasons(self, feature_row: pd.Series) -> List[str]:
        """
        Identify specific reasons for anomaly
        """
        reasons = []
        
        if feature_row['is_very_late']:
            late_minutes = feature_row['punch_in_minutes'] - feature_row['avg_punch_in']
            reasons.append(f"Punched in {int(late_minutes)} minutes late")
        
        if feature_row['is_very_early']:
            early_minutes = feature_row['avg_punch_in'] - feature_row['punch_in_minutes']
            reasons.append(f"Punched in {int(early_minutes)} minutes early")
        
        if feature_row['is_short_duration']:
            duration_diff = feature_row['avg_worked_minutes'] - feature_row['total_worked_minutes']
            reasons.append(f"Worked {int(duration_diff)} minutes less than usual")
        
        if feature_row['is_long_duration']:
            duration_diff = feature_row['total_worked_minutes'] - feature_row['avg_worked_minutes']
            reasons.append(f"Worked {int(duration_diff)} minutes more than usual")
        
        if abs(feature_row['punch_in_deviation']) > 2:
            reasons.append("Unusual punch-in time pattern")
        
        if feature_row['is_weekend']:
            reasons.append("Weekend attendance (unusual)")
        
        if feature_row['status_encoded'] == 0:
            reasons.append("Absent or Pending status")
        
        return reasons if reasons else ['General pattern deviation']


# Global storage for trained models (per organization)
# In production, use Redis or database
_trained_models = {}


def get_or_train_model(db: Session, organization_id: int, days_back: int = 90) -> AttendanceAnomalyDetector:
    """
    Get trained model for an organization, or train a new one if not exists
    """
    from app.models.attendance_m import Attendance
    from app.models.user_m import User
    
    model_key = f"org_{organization_id}"
    
    # Return cached model if exists
    if model_key in _trained_models:
        return _trained_models[model_key]
    
    # Train new model
    cutoff_date = datetime.now().date() - timedelta(days=days_back)
    
    records = db.query(Attendance).filter(
        Attendance.attendance_date >= cutoff_date
    ).all()
    
    if len(records) < 10:
        raise ValueError(f"Insufficient data for training. Need at least 10 records, found {len(records)}")
    
    # Convert to dict
    attendance_dicts = [
        {
            'id': r.id,
            'user_id': r.user_id,
            'attendance_date': r.attendance_date,
            'punch_in': r.punch_in,
            'punch_out': r.punch_out,
            'total_worked_minutes': r.total_worked_minutes,
            'status': r.status
        }
        for r in records
    ]
    
    # Train model
    detector = AttendanceAnomalyDetector(contamination=0.1)
    detector.fit(attendance_dicts)
    
    # Cache it
    _trained_models[model_key] = detector
    
    return detector