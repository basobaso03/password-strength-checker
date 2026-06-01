"""
Password Strength Checker Module
Evaluates password strength based on multiple security criteria.

This module implements the core password validation logic using entropy principles
and security best practices to assess password strength levels.
"""

import re
from typing import Dict, Tuple
from collections import Counter


class PasswordStrengthChecker:
    """
    Evaluates password strength using multiple security criteria.
    
    Criteria:
    - Length: minimum required characters
    - Complexity: uppercase, lowercase, numbers, symbols
    - Entropy: character diversity
    - Common patterns: detects weak patterns
    """
    
    # Common weak passwords to check against
    COMMON_WEAK_PASSWORDS = {
        'password', '123456', '12345678', 'qwerty', 'abc123',
        'monkey', '1234567', 'letmein', 'trustno1', 'dragon',
        'baseball', '111111', 'iloveyou', 'master', 'sunshine',
        'ashley', 'bailey', 'passw0rd', 'shadow', '123123',
        '654321', 'superman', 'qazwsx', 'michael', 'football'
    }
    
    # Strength thresholds
    MIN_LENGTH_WEAK = 6
    MIN_LENGTH_MEDIUM = 8
    MIN_LENGTH_STRONG = 12
    
    def __init__(self):
        """Initialize the password strength checker."""
        self.uppercase_pattern = re.compile(r'[A-Z]')
        self.lowercase_pattern = re.compile(r'[a-z]')
        self.digit_pattern = re.compile(r'\d')
        self.special_pattern = re.compile(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]')
        self.sequential_pattern = re.compile(r'(.)\1{2,}')  # 3+ repeated chars
        self.common_sequence_pattern = re.compile(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)')
    
    def check_password(self, password: str) -> Dict:
        """
        Analyze password strength and return detailed feedback.
        
        Args:
            password (str): The password to analyze
            
        Returns:
            Dict: Contains strength level, score, feedback, and detailed criteria
        """
        if not password:
            return self._create_response('weak', 0, 'Password cannot be empty')

        if len(password) < self.MIN_LENGTH_MEDIUM:
            return {
                'strength': 'weak',
                'score': 0,
                'feedback': f'✗ Weak password - minimum {self.MIN_LENGTH_MEDIUM} characters required',
                'criteria': self._get_criteria_details(password),
                'suggestions': self._get_suggestions(password),
                'entropy': self._calculate_entropy(password)
            }
        
        # Calculate score based on multiple criteria
        score = self._calculate_score(password)
        strength, feedback = self._determine_strength(password, score)
        
        return {
            'strength': strength,
            'score': score,
            'feedback': feedback,
            'criteria': self._get_criteria_details(password),
            'suggestions': self._get_suggestions(password),
            'entropy': self._calculate_entropy(password)
        }
    
    def _calculate_score(self, password: str) -> int:
        """Calculate strength score (0-100)."""
        score = 0
        
        # Length scoring
        length = len(password)
        if length >= 8:
            score += 20
        elif length >= 6:
            score += 10
        
        if length >= 12:
            score += 10
        if length >= 16:
            score += 10
        
        # Character type diversity
        if self.uppercase_pattern.search(password):
            score += 15
        if self.lowercase_pattern.search(password):
            score += 15
        if self.digit_pattern.search(password):
            score += 15
        if self.special_pattern.search(password):
            score += 15
        
        # Penalize weak patterns
        if self._has_repeated_characters(password):
            score -= 10
        if self._has_sequential_characters(password):
            score -= 10
        if self._is_common_password(password):
            score -= 30
        if self._has_dictionary_words(password):
            score -= 5
        
        # Entropy bonus
        entropy = self._calculate_entropy(password)
        if entropy > 50:
            score += 10
        
        return max(0, min(score, 100))
    
    def _determine_strength(self, password: str, score: int) -> Tuple[str, str]:
        """Determine strength level based on score and criteria."""
        if score >= 80:
            return 'strong', '✓ Strong password'
        elif score >= 50:
            return 'medium', '◐ Medium password'
        else:
            return 'weak', '✗ Weak password'
    
    def _get_criteria_details(self, password: str) -> Dict:
        """Get detailed breakdown of each criteria."""
        length = len(password)
        return {
            'length': {
                'value': length,
                'met': length >= self.MIN_LENGTH_MEDIUM,
                'requirement': f'Minimum {self.MIN_LENGTH_MEDIUM} characters (current: {length})',
                'status': '✓' if length >= self.MIN_LENGTH_MEDIUM else '✗'
            },
            'uppercase': {
                'met': bool(self.uppercase_pattern.search(password)),
                'requirement': 'Contains uppercase letters (A-Z)',
                'status': '✓' if self.uppercase_pattern.search(password) else '✗'
            },
            'lowercase': {
                'met': bool(self.lowercase_pattern.search(password)),
                'requirement': 'Contains lowercase letters (a-z)',
                'status': '✓' if self.lowercase_pattern.search(password) else '✗'
            },
            'numbers': {
                'met': bool(self.digit_pattern.search(password)),
                'requirement': 'Contains numbers (0-9)',
                'status': '✓' if self.digit_pattern.search(password) else '✗'
            },
            'symbols': {
                'met': bool(self.special_pattern.search(password)),
                'requirement': 'Contains special symbols (!@#$%^&*)',
                'status': '✓' if self.special_pattern.search(password) else '✗'
            },
            'no_repeated': {
                'met': not self._has_repeated_characters(password),
                'requirement': 'No 3+ repeated characters',
                'status': '✓' if not self._has_repeated_characters(password) else '✗'
            },
            'no_sequential': {
                'met': not self._has_sequential_characters(password),
                'requirement': 'No sequential characters (abc, 123)',
                'status': '✓' if not self._has_sequential_characters(password) else '✗'
            }
        }
    
    def _get_suggestions(self, password: str) -> list:
        """Generate actionable suggestions for improvement."""
        suggestions = []
        
        if len(password) < self.MIN_LENGTH_STRONG:
            suggestions.append(f'Add more characters (target: {self.MIN_LENGTH_STRONG}+)')
        
        if not self.uppercase_pattern.search(password):
            suggestions.append('Add uppercase letters (A-Z)')
        
        if not self.lowercase_pattern.search(password):
            suggestions.append('Add lowercase letters (a-z)')
        
        if not self.digit_pattern.search(password):
            suggestions.append('Add numbers (0-9)')
        
        if not self.special_pattern.search(password):
            suggestions.append('Add special symbols (!@#$%^&*)')
        
        if self._has_repeated_characters(password):
            suggestions.append('Avoid repeating characters (aaa, 111)')
        
        if self._has_sequential_characters(password):
            suggestions.append('Avoid sequential patterns (abc, 123, qwerty)')
        
        if self._is_common_password(password):
            suggestions.append('This password is too common - choose something unique')
        
        return suggestions if suggestions else ['Password meets all security criteria!']
    
    def _has_repeated_characters(self, password: str) -> bool:
        """Check for 3+ repeated characters."""
        return bool(self.sequential_pattern.search(password))
    
    def _has_sequential_characters(self, password: str) -> bool:
        """Check for sequential characters (abc, 123)."""
        return bool(self.common_sequence_pattern.search(password.lower()))
    
    def _is_common_password(self, password: str) -> bool:
        """Check if password is in common weak passwords list."""
        return password.lower() in self.COMMON_WEAK_PASSWORDS
    
    def _has_dictionary_words(self, password: str) -> bool:
        """Check for common dictionary words."""
        # Extended list of common dictionary words
        common_words = {
            'admin', 'user', 'pass', 'test', 'demo', 'guest', 'hello',
            'world', 'love', 'hate', 'good', 'bad', 'king', 'queen',
            'prince', 'love', 'angel', 'devil', 'root', 'system'
        }
        password_lower = password.lower()
        return any(word in password_lower for word in common_words)
    
    def _calculate_entropy(self, password: str) -> float:
        """
        Calculate Shannon entropy of password (measure of randomness).
        Higher entropy = more random/secure.
        
        Returns:
            float: Entropy value (0-100 scale)
        """
        import math
        
        if not password:
            return 0
        
        # Count character frequency
        char_counts = Counter(password)
        entropy = 0
        
        for count in char_counts.values():
            probability = count / len(password)
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        # Normalize to 0-100 scale (max entropy for 94 printable chars)
        max_entropy = math.log2(94)  # Approximately 6.55 bits
        normalized_entropy = (entropy / max_entropy) * 100
        
        return round(min(normalized_entropy, 100), 2)
    
    def _create_response(self, strength: str, score: int, message: str) -> Dict:
        """Create a standard response object."""
        return {
            'strength': strength,
            'score': score,
            'feedback': message,
            'criteria': {},
            'suggestions': [],
            'entropy': 0
        }
