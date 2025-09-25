// Global variables
let isResearching = false;
let currentReport = '';

// DOM elements - Fixed to match actual HTML IDs
const researchTopicInput = document.getElementById('research-topic');
const researchButton = document.getElementById('research-btn');
const reportContainer = document.getElementById('results-section');
const downloadButton = document.getElementById('download-btn');
const statusContainer = document.getElementById('status-section');
const statusTitle = document.getElementById('status-title');
const statusDescription = document.getElementById('status-description');

// Event listeners
researchButton.addEventListener('click', startResearch);
downloadButton.addEventListener('click', downloadReport);

// Allow Enter key to start research
researchTopicInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !isResearching) {
        startResearch();
    }
});

// Input validation
researchTopicInput.addEventListener('input', () => {
    const topic = researchTopicInput.value.trim();
    researchButton.disabled = !topic || isResearching;
});

// Initialize
updateUIState('idle');

// Force CSS reload to prevent caching issues
function forceCSSReload() {
    const links = document.querySelectorAll('link[rel="stylesheet"]');
    links.forEach(link => {
        const href = link.href.split('?')[0];
        link.href = href + '?v=' + Date.now();
    });
}

// Call this on page load to ensure fresh CSS
window.addEventListener('load', forceCSSReload);

function showElement(element) {
    if (!element) return;
    element.classList.remove('hidden');
}

function hideElement(element) {
    if (!element) return;
    element.classList.add('hidden');
}

async function startResearch() {
    const topic = researchTopicInput.value.trim();

    if (!topic || isResearching) {
        return;
    }

    isResearching = true;
    updateUIState('researching');

    try {
        const response = await fetch('/api/research', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Research failed');
        }

        // Indicate gathering phase while waiting for JSON parsing
        updateUIState('gathering');

        const data = await response.json();

        if (data.status === 'success') {
            currentReport = data.report;
            updateUIState('success');
        } else if (data.status === 'queued') {
            await pollQueueStatus(data.session_id, data.queue_position);
        }

    } catch (error) {
        console.error('Research error:', error);
        updateUIState('error', error.message);
    } finally {
        isResearching = false;
    }
}

async function pollQueueStatus(sessionId, initialQueuePosition) {
    let queuePosition = initialQueuePosition;
    let attempts = 0;
    const maxAttempts = 300; // 5 minutes max

    const poll = async () => {
        try {
            const response = await fetch(`/api/queue-status/${sessionId}`);

            if (!response.ok) {
                throw new Error('Failed to get queue status');
            }

            const status = await response.json();

            if (status.status === 'completed') {
                currentReport = status.result;
                updateUIState('success');
                return;
            } else if (status.status === 'failed') {
                throw new Error(status.error || 'Research failed');
            } else if (status.status === 'processing') {
                updateUIState('processing', `Processing your request...`);
            } else if (status.status === 'queued') {
                queuePosition = status.queue_position;
                const waitTime = Math.ceil(status.estimated_wait_time / 60);
                updateUIState('queued', `Position ${queuePosition} in queue. Estimated wait: ${waitTime} minutes`);
            }

            attempts++;
            if (attempts < maxAttempts) {
                setTimeout(poll, 2000); // Poll every 2 seconds
            } else {
                throw new Error('Request timed out');
            }

        } catch (error) {
            console.error('Queue polling error:', error);
            updateUIState('error', error.message);
        }
    };

    // Start polling
    poll();
}

function updateUIState(state, message = '') {
    const spinner = document.querySelector('.spinner');
    const buttonText = document.querySelector('.button-text');
    
    const setSpinner = (visible) => {
        if (!spinner) return;
        if (visible) {
            spinner.classList.remove('hidden');
        } else {
            spinner.classList.add('hidden');
        }
    };
    
    switch (state) {
        case 'idle':
            researchButton.disabled = !researchTopicInput.value.trim();
            buttonText.textContent = 'Start Research';
            setSpinner(false);
            hideElement(reportContainer);
            hideElement(statusContainer);
            hideElement(downloadButton);
            hideElement(document.getElementById('error-section'));
            break;
            
        case 'researching':
            researchButton.disabled = true;
            buttonText.textContent = 'Researching...';
            setSpinner(true);
            hideElement(reportContainer);
            hideElement(downloadButton);
            hideElement(document.getElementById('error-section'));
            if (statusContainer) {
                showElement(statusContainer);
                if (statusTitle) statusTitle.textContent = 'Creating Research Plan';
                if (statusDescription) statusDescription.textContent = 'We are drafting the research plan for your topic.';
            }
            break;
            
        case 'gathering':
            researchButton.disabled = true;
            buttonText.textContent = 'Researching...';
            setSpinner(true);
            hideElement(reportContainer);
            hideElement(downloadButton);
            hideElement(document.getElementById('error-section'));
            if (statusContainer) {
                showElement(statusContainer);
                if (statusTitle) statusTitle.textContent = 'Gathering Information';
                if (statusDescription) statusDescription.textContent = message || 'Collecting the most relevant sources and insights...';
            }
            break;
            
        case 'success':
            researchButton.disabled = false;
            buttonText.textContent = 'Start Research';
            setSpinner(false);
            showElement(reportContainer);
            showElement(downloadButton);
            hideElement(statusContainer);
            hideElement(document.getElementById('error-section'));
            displayReport(currentReport);
            break;
            
        case 'error':
            researchButton.disabled = false;
            buttonText.textContent = 'Start Research';
            setSpinner(false);
            hideElement(reportContainer);
            hideElement(downloadButton);
            showElement(document.getElementById('error-section'));
            hideElement(statusContainer);
            if (statusDescription && statusContainer) {
                showElement(statusContainer);
                if (statusTitle) statusTitle.textContent = 'Research Failed';
                statusDescription.textContent = message;
            }
            break;
            
        case 'processing':
            researchButton.disabled = true;
            buttonText.textContent = 'Processing...';
            setSpinner(true);
            hideElement(reportContainer);
            hideElement(downloadButton);
            hideElement(document.getElementById('error-section'));
            if (statusContainer) {
                showElement(statusContainer);
                if (statusTitle) statusTitle.textContent = 'Finalizing Report';
                if (statusDescription) statusDescription.textContent = message || 'Finalizing your research report...';
            }
            break;
    }
}

function displayReport(report) {
    const reportContent = document.getElementById('report-content');
    const formattedReport = formatReport(report);
    reportContent.innerHTML = formattedReport;
}

function formatReport(report) {
    if (!report) return '';
    
    // Clean up the report by removing markdown symbols
    let cleanReport = report.replace(/#+/g, '');
    
    // Ensure main sections are on their own lines
    const mainSections = ['Executive Summary', 'Introduction', 'Key Findings', 'Conclusion', 'Thesis'];
    mainSections.forEach(section => {
        // Replace inline section headers with proper line breaks
        cleanReport = cleanReport.replace(new RegExp(`(?<!\\n)${section}(?!\\n)`, 'g'), `\n\n${section}\n\n`);
    });
    
    // Split by double line breaks to get sections
    const sections = cleanReport.split(/\n\s*\n/);
    
    let sectionCounter = 1;
    
    return sections.map(section => {
        const trimmedSection = section.trim();
        if (!trimmedSection) return '';
        
        // Check if it's a main section header (exact match)
        if (mainSections.includes(trimmedSection)) {
            const numberedHeader = `${sectionCounter}. ${trimmedSection}`;
            sectionCounter++;
            return `<h1>${numberedHeader}</h1>`;
        }
        
        // Check if it starts with a main section header followed by content
        for (const header of mainSections) {
            if (trimmedSection.startsWith(header)) {
                const remainingText = trimmedSection.substring(header.length).trim();
                const numberedHeader = `${sectionCounter}. ${header}`;
                sectionCounter++;
                
                if (remainingText) {
                    // Split the header from the content and handle multiple paragraphs
                    const contentParagraphs = remainingText.split(/\n\s*\n/);
                    const formattedContent = contentParagraphs.map(para => {
                        if (para.trim()) {
                            return `<p>${formatMarkdownText(para.trim())}</p>`;
                        }
                        return '';
                    }).join('');
                    return `<h1>${numberedHeader}</h1>${formattedContent}`;
                } else {
                    return `<h1>${numberedHeader}</h1>`;
                }
            }
        }
        
        // Regular paragraph content
        return `<p>${formatMarkdownText(trimmedSection)}</p>`;
    }).join('');
}

function formatMarkdownText(text) {
    if (!text) return '';
    
    // Convert bold text
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert italic text
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Convert bullet points
    const lines = text.split('\n');
    const formattedLines = [];
    let inList = false;
    
    for (const line of lines) {
        const stripped = line.trim();
        if (stripped.startsWith('- ')) {
            if (!inList) {
                formattedLines.push('<ul>');
                inList = true;
            }
            formattedLines.push(`<li>${stripped.substring(2)}</li>`);
        } else {
            if (inList) {
                formattedLines.push('</ul>');
                inList = false;
            }
            if (stripped) {
                formattedLines.push(`<p>${stripped}</p>`);
            }
        }
    }
    
    if (inList) {
        formattedLines.push('</ul>');
    }
    
    return formattedLines.join('');
}

function downloadReport() {
    if (!currentReport) {
        showToast('No report available to download', 'error');
        return;
    }

    const topic = document.getElementById('research-topic').value.trim() || 'Research Report';
    generatePdfOnServer(topic, currentReport);
}

async function generatePdfOnServer(topic, report) {
    try {
        showToast('Generating PDF...', 'success');
        const response = await fetch('/api/download-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic, report }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to generate PDF');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const filename = `${topic.replace(/[^a-z0-9]/gi, '_').toLowerCase() || 'research_report'}.pdf`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        showToast('PDF downloaded successfully!', 'success');
    } catch (error) {
        console.error('Server PDF generation error:', error);
        showToast(error.message || 'Failed to generate PDF.', 'error');
    }
}

function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Style the toast
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#f44336' : type === 'success' ? '#4caf50' : type === 'warning' ? '#ff9800' : '#2196f3'};
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 1000;
        font-size: 14px;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    // Add to page
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}