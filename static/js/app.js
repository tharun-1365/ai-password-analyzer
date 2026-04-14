document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const passwordInput = document.getElementById('password-input');
    const usernameInput = document.getElementById('username-input');
    const toggleBtn = document.getElementById('toggle-visibility');
    const toggleIcon = toggleBtn.querySelector('i');
    const submitBtn = document.getElementById('submit-btn');
    const authMessage = document.getElementById('auth-message');
    
    // Tabs
    const tabLogin = document.getElementById('tab-login');
    const tabRegister = document.getElementById('tab-register');
    let isLoginMode = true;

    // Analyzer UI
    const dashboard = document.getElementById('results-dashboard');
    const spinner = document.getElementById('loading-spinner');
    const strengthLabel = document.getElementById('strength-label');
    const aiScore = document.getElementById('ai-score');
    const progressBar = document.getElementById('progress-bar');
    const entropyScore = document.getElementById('entropy-score');
    const lengthScore = document.getElementById('length-score');
    
    // Badges
    const badges = {
        upper: document.getElementById('badge-upper'),
        lower: document.getElementById('badge-lower'),
        digits: document.getElementById('badge-digits'),
        special: document.getElementById('badge-special')
    };
    const feedbackList = document.getElementById('feedback-list');

    // OTP Modal Elements
    const otpModal = document.getElementById('otp-modal');
    const verifyOtpBtn = document.getElementById('verify-otp-btn');
    const otpInput = document.getElementById('otp-input');
    const otpMessage = document.getElementById('otp-message');
    
    // Biometrics State
    let keydownTimes = {};
    let keystrokeEvents = [];
    let backspaceCount = 0;
    let deleteCount = 0;
    
    // Analysis Timeout
    let timeoutId;

    // --- Tab Handling ---
    function switchTab(loginSelected) {
        isLoginMode = loginSelected;
        if (isLoginMode) {
            tabLogin.classList.add('active');
            tabRegister.classList.remove('active');
            submitBtn.textContent = 'Login';
        } else {
            tabRegister.classList.add('active');
            tabLogin.classList.remove('active');
            submitBtn.textContent = 'Register';
        }
        
        // Reset state
        authMessage.classList.add('hidden');
        passwordInput.value = '';
        usernameInput.value = '';
        dashboard.classList.add('hidden');
        document.querySelector('.glass-panel').className = 'glass-panel';
        resetBiometrics();
    }
    
    tabLogin.addEventListener('click', () => switchTab(true));
    tabRegister.addEventListener('click', () => switchTab(false));

    // --- Biometrics Tracking ---
    function resetBiometrics() {
        keydownTimes = {};
        keystrokeEvents = [];
        backspaceCount = 0;
        deleteCount = 0;
    }

    passwordInput.addEventListener('keydown', (e) => {
        const timestamp = performance.now();
        const key = e.key;

        if (key === 'Backspace') backspaceCount++;
        if (key === 'Delete') deleteCount++;

        if (!keydownTimes[key]) {
            keydownTimes[key] = timestamp;
        }
    });

    passwordInput.addEventListener('keyup', (e) => {
        const timestamp = performance.now();
        const key = e.key;

        if (keydownTimes[key]) {
            const dwellTime = timestamp - keydownTimes[key];
            keystrokeEvents.push({
                key: key,
                downTime: keydownTimes[key],
                upTime: timestamp,
                dwellTime: dwellTime
            });
            delete keydownTimes[key];
        }
    });

    function calculateBiometricsFeatures() {
        if (keystrokeEvents.length === 0) return {};

        let totalDwell = 0;
        let totalFlight = 0;
        let validFlightEvents = 0;
        let hesitationCount = 0;

        // Calculate Dwell
        keystrokeEvents.forEach(event => {
            totalDwell += event.dwellTime;
        });

        // Calculate Flight (time from key_1 up to key_2 down)
        // Note: For simple typing, we just approximate it using consecutive event times in the array
        keystrokeEvents.sort((a, b) => a.downTime - b.downTime);
        for (let i = 1; i < keystrokeEvents.length; i++) {
            const currentDown = keystrokeEvents[i].downTime;
            const prevUp = keystrokeEvents[i-1].upTime;
            const flightTime = currentDown - prevUp;
            
            if (flightTime > 800) {
                hesitationCount++;
            }
            
            // Filter out anomalous pauses (e.g. going to grab coffee)
            if (flightTime > 0 && flightTime < 2000) { 
                totalFlight += flightTime;
                validFlightEvents++;
            }
        }

        const avgDwell = totalDwell / keystrokeEvents.length;
        const avgFlight = validFlightEvents > 0 ? (totalFlight / validFlightEvents) : 0;
        
        // Overall Speed
        const totalDuration = keystrokeEvents[keystrokeEvents.length - 1].upTime - keystrokeEvents[0].downTime;
        const typingSpeed = totalDuration > 0 ? (keystrokeEvents.length / (totalDuration / 1000)) : 0; // chars per second

        return {
            avg_dwell: avgDwell,
            avg_flight: avgFlight,
            typing_speed: typingSpeed,
            error_rate: backspaceCount / Math.max(passwordInput.value.length, 1),
            backspace_count: backspaceCount,
            delete_count: deleteCount,
            hesitation_count: hesitationCount
        };
    }

    // --- Visibility Toggle ---
    toggleBtn.addEventListener('click', () => {
        const isPassword = passwordInput.type === 'password';
        passwordInput.type = isPassword ? 'text' : 'password';
        toggleIcon.className = isPassword ? 'fa-solid fa-eye' : 'fa-solid fa-eye-slash';
    });

    // --- Live Password Analyzer ---
    passwordInput.addEventListener('input', (e) => {
        const password = e.target.value;
        clearTimeout(timeoutId);
        
        if (!password) {
            dashboard.classList.add('hidden');
            spinner.classList.add('hidden');
            document.querySelector('.glass-panel').className = 'glass-panel';
            return;
        }

        timeoutId = setTimeout(() => {
            fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password })
            })
            .then(res => res.json())
            .then(data => {
                if (!data.empty) updateAnalyzerUI(data);
            });
        }, 300);
    });

    function updateAnalyzerUI(data) {
        dashboard.classList.remove('hidden');
        
        const { strength, score, features, feedback } = data;
        const stateClass = `state-${strength.toLowerCase()}`;
        document.querySelector('.glass-panel').className = `glass-panel ${stateClass}`;
        
        strengthLabel.textContent = strength;
        aiScore.textContent = `${score}%`;
        
        // Progress UI
        let progressWidth = '0%';
        if (strength === 'Weak') progressWidth = Math.max(10, score) + '%';
        if (strength === 'Medium') progressWidth = '50%';
        if (strength === 'Strong') progressWidth = '100%';
        progressBar.style.width = progressWidth;
        
        entropyScore.textContent = Math.round(features.entropy);
        lengthScore.textContent = features.length;
        
        // Badges
        updateBadge(badges.upper, features.num_upper);
        updateBadge(badges.lower, features.num_lower);
        updateBadge(badges.digits, features.num_digits);
        updateBadge(badges.special, features.num_special);
        
        // Feedback
        feedbackList.innerHTML = '';
        if (feedback.length === 0) {
            feedbackList.innerHTML = '<li>Excellent! No vulnerabilities detected.</li>';
        } else {
            feedback.forEach(item => {
                const li = document.createElement('li');
                let iconClass = 'fa-circle-info';
                let iconColor = 'var(--medium-color)';
                
                if (item.includes("Great") || item.includes("Looks good")) {
                    iconClass = 'fa-check-circle'; iconColor = 'var(--strong-color)';
                } else if (strength === 'Weak') {
                    iconClass = 'fa-triangle-exclamation'; iconColor = 'var(--weak-color)';
                }
                
                li.innerHTML = `<i class="fa-solid ${iconClass}" style="color: ${iconColor}; margin-right: 8px;"></i> <span>${item}</span>`;
                li.style.display = 'flex';
                li.style.alignItems = 'flex-start';
                feedbackList.appendChild(li);
            });
        }
    }

    function updateBadge(el, count) {
        el.querySelector('.count').textContent = count;
        count > 0 ? el.classList.add('active') : el.classList.remove('active');
    }

    // --- Form Submission (Auth) ---
    function showMessage(msg, isSuccess) {
        authMessage.textContent = msg;
        authMessage.className = `message ${isSuccess ? 'success' : 'error'}`;
        authMessage.classList.remove('hidden');
    }

    submitBtn.addEventListener('click', async () => {
        const username = usernameInput.value;
        const password = passwordInput.value;
        
        if (!username || !password) {
            showMessage('Please enter both username and password', false);
            return;
        }

        const endpoint = isLoginMode ? '/api/login' : '/api/register';
        const payload = { username, password };
        
        if (isLoginMode) {
            payload.keystrokes = calculateBiometricsFeatures();
        }

        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            
            if (isLoginMode) {
                if (data.status === "SUSPICIOUS") {
                    otpModal.classList.remove('hidden');
                    document.querySelector('#otp-modal p').textContent = data.message;
                    resetBiometrics();
                } else if (data.success) {
                    showMessage(data.message, true);
                    // Optional: transition to a "Logged In" screen
                } else {
                    showMessage(data.message, false);
                }
            } else {
                showMessage(data.message, data.success);
            }
            
        } catch (err) {
            showMessage('System error during authentication', false);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = isLoginMode ? 'Login' : 'Register';
        }
    });

    // --- OTP Verification ---
    verifyOtpBtn.addEventListener('click', async () => {
        const otp = otpInput.value;
        verifyOtpBtn.disabled = true;
        
        try {
            const response = await fetch('/api/verify_otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ otp })
            });
            const data = await response.json();
            
            otpMessage.classList.remove('hidden');
            otpMessage.textContent = data.message;
            otpMessage.className = `message ${data.success ? 'success' : 'error'}`;
            
            if (data.success) {
                setTimeout(() => {
                    otpModal.classList.add('hidden');
                    showMessage("Access Granted with secondary verification.", true);
                    otpMessage.classList.add('hidden');
                    otpInput.value = '';
                }, 1500);
            }
        } finally {
            verifyOtpBtn.disabled = false;
        }
    });
});
