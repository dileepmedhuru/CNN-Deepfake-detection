from database import db
from datetime import datetime

class DetectionHistory(db.Model):
    """Detection History model"""
    __tablename__ = 'detection_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # 'image' or 'video'
    file_path = db.Column(db.String(500))
    prediction = db.Column(db.String(20), nullable=False)  # 'real' or 'fake'
    confidence = db.Column(db.Float, nullable=False)
    processing_time = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_path': self.file_path,
            'prediction': self.prediction,
            'confidence': round(self.confidence, 2),
            'processing_time': round(self.processing_time, 2) if self.processing_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Detection {self.file_name} - {self.prediction}>'