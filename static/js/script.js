document.addEventListener('DOMContentLoaded', function() {
    const serviceGrid = document.getElementById('serviceGrid');
    const inputSection = document.getElementById('inputSection');
    const serviceTitle = document.getElementById('serviceTitle');
    const serviceFields = document.getElementById('serviceFields');
    const serviceForm = document.getElementById('serviceForm');
    const submitBtn = document.getElementById('submitBtn');
    const backBtn = document.getElementById('backBtn');
    const processing = document.getElementById('processing');
    const results = document.getElementById('results');
    const responseContent = document.getElementById('responseContent');
    const progressLog = document.getElementById('progressLog');
    const agentStatus = document.getElementById('agentStatus');
    const exportBtn = document.getElementById('exportBtn');
    const copyBtn = document.getElementById('copyBtn');
    const newRequestBtn = document.getElementById('newRequestBtn');

    let selectedService = null;
    
    // Client-side event filtering state
    let eventQueue = [];
    let debounceTimer = null;
    const DEBOUNCE_INTERVAL = 5000; // 5 seconds

    // Automatic sensor simulation state
    let sensorIntervalId = null;
    const SENSOR_SIMULATION_INTERVAL = 15000; // 15 seconds

    // Service field configurations
    const serviceFieldsConfig = {
        'perceive': [
            { name: 'sensor_data', label: 'Sensor Data', type: 'textarea', 
              placeholder: 'e.g., Accelerometer: x=0.5, y=-0.3, z=9.8, GPS: lat=28.6, long=77.2, Audio: 45dB',
              required: true }
        ],
        'reason': [
            { name: 'context_data', label: 'Context Data', type: 'textarea', 
              placeholder: 'Describe the current context...', required: true }
        ],
        'act': [
            { name: 'action_request', label: 'Action Request', type: 'textarea', 
              placeholder: 'What action would you like to automate?', required: true }
        ],
        'monitor': [
            { name: 'health_data', label: 'Health Data', type: 'textarea', 
              placeholder: 'e.g., Steps: 5000, Sleep: 6 hours, Activity: Walking',
              required: true }
        ]
    };

    // Load models
    async function loadModels() {
        try {
            const response = await fetch('/api/models');
            const data = await response.json();
            
            const modelList = document.getElementById('modelList');
            modelList.innerHTML = '';
            
            if (data.status === 'success') {
                const models = data.models;
                const allModels = [models.primary, ...models.fallbacks];
                
                allModels.forEach(model => {
                    if (model && model.trim()) {
                        const div = document.createElement('div');
                        div.className = 'model-item';
                        const isAvailable = models.available.includes(model);
                        if (!isAvailable) {
                            div.classList.add('unavailable');
                        }
                        div.textContent = `${model} ${isAvailable ? '✅' : '❌'}`;
                        modelList.appendChild(div);
                    }
                });
            }
        } catch (error) {
            console.error('Error loading models:', error);
            document.getElementById('modelList').innerHTML = '⚠️ Failed to load models';
        }
    }

    // Service card click
    serviceGrid.addEventListener('click', function(e) {
        const card = e.target.closest('.service-card');
        if (!card) return;
        
        const service = card.dataset.service;
        selectedService = service;
        
        document.querySelectorAll('.service-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        
        inputSection.classList.remove('hidden');
        serviceTitle.textContent = `${card.querySelector('.service-icon').textContent} ${card.querySelector('h3').textContent}`;
        
        generateFields(service);
        inputSection.scrollIntoView({ behavior: 'smooth' });
    });

    function generateFields(service) {
        const fields = serviceFieldsConfig[service] || [];
        serviceFields.innerHTML = '';
        
        const languageSelect = document.getElementById('languageSelect');
        
        fields.forEach(field => {
            const div = document.createElement('div');
            div.className = 'form-group';
            
            const label = document.createElement('label');
            label.textContent = field.label;
            label.htmlFor = field.name;
            
            let input;
            if (field.type === 'textarea') {
                input = document.createElement('textarea');
                input.id = field.name;
                input.name = field.name;
                input.placeholder = field.placeholder || '';
                input.rows = 4;
            } else {
                input = document.createElement('input');
                input.type = field.type;
                input.id = field.name;
                input.name = field.name;
                input.placeholder = field.placeholder || '';
            }
            
            if (field.required) {
                input.required = true;
            }
            
            div.appendChild(label);
            div.appendChild(input);
            serviceFields.appendChild(div);
        });
    }

    backBtn.addEventListener('click', function() {
        inputSection.classList.add('hidden');
        results.classList.add('hidden');
        processing.classList.add('hidden');
        document.querySelectorAll('.service-card').forEach(c => c.classList.remove('active'));
        selectedService = null;
    });

    serviceForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!selectedService) return;
        
        const formData = new FormData(serviceForm);
        const data = {
            service_type: selectedService,
            language: document.getElementById('languageSelect').value,
            user_id: 'user_123'
        };
        
        const fields = serviceFieldsConfig[selectedService] || [];
        fields.forEach(field => {
            const value = formData.get(field.name);
            if (value) {
                data[field.name] = value;
            }
        });

    // For 'perceive' service, use the event queue
    if (selectedService === 'perceive') {
        handleSensorEvent(data.sensor_data);
        // Prevent form from submitting directly, handleSensorEvent will do it
        return;
    }

        
        processing.classList.remove('hidden');
        results.classList.add('hidden');
        progressLog.innerHTML = '';
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
        agentStatus.textContent = '⏳ AI Agent: Starting...';
        
    // For other services, process immediately
    processRequest(data);
});

function handleSensorEvent(sensorData) {
    if (!sensorData) return;

    addLog(`📥 Event received. Queued for batching.`);
    eventQueue.push(sensorData);

    // Reset the debounce timer
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        if (eventQueue.length > 0) {
            addLog(`⏳ Debounce timer expired. Sending batch of ${eventQueue.length} events.`);
            const batchedData = eventQueue.join('\n');
            eventQueue = []; // Clear the queue

            const data = {
                service_type: 'perceive',
                language: document.getElementById('languageSelect').value,
                user_id: 'user_123', // This should be a persistent user ID
                sensor_data: batchedData
            };
            processRequest(data);
        }
    }, DEBOUNCE_INTERVAL);
}

async function processRequest(data) {
    processing.classList.remove('hidden');
    results.classList.add('hidden');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';
    agentStatus.textContent = '⏳ AI Agent: Starting...';
    
    try {
        agentStatus.textContent = '🤖 AI Agent: Processing...';
        addLog('📤 Sending request to AI agents...');
        
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        displayApiResponse(response, result);

    } catch (error) {
        handleApiError(error);
    } finally {
        resetUI();
    }
}

    function addLog(message) {
        const logEntry = document.createElement('div');
        logEntry.textContent = `🔄 ${new Date().toLocaleTimeString()}: ${message}`;
        progressLog.appendChild(logEntry);
        progressLog.scrollTop = progressLog.scrollHeight;
    }

    function displayApiResponse(response, result) {
        if (response.ok && (result.status === 'success' || result.status === 'accepted')) {
            agentStatus.textContent = '✅ AI Agent: Complete!';
            addLog('✅ Processing completed successfully!');
            if (result.result) {
                displayResponse(result);
                // Check for actions that need to be spoken
                const actions = result.result.actions;
                if (actions && actions.includes("type: 'voice_reminder'") || actions.includes("type: 'critical_alert'") || actions.includes("type: 'voice_suggestion'")) {
                    // A simple way to extract the content to be spoken.
                    const contentMatch = actions.match(/content: '(.*?)'/);
                    if (contentMatch && contentMatch[1]) speak(contentMatch[1]);
                }
            } else {
                addLog(`Job enqueued with ID: ${result.job_id}`);
            }
        } else {
            agentStatus.textContent = '❌ AI Agent: Error';
            addLog(`❌ Error: ${result.error || 'Unknown error'}`);
            alert(`Error: ${result.error || 'Failed to process request'}`);
        }
    }

    function handleApiError(error) {
        console.error('Error:', error);
        agentStatus.textContent = '❌ AI Agent: Network Error';
        addLog(`❌ Network error: ${error.message}`);
        alert('Error processing request. Please try again.');
    }

    function displayResponse(result) {
        results.classList.remove('hidden');
        
        let html = '';
        const responseData = result.result;
        
        if (responseData) {
            html += `<h2>📋 Processing Results</h2>`;
            html += `<p><strong>User ID:</strong> ${responseData.user_id || 'N/A'}</p>`;
            html += `<p><strong>Status:</strong> ${responseData.status || 'N/A'}</p>`;
            html += `<p><strong>Timestamp:</strong> ${new Date(responseData.timestamp).toLocaleString()}</p>`;
            html += `<hr>`;
            
            if (responseData.perception) {
                html += `<h3>📱 Perception Analysis</h3>`;
                html += `<div>${formatContent(responseData.perception)}</div>`;
            }
            
            if (responseData.reasoning) {
                html += `<h3>🧠 Reasoning</h3>`;
                html += `<div>${formatContent(responseData.reasoning)}</div>`;
            }
            
            if (responseData.actions) {
                html += `<h3>⚡ Actions</h3>`;
                html += `<div>${formatContent(responseData.actions)}</div>`;
            }
            
            if (responseData.context) {
                html += `<h3>📊 Context Update</h3>`;
                html += `<div>${formatContent(responseData.context)}</div>`;
            }
        }
        
        responseContent.innerHTML = html;
        results.scrollIntoView({ behavior: 'smooth' });
    }

    function resetUI() {
        processing.classList.add('hidden');
        submitBtn.disabled = false;
        submitBtn.textContent = '🚀 Process';
    }

    function formatContent(text) {
        if (!text) return '';
        
        let html = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/^#### (.*$)/gm, '<h4>$1</h4>')
            .replace(/^\* (.*$)/gm, '<li>$1</li>')
            .replace(/^- (.*$)/gm, '<li>$1</li>')
            .replace(/\n/g, '<br>');
        
        html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
        
        return html;
    }

    function speak(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = document.getElementById('languageSelect').value;
            window.speechSynthesis.speak(utterance);
            addLog(`🔊 Speaking: "${text}"`);
        } else {
            addLog('⚠️ Text-to-speech not supported in this browser.');
            alert(text); // Fallback for browsers without speech synthesis
        }
    }

    // Export
    exportBtn.addEventListener('click', function() {
        const content = responseContent.textContent;
        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `robot_results_${new Date().toISOString().slice(0,10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    });

    // Copy
    copyBtn.addEventListener('click', function() {
        const text = responseContent.textContent;
        navigator.clipboard.writeText(text).then(() => {
            const original = this.textContent;
            this.textContent = '✅ Copied!';
            setTimeout(() => {
                this.textContent = original;
            }, 2000);
        }).catch(() => {
            const range = document.createRange();
            range.selectNode(responseContent);
            window.getSelection().removeAllRanges();
            window.getSelection().addRange(range);
            document.execCommand('copy');
            const original = this.textContent;
            this.textContent = '✅ Copied!';
            setTimeout(() => {
                this.textContent = original;
            }, 2000);
        });
    });

    // New request
    newRequestBtn.addEventListener('click', function() {
        results.classList.add('hidden');
        inputSection.scrollIntoView({ behavior: 'smooth' });
    });

    // --- Automatic Sensor Simulation ---
    function simulateSensorData() {
        const activities = [
            "Accelerometer: x=0.1, y=-0.2, z=9.8, GPS: lat=34.05, long=-118.2, Audio: 40dB, Light: 300lux. User appears to be sitting indoors.",
            "Accelerometer: x=1.5, y=-2.3, z=8.8, GPS: lat=34.06, long=-118.2, Audio: 65dB, Light: 1500lux. User appears to be walking outside.",
            "Accelerometer: x=0.0, y=9.8, z=0.1, GPS: lat=34.05, long=-118.2, Audio: 30dB, Light: 10lux. User appears to be lying down, likely sleeping.",
            "Accelerometer: x=8.5, y=-10.3, z=15.8, GPS: lat=34.05, long=-118.2, Audio: 55dB, Light: 250lux. SUDDEN HIGH MOVEMENT - POSSIBLE FALL."
        ];
        // Pick a random activity, but favor normal ones
        const isFall = Math.random() > 0.95; // 5% chance of a fall event
        const data = isFall ? activities[3] : activities[Math.floor(Math.random() * 3)];
        
        addLog(`🤖 Auto-sensor triggered. Data: "${data.substring(0, 50)}..."`);
        handleSensorEvent(data);
    }

    function initializeAutoSensing() {
        const controls = document.querySelector('.controls');
        if (controls) {
            controls.insertAdjacentHTML('beforeend', `<div class="toggle-switch"><input type="checkbox" id="autoSensorToggle"><label for="autoSensorToggle">Enable Auto-Sensing</label></div>`);
            
            const autoSensorToggle = document.getElementById('autoSensorToggle');
            autoSensorToggle.addEventListener('change', function() {
                if (this.checked) {
                    if (!sensorIntervalId) {
                        addLog('🟢 Automatic sensing enabled.');
                        // Immediately trigger once, then start interval
                        simulateSensorData();
                        sensorIntervalId = setInterval(simulateSensorData, SENSOR_SIMULATION_INTERVAL);
                    }
                } else {
                    if (sensorIntervalId) {
                        clearInterval(sensorIntervalId);
                        sensorIntervalId = null;
                        addLog('🔴 Automatic sensing disabled.');
                    }
                }
            });
        } else {
            console.error("Could not find '.controls' element to attach the auto-sensing toggle.");
        }
    }

    // Initialize
    loadModels();
    initializeAutoSensing();
    console.log('🤖 Smartphone Robot Assistant loaded successfully!');
});

// Add a toggle to the HTML to control the simulation
document.addEventListener('DOMContentLoaded', () => {
    const controls = document.querySelector('.controls');
    if (controls) {
        controls.insertAdjacentHTML('beforeend', `<div class="toggle-switch"><input type="checkbox" id="autoSensorToggle"><label for="autoSensorToggle">Enable Auto-Sensing</label></div>`);
    } else {
        console.error("Could not find '.controls' element to attach the auto-sensing toggle.");
    }
});
            }
        } else {
            if (sensorIntervalId) {
                clearInterval(sensorIntervalId);
                sensorIntervalId = null;
                addLog('🔴 Automatic sensing disabled.');
            }
        }
    });

    // Initialize
    loadModels();
    console.log('🤖 Smartphone Robot Assistant loaded successfully!');
});

// Add a toggle to the HTML to control the simulation
document.addEventListener('DOMContentLoaded', () => {
    const controls = document.querySelector('.controls');
    controls.insertAdjacentHTML('beforeend', `<div class="toggle-switch"><input type="checkbox" id="autoSensorToggle"><label for="autoSensorToggle">Enable Auto-Sensing</label></div>`);
});