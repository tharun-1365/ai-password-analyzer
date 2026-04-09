document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('password-input');
    const toggleBtn = document.getElementById('toggle-visibility');
    const toggleIcon = toggleBtn.querySelector('i');
    
    const dashboard = document.getElementById('results-dashboard');
    const spinner = document.getElementById('loading-spinner');
    
    // UI Elements
    const strengthLabel = document.getElementById('strength-label');
    const aiScore = document.getElementById('ai-score');
    const progressBar = document.getElementById('progress-bar');
    const entropyScore = document.getElementById('entropy-score');
    const lengthScore = document.getElementById('length-score');
    
    const badgeUpper = document.getElementById('badge-upper');
    const badgeLower = document.getElementById('badge-lower');
    const badgeDigits = document.getElementById('badge-digits');
    const badgeSpecial = document.getElementById('badge-special');
    
    const feedbackList = document.getElementById('feedback-list');
    
    let timeoutId;
    
    // Toggle Password Visibility
    toggleBtn.addEventListener('click', () => {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            toggleIcon.classList.remove('fa-eye-slash');
            toggleIcon.classList.add('fa-eye');
        } else {
            passwordInput.type = 'password';
            toggleIcon.classList.remove('fa-eye');
            toggleIcon.classList.add('fa-eye-slash');
        }
    });

    // Handle Input
    passwordInput.addEventListener('input', (e) => {
        const password = e.target.value;
        
        clearTimeout(timeoutId);
        
        if (!password) {
            dashboard.classList.add('hidden');
            spinner.classList.add('hidden');
            document.body.className = '';
            document.querySelector('.glass-panel').className = 'glass-panel';
            return;
        }

        // Slight debounce for performance
        timeoutId = setTimeout(() => {
            analyzePassword(password);
        }, 300);
    });

    async function analyzePassword(password) {
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ password })
            });

            const data = await response.json();
            
            if (data.empty) {
                dashboard.classList.add('hidden');
                return;
            }

            updateUI(data);
        } catch (error) {
            console.error('Error analyzing password:', error);
        }
    }

    function updateUI(data) {
        dashboard.classList.remove('hidden');
        spinner.classList.add('hidden');
        
        const { strength, score, features, feedback } = data;
        
        // Update State Classes
        const stateClass = `state-${strength.toLowerCase()}`;
        document.querySelector('.glass-panel').className = `glass-panel ${stateClass}`;
        
        // Animate weak state
        if (strength === 'Weak') {
            const inputGroup = document.querySelector('.input-group');
            inputGroup.classList.remove('shake');
            void inputGroup.offsetWidth; // trigger reflow
            inputGroup.classList.add('shake');
        }
        
        // Update basic metrics
        strengthLabel.textContent = strength;
        aiScore.textContent = `${score}%`;
        
        // Progress bar logic
        let progressWidth = '0%';
        if (strength === 'Weak') progressWidth = Math.max(10, score) + '%';
        if (strength === 'Medium') progressWidth = '50%';
        if (strength === 'Strong') progressWidth = '100%';
        progressBar.style.width = progressWidth;
        
        entropyScore.textContent = Math.round(features.entropy);
        lengthScore.textContent = features.length;
        
        // Update Feature Badges
        updateBadge(badgeUpper, features.num_upper);
        updateBadge(badgeLower, features.num_lower);
        updateBadge(badgeDigits, features.num_digits);
        updateBadge(badgeSpecial, features.num_special);
        
        // Update Feedback List
        feedbackList.innerHTML = '';
        if (feedback.length === 0) {
            const li = document.createElement('li');
            li.textContent = "Excellent! No vulnerabilities detected.";
            feedbackList.appendChild(li);
        } else {
            feedback.forEach(item => {
                const li = document.createElement('li');
                
                // Add icon based on content
                if (item.includes("Great") || item.includes("Looks good")) {
                    li.innerHTML = `<i class="fa-solid fa-check-circle" style="color: var(--strong-color); margin-right: 8px;"></i> <span>${item}</span>`;
                } else if (strength === 'Weak') {
                    li.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color: var(--weak-color); margin-right: 8px;"></i> <span>${item}</span>`;
                } else {
                    li.innerHTML = `<i class="fa-solid fa-circle-info" style="color: var(--medium-color); margin-right: 8px;"></i> <span>${item}</span>`;
                }
                
                li.style.display = 'flex';
                li.style.alignItems = 'flex-start';
                feedbackList.appendChild(li);
            });
        }
    }

    function updateBadge(badgeElement, count) {
        const countSpan = badgeElement.querySelector('.count');
        countSpan.textContent = count;
        
        if (count > 0) {
            badgeElement.classList.add('active');
        } else {
            badgeElement.classList.remove('active');
        }
    }
});
