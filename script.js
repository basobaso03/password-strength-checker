/**
 * Password Strength Checker - Frontend JavaScript
 * Handles UI interactions, API communication, and real-time password analysis
 */

const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const passwordInput = document.getElementById('password-input');
const toggleVisibilityBtn = document.getElementById('toggle-visibility');
const resultsSection = document.getElementById('results-section');
const emptyState = document.getElementById('empty-state');
const strengthBar = document.getElementById('strength-bar');
const strengthLevel = document.getElementById('strength-level');
const strengthScore = document.getElementById('strength-score');
const feedbackText = document.getElementById('feedback-text');
const criteriaList = document.getElementById('criteria-list');
const suggestionsList = document.getElementById('suggestions-list');
const suggestionsSection = document.getElementById('suggestions-section');
const entropyValue = document.getElementById('entropy-value');
const copyResultsBtn = document.getElementById('copy-results-btn');

// State
let currentResult = null;
let isPasswordVisible = false;
let useLocalChecker = false;

// Common patterns/lists for client-side evaluation matching backend/checker.py
const COMMON_WEAK_PASSWORDS = new Set([
    'password', '123456', '12345678', 'qwerty', 'abc123',
    'monkey', '1234567', 'letmein', 'trustno1', 'dragon',
    'baseball', '111111', 'iloveyou', 'master', 'sunshine',
    'ashley', 'bailey', 'passw0rd', 'shadow', '123123',
    '654321', 'superman', 'qazwsx', 'michael', 'football'
]);

const DICTIONARY_WORDS = [
    'admin', 'user', 'pass', 'test', 'demo', 'guest', 'hello',
    'world', 'love', 'hate', 'good', 'bad', 'king', 'queen',
    'prince', 'love', 'angel', 'devil', 'root', 'system'
];

// ============================================
// Event Listeners
// ============================================

/**
 * Real-time password input handler
 */
passwordInput.addEventListener('input', async (e) => {
    const password = e.target.value;

    if (!password) {
        // Show empty state
        resultsSection.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';
    resultsSection.style.display = 'block';

    try {
        // Call API to check password
        const result = await checkPasswordStrength(password);
        currentResult = result;

        // Update UI with results
        displayResults(result);
    } catch (error) {
        console.error('Error checking password:', error);
        showToast('Error checking password strength', 'error');
    }
});

/**
 * Toggle password visibility
 */
toggleVisibilityBtn.addEventListener('click', () => {
    isPasswordVisible = !isPasswordVisible;
    const newType = isPasswordVisible ? 'text' : 'password';
    passwordInput.type = newType;
    toggleVisibilityBtn.textContent = isPasswordVisible ? '🙈' : '👁️';
});

/**
 * Copy results button
 */
copyResultsBtn.addEventListener('click', async () => {
    if (!currentResult) return;

    const resultsText = formatResultsForCopy(currentResult);
    try {
        await navigator.clipboard.writeText(resultsText);
        showToast('Results copied to clipboard!', 'success');
    } catch (error) {
        console.error('Failed to copy:', error);
        showToast('Failed to copy results', 'error');
    }
});

// ============================================
// API Communication & Local Checker Fallback
// ============================================

/**
 * Check password strength via API (with client-side fallback)
 * @param {string} password - The password to check
 * @returns {Promise<Object>} - The analysis result
 */
async function checkPasswordStrength(password) {
    if (useLocalChecker) {
        return checkPasswordStrengthLocal(password);
    }

    try {
        const response = await fetch(`${API_BASE_URL}/check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ password }),
        });

        if (!response.ok) {
            throw new Error(`API response status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.warn('API communication error. Falling back to local analyzer.', error);
        return checkPasswordStrengthLocal(password);
    }
}

/**
 * Test API connection
 */
async function testAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch (error) {
        console.error('Cannot connect to API:', error);
        return false;
    }
}

/**
 * Evaluates password strength entirely on the client-side.
 * Replicates the calculations of the Python Flask backend for static deployments (GitHub Pages).
 */
function checkPasswordStrengthLocal(password) {
    if (!password) {
        return {
            strength: 'weak',
            score: 0,
            feedback: 'Password cannot be empty',
            criteria: {},
            suggestions: [],
            entropy: 0
        };
    }

    let score = 0;
    const len = password.length;

    // 1. Length scoring
    if (len >= 8) {
        score += 20;
    } else if (len >= 6) {
        score += 10;
    }
    if (len >= 12) score += 10;
    if (len >= 16) score += 10;

    // 2. Character type diversity
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasDigit = /\d/.test(password);
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]/.test(password);

    if (hasUpper) score += 15;
    if (hasLower) score += 15;
    if (hasDigit) score += 15;
    if (hasSpecial) score += 15;

    // 3. Repeated characters (3+ consecutive identical)
    const hasRepeated = /(.)\1{2,}/.test(password);
    if (hasRepeated) score -= 10;

    // 4. Sequential patterns (abc, 123)
    const sequentialPattern = /(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)/i;
    const hasSequential = sequentialPattern.test(password);
    if (hasSequential) score -= 10;

    // 5. Common weak passwords check
    const isCommon = COMMON_WEAK_PASSWORDS.has(password.toLowerCase());
    if (isCommon) score -= 30;

    // 6. Dictionary words check
    const hasDict = DICTIONARY_WORDS.some(word => password.toLowerCase().includes(word));
    if (hasDict) score -= 5;

    // 7. Entropy calculation & bonus
    const entropy = calculateEntropy(password);
    if (entropy > 50) score += 10;

    // Clamp score 0-100
    score = Math.max(0, Math.min(score, 100));

    // Determine strength level
    let strength = 'weak';
    let feedback = '✗ Weak password';
    if (score >= 80) {
        strength = 'strong';
        feedback = '✓ Strong password';
    } else if (score >= 50) {
        strength = 'medium';
        feedback = '◐ Medium password';
    }

    // Build criteria object matching backend schema
    const criteria = {
        length: {
            value: len,
            met: len >= 8,
            requirement: `Minimum 8 characters (current: ${len})`,
            status: len >= 8 ? '✓' : '✗'
        },
        uppercase: {
            met: hasUpper,
            requirement: 'Contains uppercase letters (A-Z)',
            status: hasUpper ? '✓' : '✗'
        },
        lowercase: {
            met: hasLower,
            requirement: 'Contains lowercase letters (a-z)',
            status: hasLower ? '✓' : '✗'
        },
        numbers: {
            met: hasDigit,
            requirement: 'Contains numbers (0-9)',
            status: hasDigit ? '✓' : '✗'
        },
        symbols: {
            met: hasSpecial,
            requirement: 'Contains special symbols (!@#$%^&*)',
            status: hasSpecial ? '✓' : '✗'
        },
        no_repeated: {
            met: !hasRepeated,
            requirement: 'No 3+ repeated characters',
            status: !hasRepeated ? '✓' : '✗'
        },
        no_sequential: {
            met: !hasSequential,
            requirement: 'No sequential characters (abc, 123)',
            status: !hasSequential ? '✓' : '✗'
        }
    };

    // Build actionable suggestions
    const suggestions = [];
    if (len < 12) suggestions.push('Add more characters (target: 12+)');
    if (!hasUpper) suggestions.push('Add uppercase letters (A-Z)');
    if (!hasLower) suggestions.push('Add lowercase letters (a-z)');
    if (!hasDigit) suggestions.push('Add numbers (0-9)');
    if (!hasSpecial) suggestions.push('Add special symbols (!@#$%^&*)');
    if (hasRepeated) suggestions.push('Avoid repeating characters (aaa, 111)');
    if (hasSequential) suggestions.push('Avoid sequential patterns (abc, 123, qwerty)');
    if (isCommon) suggestions.push('This password is too common - choose something unique');

    if (suggestions.length === 0) {
        suggestions.push('Password meets all security criteria!');
    }

    return {
        strength,
        score,
        feedback,
        criteria,
        suggestions,
        entropy
    };
}

/**
 * Calculates the Shannon Entropy of a password on a 0-100 scale.
 * Matches backend Shannon Entropy logic.
 */
function calculateEntropy(password) {
    if (!password) return 0;

    const charCounts = {};
    for (let char of password) {
        charCounts[char] = (charCounts[char] || 0) + 1;
    }

    let entropy = 0;
    const len = password.length;
    for (let char in charCounts) {
        const p = charCounts[char] / len;
        if (p > 0) {
            entropy -= p * Math.log2(p);
        }
    }

    // Normalize to 0-100 scale (max entropy is approximately 6.55 bits for 94 printable ASCII characters)
    const maxEntropy = Math.log2(94);
    const normalizedEntropy = (entropy / maxEntropy) * 100;

    return parseFloat(Math.min(normalizedEntropy, 100).toFixed(2));
}

// ============================================
// UI Updates
// ============================================

/**
 * Display password analysis results
 * @param {Object} result - The analysis result from API
 */
function displayResults(result) {
    // Update strength bar
    updateStrengthBar(result.strength, result.score);

    // Update strength level and score
    strengthLevel.textContent = result.feedback;
    strengthScore.textContent = `Score: ${result.score}/100`;

    // Update feedback
    feedbackText.textContent = result.feedback;

    // Update entropy
    entropyValue.textContent = `${result.entropy}%`;

    // Update criteria
    displayCriteria(result.criteria);

    // Update suggestions
    displaySuggestions(result.suggestions);
}

/**
 * Update the strength meter bar
 * @param {string} strength - 'weak', 'medium', or 'strong'
 * @param {number} score - Score from 0-100
 */
function updateStrengthBar(strength, score) {
    // Remove previous strength classes
    strengthBar.classList.remove('weak', 'medium', 'strong');

    // Add new strength class
    strengthBar.classList.add(strength);

    // Update bar width based on score
    strengthBar.style.width = `${Math.max(score, 5)}%`;
}

/**
 * Display criteria checklist
 * @param {Object} criteria - Criteria object from API
 */
function displayCriteria(criteria) {
    criteriaList.innerHTML = '';

    Object.entries(criteria).forEach(([key, criterion]) => {
        const criteriaItem = createCriteriaElement(key, criterion);
        criteriaList.appendChild(criteriaItem);
    });
}

/**
 * Create a criteria list item
 * @param {string} key - Criteria key
 * @param {Object} criterion - Criteria object
 * @returns {HTMLElement} - The criteria item element
 */
function createCriteriaElement(key, criterion) {
    const div = document.createElement('div');
    div.className = `criteria-item ${criterion.met ? 'met' : 'unmet'}`;

    const status = document.createElement('span');
    status.className = 'status';
    status.textContent = criterion.status;

    const requirement = document.createElement('span');
    requirement.className = 'requirement';
    requirement.textContent = criterion.requirement;

    div.appendChild(status);
    div.appendChild(requirement);

    // Add value for length criterion
    if (key === 'length' && criterion.value !== undefined) {
        const value = document.createElement('span');
        value.className = 'value';
        value.textContent = `Current: ${criterion.value} characters`;
        div.appendChild(value);
    }

    return div;
}

/**
 * Display suggestions
 * @param {Array} suggestions - Array of suggestion strings
 */
function displaySuggestions(suggestions) {
    suggestionsList.innerHTML = '';

    if (suggestions.length === 0) {
        suggestionsSection.style.display = 'none';
        return;
    }

    suggestionsSection.style.display = 'block';

    suggestions.forEach((suggestion) => {
        const li = document.createElement('li');
        li.textContent = suggestion;
        suggestionsList.appendChild(li);
    });
}

/**
 * Format results for clipboard copying
 * @param {Object} result - The analysis result
 * @returns {string} - Formatted text
 */
function formatResultsForCopy(result) {
    let text = `Password Strength Analysis\n`;
    text += `================================\n`;
    text += `Strength: ${result.strength.toUpperCase()}\n`;
    text += `Score: ${result.score}/100\n`;
    text += `Entropy: ${result.entropy}%\n`;
    text += `Feedback: ${result.feedback}\n\n`;

    text += `Criteria Met:\n`;
    Object.entries(result.criteria).forEach(([key, criterion]) => {
        text += `${criterion.status} ${criterion.requirement}\n`;
    });

    if (result.suggestions.length > 0) {
        text += `\nSuggestions:\n`;
        result.suggestions.forEach((suggestion) => {
            text += `• ${suggestion}\n`;
        });
    }

    return text;
}

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - 'success' or 'error'
 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// ============================================
// Initialization
// ============================================

/**
 * Initialize the application
 */
async function initializeApp() {
    console.log('Initializing Password Strength Checker...');

    const apiStatusBadge = document.getElementById('api-status-badge');
    const isGitHubPages = window.location.hostname.endsWith('github.io');

    if (isGitHubPages) {
        useLocalChecker = true;
        console.log('✓ Running on GitHub Pages. Enabled local static analysis.');
        if (apiStatusBadge) {
            apiStatusBadge.textContent = 'Mode: Local (Browser)';
            apiStatusBadge.className = 'status-badge local';
        }
    } else {
        // Test API connection
        const isConnected = await testAPIConnection();

        if (!isConnected) {
            useLocalChecker = true;
            console.warn('API connection failed. Make sure the Flask server is running on http://localhost:5000. Using client-side analysis.');
            if (apiStatusBadge) {
                apiStatusBadge.textContent = 'Mode: Local (Fallback)';
                apiStatusBadge.className = 'status-badge local';
            }
        } else {
            useLocalChecker = false;
            console.log('✓ API connection successful');
            if (apiStatusBadge) {
                apiStatusBadge.textContent = 'Mode: API (Backend)';
                apiStatusBadge.className = 'status-badge api';
            }
        }
    }

    // Focus on password input
    passwordInput.focus();
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// ============================================
// Utility Functions
// ============================================

/**
 * Format number with thousand separators
 * @param {number} num - Number to format
 * @returns {string} - Formatted number
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Get current password length
 * @returns {number} - Password length
 */
function getPasswordLength() {
    return passwordInput.value.length;
}

/**
 * Clear password input
 */
function clearPassword() {
    passwordInput.value = '';
    passwordInput.dispatchEvent(new Event('input'));
}

/**
 * Log password analysis (for debugging)
 */
function logAnalysis() {
    if (currentResult) {
        console.log('Current Password Analysis:', currentResult);
    } else {
        console.log('No analysis available');
    }
}

// Expose utility functions for console testing
window.passwordStrengthChecker = {
    clearPassword,
    logAnalysis,
    getPasswordLength,
};

console.log('Password Strength Checker loaded. Type: window.passwordStrengthChecker.logAnalysis() to see current analysis.');
