"""
Progress Tracking module for Synapse AI Tutor.
Stores and retrieves student progress data using JSON.
All tracking is topic-specific.
"""

import json
import os
from datetime import datetime

PROGRESS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "progress.json")


def _load_progress() -> dict:
    """Load progress data from JSON file."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_progress(data: dict):
    """Save progress data to JSON file."""
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_user_progress(username: str) -> dict:
    """
    Get all progress data for a specific user.
    
    Args:
        username: The username
        
    Returns:
        Dictionary of topic-specific progress data
    """
    data = _load_progress()
    return data.get(username, {})


def get_topic_progress(username: str, topic: str) -> dict:
    """
    Get progress data for a specific user and topic.
    
    Args:
        username: The username
        topic: The topic name
        
    Returns:
        Dictionary with mastery, level, scores, etc.
    """
    user_data = get_user_progress(username)
    return user_data.get(topic, {
        "mastery": 0,
        "level": "Not Assessed",
        "scores": [],
        "weak_areas": [],
        "sessions": 0,
        "last_accessed": None
    })


def update_assessment_score(username: str, topic: str, score: int, level: str):
    """
    Update the assessment score for a user's topic.
    
    Args:
        username: The username
        topic: The topic name
        score: The assessment score (0-100)
        level: The determined level (Beginner/Intermediate/Advanced)
    """
    data = _load_progress()
    
    if username not in data:
        data[username] = {}
    
    if topic not in data[username]:
        data[username][topic] = {
            "mastery": 0,
            "level": "Not Assessed",
            "scores": [],
            "weak_areas": [],
            "sessions": 0,
            "last_accessed": None,
            "completed": False
        }
    
    topic_data = data[username][topic]
    topic_data["scores"].append(score)
    topic_data["level"] = level
    
    # Calculate mastery as weighted average (recent scores weighted more)
    scores = topic_data["scores"]
    if len(scores) == 1:
        topic_data["mastery"] = score
    else:
        # Exponential moving average
        alpha = 0.6
        mastery = scores[0]
        for s in scores[1:]:
            mastery = alpha * s + (1 - alpha) * mastery
        topic_data["mastery"] = int(mastery)
    
    topic_data["last_accessed"] = datetime.now().isoformat()
    topic_data["sessions"] += 1
    
    if topic_data["mastery"] >= 75:
        topic_data["completed"] = True
    
    _save_progress(data)


def update_weak_areas(username: str, topic: str, weak_areas: list):
    """
    Update the identified weak areas for a user's topic.
    
    Args:
        username: The username
        topic: The topic name
        weak_areas: List of weak area strings
    """
    data = _load_progress()
    
    if username not in data:
        data[username] = {}
    
    if topic not in data[username]:
        data[username][topic] = {
            "mastery": 0,
            "level": "Not Assessed",
            "scores": [],
            "weak_areas": [],
            "sessions": 0,
            "last_accessed": None
        }
    
    data[username][topic]["weak_areas"] = weak_areas
    _save_progress(data)


def get_mastery_scores(username: str) -> dict:
    """
    Get mastery scores for all topics for a user.
    Used by the gap detector.
    
    Args:
        username: The username
        
    Returns:
        Dictionary of {topic: {"mastery": score, "level": level}}
    """
    user_data = get_user_progress(username)
    scores = {}
    for topic, data in user_data.items():
        scores[topic] = {
            "mastery": data.get("mastery", 0),
            "level": data.get("level", "Not Assessed")
        }
    return scores


def get_completed_topics(username: str) -> list:
    """Get list of topics where mastery >= 75."""
    user_data = get_user_progress(username)
    completed = []
    for topic, data in user_data.items():
        if data.get("mastery", 0) >= 75 or data.get("completed", False):
            completed.append(topic)
    return completed


def get_strengths(username: str) -> list:
    """Get topics where student performs well (mastery >= 60)."""
    user_data = get_user_progress(username)
    strengths = []
    for topic, data in user_data.items():
        if data.get("mastery", 0) >= 60:
            strengths.append({"topic": topic, "mastery": data["mastery"]})
    return sorted(strengths, key=lambda x: x["mastery"], reverse=True)


def get_weak_topics(username: str) -> list:
    """Get topics where student needs improvement (mastery < 50)."""
    user_data = get_user_progress(username)
    weak = []
    for topic, data in user_data.items():
        if 0 < data.get("mastery", 0) < 50:
            weak.append({"topic": topic, "mastery": data["mastery"]})
    return sorted(weak, key=lambda x: x["mastery"])


def get_overall_stats(username: str) -> dict:
    """
    Get overall statistics for a user.
    
    Returns:
        Dictionary with overall stats
    """
    user_data = get_user_progress(username)
    
    if not user_data:
        return {
            "total_topics_attempted": 0,
            "completed_topics": 0,
            "average_mastery": 0,
            "total_sessions": 0,
            "strongest_topic": None,
            "weakest_topic": None
        }
    
    masteries = []
    total_sessions = 0
    completed = 0
    strongest = None
    weakest = None
    max_mastery = -1
    min_mastery = 101
    
    for topic, data in user_data.items():
        mastery = data.get("mastery", 0)
        if mastery > 0:
            masteries.append(mastery)
            total_sessions += data.get("sessions", 0)
            
            if data.get("completed", False):
                completed += 1
            
            if mastery > max_mastery:
                max_mastery = mastery
                strongest = topic
            
            if mastery < min_mastery:
                min_mastery = mastery
                weakest = topic
    
    return {
        "total_topics_attempted": len(masteries),
        "completed_topics": completed,
        "average_mastery": int(sum(masteries) / len(masteries)) if masteries else 0,
        "total_sessions": total_sessions,
        "strongest_topic": strongest,
        "weakest_topic": weakest
    }
