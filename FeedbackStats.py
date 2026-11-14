"""
FeedbackStats.py - Mini-Lab 3: Satisfaction Kiosk
Author: Emanuel Petrini

Business model for the kiosk: keeps the positive and negative vote counts
and answers questions about the current satisfaction level.
"""


class FeedbackStats:
    """
    Counts customer votes and computes the satisfaction percentage.
    The kiosk controller asks this class whether satisfaction is low enough
    to raise the manager alarm.
    """

    def __init__(self):
        """Start with no votes."""
        self._positive = 0
        self._negative = 0

    def record(self, positive):
        """Record one vote: True for a positive (green) vote, False for negative (red)."""
        if positive:
            self._positive += 1
        else:
            self._negative += 1

    def total(self):
        """Return the total number of votes recorded."""
        return self._positive + self._negative

    def satisfaction_pct(self):
        """
        Return the share of positive votes as an int from 0 to 100.
        Returns 100 when there are no votes yet, so an empty kiosk never
        divides by zero and never looks like a failure.
        """
        total = self.total()
        if total == 0:
            return 100
        return round(self._positive * 100 / total)

    def is_low(self, threshold, min_votes):
        """
        Return True when there are at least min_votes votes and the
        satisfaction percentage is below threshold.
        """
        return self.total() >= min_votes and self.satisfaction_pct() < threshold

    def reset(self):
        """Clear all votes (used by the manager)."""
        self._positive = 0
        self._negative = 0
