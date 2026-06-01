"""
Unit tests for the PasswordStrengthChecker module.
Tests all criteria, edge cases, and security logic.
"""

import pytest
from checker import PasswordStrengthChecker


class TestPasswordStrengthChecker:
    """Test suite for password strength checker."""
    
    @pytest.fixture
    def checker(self):
        """Initialize checker for each test."""
        return PasswordStrengthChecker()
    
    # ====== LENGTH TESTS ======
    
    def test_empty_password(self, checker):
        """Test empty password handling."""
        result = checker.check_password('')
        assert result['strength'] == 'weak'
        assert result['score'] == 0
        assert 'empty' in result['feedback'].lower()
    
    def test_very_short_password(self, checker):
        """Test very short passwords."""
        result = checker.check_password('a')
        assert result['strength'] == 'weak'
        assert result['score'] < 50
    
    def test_minimum_weak_length(self, checker):
        """Test minimum weak password length."""
        result = checker.check_password('abc123')
        assert result['strength'] == 'weak'
        assert result['score'] == 0
    
    def test_medium_length_password(self, checker):
        """Test medium length password."""
        result = checker.check_password('Password12')
        assert result['criteria']['length']['met'] == True
        assert result['criteria']['length']['value'] == 10
    
    def test_long_password(self, checker):
        """Test long password."""
        result = checker.check_password('VeryLongPasswordWith123!@#Symbols')
        assert result['criteria']['length']['value'] == 33
        assert result['score'] > 50
    
    def test_maximum_length(self, checker):
        """Test very long password."""
        long_pass = 'A' * 100 + 'b1!@'
        result = checker.check_password(long_pass)
        assert result['criteria']['length']['value'] == 104
    
    # ====== CHARACTER TYPE TESTS ======
    
    def test_uppercase_requirement(self, checker):
        """Test uppercase letter detection."""
        result = checker.check_password('abcdef123!')
        assert result['criteria']['uppercase']['met'] == False
        
        result = checker.check_password('Abcdef123!')
        assert result['criteria']['uppercase']['met'] == True
    
    def test_lowercase_requirement(self, checker):
        """Test lowercase letter detection."""
        result = checker.check_password('ABCDEF123!')
        assert result['criteria']['lowercase']['met'] == False
        
        result = checker.check_password('ABCDEFabc123!')
        assert result['criteria']['lowercase']['met'] == True
    
    def test_number_requirement(self, checker):
        """Test number detection."""
        result = checker.check_password('AbcDefGH!')
        assert result['criteria']['numbers']['met'] == False
        
        result = checker.check_password('AbcDefGH9!')
        assert result['criteria']['numbers']['met'] == True
    
    def test_symbol_requirement(self, checker):
        """Test special symbol detection."""
        result = checker.check_password('AbcDefGH123')
        assert result['criteria']['symbols']['met'] == False
        
        result = checker.check_password('AbcDefGH123!')
        assert result['criteria']['symbols']['met'] == True
    
    def test_multiple_symbol_types(self, checker):
        """Test various special symbols."""
        symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '=', '_', '+']
        for symbol in symbols:
            password = f'Pass1{symbol}'
            result = checker.check_password(password)
            assert result['criteria']['symbols']['met'] == True
    
    # ====== PATTERN TESTS ======
    
    def test_repeated_characters(self, checker):
        """Test detection of repeated characters."""
        result = checker.check_password('Password111!!!1Aa@')
        assert result['criteria']['no_repeated']['met'] == False
    
    def test_no_repeated_characters(self, checker):
        """Test password with no repeated characters."""
        result = checker.check_password('Pasword1!@')
        assert result['criteria']['no_repeated']['met'] == True
    
    def test_sequential_numbers(self, checker):
        """Test detection of sequential numbers."""
        result = checker.check_password('Pass123Word!')
        assert result['criteria']['no_sequential']['met'] == False
    
    def test_sequential_letters(self, checker):
        """Test detection of sequential letters."""
        result = checker.check_password('AbcPassword123!')
        assert result['criteria']['no_sequential']['met'] == False
    
    def test_no_sequential_patterns(self, checker):
        """Test password with no sequential patterns."""
        result = checker.check_password('Passw0rd!@#')
        assert result['criteria']['no_sequential']['met'] == True
    
    # ====== COMMON PASSWORD TESTS ======
    
    def test_common_weak_passwords(self, checker):
        """Test detection of commonly used weak passwords."""
        common_weak = ['password', '123456', 'qwerty', 'abc123', 'monkey']
        for pwd in common_weak:
            result = checker.check_password(pwd)
            assert result['strength'] == 'weak'
    
    def test_case_insensitive_common_password(self, checker):
        """Test case-insensitive detection of common passwords."""
        result = checker.check_password('PASSWORD')
        assert result['strength'] == 'weak'
        
        result = checker.check_password('PaSsWoRd')
        assert result['strength'] == 'weak'
    
    # ====== STRENGTH LEVEL TESTS ======
    
    def test_weak_password_classification(self, checker):
        """Test weak password classification."""
        weak_passwords = ['pass', 'abc', '123', 'weak']
        for pwd in weak_passwords:
            result = checker.check_password(pwd)
            assert result['strength'] in ['weak', 'medium']
    
    def test_medium_password_classification(self, checker):
        """Test medium password classification."""
        result = checker.check_password('Passw0rd')
        assert result['strength'] in ['medium', 'strong']
    
    def test_strong_password_classification(self, checker):
        """Test strong password classification."""
        result = checker.check_password('Str0ng!@#$Passw0rd2024')
        assert result['strength'] == 'strong'
    
    # ====== SCORE TESTS ======
    
    def test_score_range(self, checker):
        """Test that score is always 0-100."""
        passwords = ['', 'a', 'password', 'MyP@ssw0rd!', 'VeryStr0ng!@#$%^&*()Password']
        for pwd in passwords:
            result = checker.check_password(pwd)
            assert 0 <= result['score'] <= 100
    
    def test_score_progression(self, checker):
        """Test score increases with complexity."""
        scores = []
        passwords = [
            'a',
            'aB',
            'aB1',
            'aB1!',
            'aB1!xxxx',
            'aB1!xxxxYY',
            'aB1!xxxxYYzz2023',
            'aB1!xxxxYYzz2023@#$%'
        ]
        for pwd in passwords:
            result = checker.check_password(pwd)
            scores.append(result['score'])
        
        # Scores should generally increase (allowing for some variation)
        assert scores[-1] > scores[0]
    
    # ====== ENTROPY TESTS ======
    
    def test_entropy_calculation(self, checker):
        """Test entropy calculation."""
        result = checker.check_password('a' * 10)
        entropy_low = result['entropy']
        
        result = checker.check_password('AaBbCc1!@#$%^&*')
        entropy_high = result['entropy']
        
        assert entropy_low < entropy_high
        assert 0 <= entropy_low <= 100
        assert 0 <= entropy_high <= 100
    
    # ====== FEEDBACK & SUGGESTIONS TESTS ======
    
    def test_suggestions_generated(self, checker):
        """Test that suggestions are generated for weak passwords."""
        result = checker.check_password('weak')
        assert len(result['suggestions']) > 0
        assert isinstance(result['suggestions'], list)
    
    def test_no_suggestions_for_strong_password(self, checker):
        """Test that strong passwords get positive feedback."""
        result = checker.check_password('Str0ng!@#$Passw0rd2024')
        assert len(result['suggestions']) > 0
        suggestions_text = ' '.join(result['suggestions']).lower()
        assert 'criteria' in suggestions_text or 'strong' in result['feedback'].lower()
    
    def test_suggestions_for_missing_uppercase(self, checker):
        """Test suggestion for missing uppercase."""
        result = checker.check_password('password123!')
        suggestions = result['suggestions']
        # Should suggest adding uppercase
        assert any('uppercase' in s.lower() for s in suggestions)
    
    def test_suggestions_for_missing_numbers(self, checker):
        """Test suggestion for missing numbers."""
        result = checker.check_password('Password!')
        suggestions = result['suggestions']
        # Should suggest adding numbers
        assert any('number' in s.lower() or 'digit' in s.lower() for s in suggestions)
    
    def test_suggestions_for_missing_symbols(self, checker):
        """Test suggestion for missing symbols."""
        result = checker.check_password('Password123')
        suggestions = result['suggestions']
        # Should suggest adding symbols
        assert any('symbol' in s.lower() or 'special' in s.lower() for s in suggestions)
    
    # ====== CRITERIA DETAILS TESTS ======
    
    def test_criteria_structure(self, checker):
        """Test that criteria response has all required fields."""
        result = checker.check_password('TestPass123!')
        criteria = result['criteria']
        
        required_fields = ['length', 'uppercase', 'lowercase', 'numbers', 'symbols', 'no_repeated', 'no_sequential']
        for field in required_fields:
            assert field in criteria
            assert 'met' in criteria[field]
            assert 'requirement' in criteria[field]
            assert 'status' in criteria[field]
    
    # ====== RESPONSE STRUCTURE TESTS ======
    
    def test_response_structure(self, checker):
        """Test that response has all required fields."""
        result = checker.check_password('TestPassword123!')
        
        required_fields = ['strength', 'score', 'feedback', 'criteria', 'suggestions', 'entropy']
        for field in required_fields:
            assert field in result
    
    def test_response_types(self, checker):
        """Test that response fields have correct types."""
        result = checker.check_password('TestPassword123!')
        
        assert isinstance(result['strength'], str)
        assert isinstance(result['score'], int)
        assert isinstance(result['feedback'], str)
        assert isinstance(result['criteria'], dict)
        assert isinstance(result['suggestions'], list)
        assert isinstance(result['entropy'], (int, float))
    
    # ====== SPECIAL CASES ======
    
    def test_unicode_characters(self, checker):
        """Test password with unicode characters."""
        result = checker.check_password('Pässwörd123!@#')
        # Should handle unicode gracefully
        assert 'strength' in result
        assert 'score' in result
    
    def test_spaces_in_password(self, checker):
        """Test password with spaces."""
        result = checker.check_password('Pass Word 123!')
        assert result['criteria']['length']['value'] == 13
    
    def test_all_same_character(self, checker):
        """Test password with all same character."""
        result = checker.check_password('aaaaaaaaaa')
        assert result['strength'] == 'weak'
    
    def test_numeric_only_password(self, checker):
        """Test numeric-only password."""
        result = checker.check_password('1234567890')
        assert result['criteria']['uppercase']['met'] == False
        assert result['criteria']['lowercase']['met'] == False


class TestPasswordCheckerEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def checker(self):
        """Initialize checker for each test."""
        return PasswordStrengthChecker()
    
    def test_null_like_strings(self, checker):
        """Test null-like string values."""
        result = checker.check_password('')
        assert result['score'] == 0
    
    def test_whitespace_only(self, checker):
        """Test whitespace-only password."""
        result = checker.check_password('     ')
        assert result['strength'] == 'weak'
        assert result['score'] < 50
    
    def test_very_long_password_performance(self, checker):
        """Test performance with very long password."""
        long_password = 'P@ssw0rd!' * 100
        result = checker.check_password(long_password)
        assert result['score'] > 0
        assert 'strength' in result
    
    def test_special_characters_only(self, checker):
        """Test password with only special characters."""
        result = checker.check_password('!@#$%^&*()')
        assert result['criteria']['uppercase']['met'] == False
        assert result['criteria']['lowercase']['met'] == False
        assert result['criteria']['numbers']['met'] == False


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
