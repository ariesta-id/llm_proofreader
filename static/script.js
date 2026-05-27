document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    lucide.createIcons();

    // DOM Elements
    const textInput = document.getElementById('text-input');
    const charCount = document.getElementById('char-count');
    const proofreadBtn = document.getElementById('proofread-btn');
    const btnText = proofreadBtn.querySelector('.btn-text');
    const btnIcon = proofreadBtn.querySelector('.btn-icon');
    const btnLoader = proofreadBtn.querySelector('.btn-loader');
    
    const resultsPanel = document.getElementById('results-panel');
    const resultsContent = document.getElementById('results-content');
    const emptyState = document.getElementById('empty-state');
    
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    const polishedOutput = document.getElementById('polished-output');
    const correctionsList = document.getElementById('corrections-list');
    const feedbackText = document.getElementById('feedback-text');
    const correctionsCountBadge = document.getElementById('corrections-count');
    
    const metricTone = document.getElementById('metric-tone');
    const metricCorrections = document.getElementById('metric-corrections');
    const metricChars = document.getElementById('metric-chars');
    
    const copyBtn = document.getElementById('copy-btn');
    const copyBtnText = document.getElementById('copy-btn-text');
    const toast = document.getElementById('toast');

    // State Variables
    let proofreadResult = null;

    /* ==========================================================================
       Character Counter
       ========================================================================== */
    textInput.addEventListener('input', () => {
        const length = textInput.value.length;
        charCount.textContent = length;
        if (metricChars) metricChars.textContent = length;
        
        if (length > 2000) {
            textInput.value = textInput.value.substring(0, 2000);
            charCount.textContent = 2000;
            if (metricChars) metricChars.textContent = 2000;
        }
    });

    /* ==========================================================================
       Tab Switching Logic
       ========================================================================== */
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            
            // Toggle active class on buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Toggle active class on tab contents
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `tab-${targetTab}`) {
                    content.classList.add('active');
                }
            });
        });
    });

    /* ==========================================================================
       Highlight Diff Rendering Logic
       ========================================================================== */
    function generatePolishedDiff(original, corrected) {
        // Tokenize text into words, whitespace, and punctuation groups
        const tokenize = (text) => text.split(/(\s+|[.,!?;:"'()\[\]{}]+)/).filter(Boolean);
        
        const tokens1 = tokenize(original);
        const tokens2 = tokenize(corrected);
        
        const m = tokens1.length;
        const n = tokens2.length;
        
        // DP table for Longest Common Subsequence
        const dp = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0));
        
        for (let i = 1; i <= m; i++) {
            for (let j = 1; j <= n; j++) {
                if (tokens1[i - 1].toLowerCase().trim() === tokens2[j - 1].toLowerCase().trim()) {
                    dp[i][j] = dp[i - 1][j - 1] + 1;
                } else {
                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                }
            }
        }
        
        // Backtrack to assemble the highlighted polished text
        let i = m, j = n;
        const diff = [];
        
        while (i > 0 || j > 0) {
            if (i > 0 && j > 0 && tokens1[i - 1].toLowerCase().trim() === tokens2[j - 1].toLowerCase().trim()) {
                // Token is unchanged; use the corrected token to preserve capitalization/punctuation
                diff.push(escapeHtml(tokens2[j - 1]));
                i--;
                j--;
            } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
                // Token was added or modified in the corrected version
                const token = tokens2[j - 1];
                if (token.trim() === '') {
                    diff.push(token); // Don't highlight pure whitespace
                } else {
                    diff.push(`<ins class="diff-highlight">${escapeHtml(token)}</ins>`);
                }
                j--;
            } else {
                // Token was deleted from the original version
                // We omit deletions from the polished text to keep it clean and ready to copy
                i--;
            }
        }
        
        return diff.reverse().join('');
    }

    /* ==========================================================================
       Proofreading Request API Call
       ========================================================================== */
    proofreadBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        if (!text) {
            alert('Please enter some text to proofread.');
            return;
        }

        // Set Loading State
        proofreadBtn.disabled = true;
        btnText.classList.add('hidden');
        btnIcon.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        
        try {
            const response = await fetch('/api/proofread', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to proofread text.');
            }

            proofreadResult = await response.json();
            
            // Render Results
            renderResults(proofreadResult);

        } catch (error) {
            console.error(error);
            alert(`Error: ${error.message}`);
        } finally {
            // Restore Button State
            proofreadBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnIcon.classList.remove('hidden');
            btnLoader.classList.add('hidden');
        }
    });

    /* ==========================================================================
       DOM Rendering
       ========================================================================== */
    function renderResults(result) {
        // Remove empty state and reveal results content
        resultsPanel.classList.remove('empty');
        emptyState.classList.add('hidden');
        resultsContent.classList.remove('hidden');

        // Set Polished Output
        const diffHtml = generatePolishedDiff(result.original_text, result.corrected_text);
        polishedOutput.innerHTML = diffHtml;

        // Set Metric Info Sidebar
        if (metricCorrections) metricCorrections.textContent = result.corrections.length;
        correctionsCountBadge.textContent = result.corrections.length;
        
        // Simple heuristic for tone
        let tone = 'Formal';
        const lowercaseText = result.original_text.toLowerCase();
        if (lowercaseText.includes("hey") || lowercaseText.includes("cool") || lowercaseText.includes("stuff") || lowercaseText.includes("y'all")) {
            tone = 'Informal';
        }
        if (metricTone) metricTone.textContent = tone;

        // Generate Corrections List
        correctionsList.innerHTML = '';
        if (result.corrections.length === 0) {
            correctionsList.innerHTML = `
                <div class="empty-state">
                    <i data-lucide="check-circle" style="color: var(--cat-other); width: 48px; height: 48px;"></i>
                    <h3>Perfect writing!</h3>
                    <p>No grammar or spelling improvements were needed.</p>
                </div>
            `;
        } else {
            result.corrections.forEach((corr, index) => {
                const categoryClass = corr.category.toLowerCase();
                const card = document.createElement('div');
                card.className = `correction-card ${categoryClass}`;
                card.innerHTML = `
                    <div class="card-header">
                        <span class="category-tag">${corr.category}</span>
                        <span class="badge">#${index + 1}</span>
                    </div>
                    <div class="diff-view">
                        <span class="diff-original">${escapeHtml(corr.original_phrase)}</span>
                        <span class="diff-arrow">&rarr;</span>
                        <span class="diff-corrected">${escapeHtml(corr.corrected_phrase)}</span>
                    </div>
                    <div class="card-explanation">
                        ${escapeHtml(corr.explanation)}
                    </div>
                `;
                correctionsList.appendChild(card);
            });
        }

        // Set Feedback Tab
        feedbackText.textContent = result.overall_feedback;

        // Reset active tab to 'polished'
        document.querySelector('[data-tab="polished"]').click();

        // Refresh Lucide Icons inside dynamic elements
        lucide.createIcons();
    }

    /* ==========================================================================
       Copy To Clipboard Logic
       ========================================================================== */
    copyBtn.addEventListener('click', () => {
        if (!proofreadResult) return;
        
        navigator.clipboard.writeText(proofreadResult.corrected_text).then(() => {
            // Show Success toast
            toast.classList.remove('hidden');
            setTimeout(() => {
                toast.classList.add('hidden');
            }, 2500);

            // Change button state temporarily
            copyBtnText.textContent = 'Copied!';
            copyBtn.style.borderColor = 'rgba(16, 185, 129, 0.4)';
            setTimeout(() => {
                copyBtnText.textContent = 'Copy to Clipboard';
                copyBtn.style.borderColor = 'var(--panel-border)';
            }, 2000);
        }).catch(err => {
            console.error('Could not copy text: ', err);
        });
    });

    // Helper functions
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
