// DOM elements
const researchTopicInput = document.getElementById('research-topic');
const researchButton = document.getElementById('research-btn');
const buttonText = document.querySelector('.button-text');
const spinner = document.querySelector('.spinner');
const statusSection = document.getElementById('status-section');
const resultsSection = document.getElementById('results-section');
const reportContent = document.getElementById('report-content');
const errorSection = document.getElementById('error-section');
const errorMessage = document.getElementById('error-message');
const copyButton = document.getElementById('copy-btn');
const downloadButton = document.getElementById('download-btn');
const retryButton = document.getElementById('retry-btn');

// State management
let currentReport = '';
let isResearching = false;

// Event listeners
researchButton.addEventListener('click', startResearch);
retryButton.addEventListener('click', startResearch);
copyButton.addEventListener('click', copyReport);
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

// Initialize button state
researchButton.disabled = true;

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
        
        const data = await response.json();
        currentReport = data.report;
        updateUIState('success');
        
    } catch (error) {
        console.error('Research error:', error);
        updateUIState('error', error.message);
    } finally {
        isResearching = false;
    }
}

function updateUIState(state, errorMsg = '') {
    // Hide all sections first
    statusSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    
    // Update button state based on current state
    if (state === 'researching') {
        researchButton.disabled = true;
        buttonText.textContent = 'Researching...';
        spinner.classList.remove('hidden');
    } else {
        // For success or error, stop the loading state
        isResearching = false;
        researchButton.disabled = false;
        buttonText.textContent = 'Start Research';
        spinner.classList.add('hidden');
    }
    
    switch (state) {
        case 'researching':
            statusSection.classList.remove('hidden');
            break;
            
        case 'success':
            resultsSection.classList.remove('hidden');
            displayReport(currentReport);
            break;
            
        case 'error':
            errorSection.classList.remove('hidden');
            errorMessage.textContent = errorMsg;
            break;
    }
}

function displayReport(report) {
    // Format the report with proper HTML structure
    const formattedReport = formatReport(report);
    reportContent.innerHTML = formattedReport;
}

function formatReport(report) {
    // First, let's clean up the report text and ensure proper section separation
    let cleanReport = report;
    
    // Remove any # symbols and clean up the text
    cleanReport = cleanReport.replace(/#+/g, '');
    
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
    // Convert markdown formatting to HTML with academic styling
    let formatted = text;
    
    // Convert bold text **text** to <strong>text</strong>
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert italic text *text* to <em>text</em> (but not if it's already bold)
    formatted = formatted.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
    
    // Convert bullet points - item to <li>item</li>
    const lines = formatted.split('\n');
    const processedLines = [];
    let inList = false;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        // Check if line starts with bullet point
        if (line.match(/^\s*[-*+]\s+/)) {
            if (!inList) {
                processedLines.push('<ul>');
                inList = true;
            }
            const listItem = line.replace(/^\s*[-*+]\s+/, '');
            processedLines.push(`<li>${listItem}</li>`);
        } else {
            if (inList) {
                processedLines.push('</ul>');
                inList = false;
            }
            if (line.trim()) {
                processedLines.push(line);
            }
        }
    }
    
    // Close any remaining list
    if (inList) {
        processedLines.push('</ul>');
    }
    
    return processedLines.join('\n');
}

async function copyReport() {
    try {
        await navigator.clipboard.writeText(currentReport);
        showToast('Report copied to clipboard!');
    } catch (error) {
        console.error('Failed to copy:', error);
        showToast('Failed to copy report', 'error');
    }
}

function downloadReport() {
    if (!currentReport) {
        showToast('No report available to download', 'error');
        return;
    }
    
    const topic = document.getElementById('research-topic').value.trim() || 'Research Report';
    
    console.log('Using client-side PDF generation (no backend call)');
    showToast('Generating PDF using client-side method...', 'success');
    
    // Use client-side PDF generation (no backend call needed)
    generatePDFWithPrint(topic, currentReport);
}

function generatePDFWithJsPDF(topic, report) {
    try {
        showToast('Generating PDF...', 'success');
        
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        // Set up the document
        doc.setFont('helvetica');
        doc.setFontSize(20);
        doc.text(topic, 20, 30);
        
        doc.setFontSize(10);
        doc.text(`Generated on ${new Date().toLocaleDateString()}`, 20, 40);
        
        // Add a line
        doc.line(20, 45, 190, 45);
        
        // Process the report content
        const lines = doc.splitTextToSize(report, 170);
        let yPosition = 60;
        
        doc.setFontSize(12);
        
        for (let i = 0; i < lines.length; i++) {
            if (yPosition > 280) {
                doc.addPage();
                yPosition = 20;
            }
            
            // Check if line is a header
            if (lines[i].startsWith('# ')) {
                doc.setFontSize(16);
                doc.setFont('helvetica', 'bold');
                doc.text(lines[i].substring(2), 20, yPosition);
                yPosition += 10;
                doc.setFontSize(12);
                doc.setFont('helvetica', 'normal');
            } else if (lines[i].startsWith('## ')) {
                doc.setFontSize(14);
                doc.setFont('helvetica', 'bold');
                doc.text(lines[i].substring(3), 20, yPosition);
                yPosition += 8;
                doc.setFontSize(12);
                doc.setFont('helvetica', 'normal');
            } else if (lines[i].startsWith('### ')) {
                doc.setFontSize(13);
                doc.setFont('helvetica', 'bold');
                doc.text(lines[i].substring(4), 20, yPosition);
                yPosition += 7;
                doc.setFontSize(12);
                doc.setFont('helvetica', 'normal');
            } else {
                doc.text(lines[i], 20, yPosition);
                yPosition += 6;
            }
        }
        
        // Save the PDF
        const fileName = `${topic.replace(/[^a-zA-Z0-9]/g, '_')}_report.pdf`;
        doc.save(fileName);
        
        showToast('PDF downloaded successfully!', 'success');
        
    } catch (error) {
        console.error('jsPDF generation failed:', error);
        showToast('jsPDF failed, using print method...', 'error');
        generatePDFWithPrint(topic, report);
    }
}

function generatePDFWithPrint(topic, report) {
    try {
        showToast('Opening PDF preview...', 'success');
        
        // Create a new window for PDF generation
        const printWindow = window.open('', '_blank', 'width=800,height=600');
        
        // Generate PDF-ready HTML content
        const pdfContent = generatePDFContent(topic, report);
        
        printWindow.document.write(pdfContent);
        printWindow.document.close();
        
        // Wait for content to load, then trigger print dialog
        printWindow.onload = function() {
            setTimeout(() => {
                printWindow.print();
                showToast('PDF ready! Use "Save as PDF" in the print dialog.', 'success');
            }, 500);
        };
        
    } catch (error) {
        console.error('Print PDF generation failed:', error);
        showToast('Failed to generate PDF', 'error');
    }
}

function generatePDFContent(topic, report) {
    const formattedReport = formatReportForPDF(report);
    const currentDate = new Date().toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${topic} - Research Report</title>
    <style>
        @page {
            size: A4;
            margin: 2.5cm 2cm;
        }
        
        body {
            font-family: 'Times New Roman', 'Georgia', serif;
            line-height: 1.7;
            color: #2c3e50;
            margin: 0;
            padding: 0;
            background: white;
            font-size: 12pt;
        }
        
        .report-header {
            text-align: center;
            margin-bottom: 3rem;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 1rem;
        }
        
        .report-title {
            font-size: 18pt;
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: #1a202c;
            font-family: 'Arial', sans-serif;
        }
        
        .report-date {
            font-size: 10pt;
            color: #666;
            font-style: italic;
        }
        
        .report-content {
            margin-top: 1rem;
        }
        
        /* Academic heading styles */
        /* Section Headings - BOLD - 13pt */
        h1 {
            font-size: 13pt;
            font-weight: bold !important;
            color: #000000;
            margin-top: 1.5rem;
            margin-bottom: 0.8rem;
            text-align: left;
            border-bottom: 1pt solid #000000;
            padding-bottom: 0.3rem;
            font-family: 'Arial', sans-serif;
            display: block !important;
            clear: both !important;
        }
        
        h1:first-child {
            margin-top: 0;
        }
        
        /* Section Subheadings - BOLD - 12pt */
        h2 {
            font-size: 12pt;
            font-weight: bold !important;
            color: #000000;
            margin-top: 1.2rem;
            margin-bottom: 0.6rem;
            text-align: left;
            font-family: 'Arial', sans-serif;
            display: block !important;
            clear: both !important;
        }
        
        h3 {
            font-size: 12pt;
            font-weight: bold !important;
            color: #000000;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            text-align: left;
            font-family: 'Arial', sans-serif;
            display: block !important;
            clear: both !important;
        }
        
        /* Section Body - NOT BOLD - 11pt */
        p {
            margin-bottom: 1rem;
            text-align: justify;
            text-indent: 1.5rem;
            line-height: 1.6;
            font-size: 11pt;
            font-weight: normal !important;
            color: #000000;
            font-family: 'Times New Roman', 'Georgia', serif;
        }
        
        /* First paragraph after heading should not be indented */
        h1 + p,
        h2 + p,
        h3 + p {
            text-indent: 0;
        }
        
        /* Lists - NOT BOLD - 11pt */
        ul, ol {
            margin: 1rem 0;
            padding-left: 2rem;
            text-align: left;
            font-weight: normal !important;
            font-size: 11pt;
            font-family: 'Times New Roman', 'Georgia', serif;
        }
        
        ul {
            list-style-type: disc;
        }
        
        ol {
            list-style-type: decimal;
        }
        
        li {
            margin-bottom: 0.3rem;
            line-height: 1.6;
            font-size: 11pt;
            font-weight: normal !important;
            color: #000000;
            font-family: 'Times New Roman', 'Georgia', serif;
        }
        
        /* Text formatting */
        strong {
            font-weight: bold !important;
            color: #000000;
        }
        
        em {
            font-style: italic;
            color: #4a5568;
        }
        
        /* Page breaks */
        .page-break {
            page-break-before: always;
        }
        
        /* Print optimizations */
        @media print {
            body {
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }
            
            .no-print {
                display: none !important;
            }
            
            /* Ensure consistent margins */
            @page {
                margin: 2.5cm 2cm;
            }
        }
    </style>
</head>
<body>
    <div class="report-header">
        <div class="report-title">${topic}</div>
        <div class="report-date">Generated on ${currentDate}</div>
    </div>
    
    <div class="report-content">
        ${formattedReport}
    </div>
</body>
</html>`;
}

function formatReportForPDF(report) {
    // First, let's clean up the report text and ensure proper section separation
    let cleanReport = report;
    
    // Remove any # symbols and clean up the text
    cleanReport = cleanReport.replace(/#+/g, '');
    
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


function showToast(message, type = 'success') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Style the toast
    Object.assign(toast.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '8px',
        color: 'white',
        fontWeight: '500',
        zIndex: '1000',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease',
        backgroundColor: type === 'error' ? '#ef4444' : '#10b981',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    });
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after delay
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Utility function to debounce input
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add some visual feedback for long operations
function simulateProgress() {
    const progressFill = document.querySelector('.progress-fill');
    if (progressFill) {
        progressFill.style.animation = 'none';
        progressFill.offsetHeight; // Trigger reflow
        progressFill.style.animation = 'progress 3s ease-in-out infinite';
    }
}

// Initialize progress animation when status section is shown
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
            if (!statusSection.classList.contains('hidden')) {
                simulateProgress();
            }
        }
    });
});

observer.observe(statusSection, { attributes: true });

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to start research
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        startResearch();
    }
    
    // Escape to clear input
    if (e.key === 'Escape') {
        researchTopicInput.value = '';
        researchButton.disabled = true;
    }
});

// Add focus management for accessibility
researchTopicInput.addEventListener('focus', () => {
    researchTopicInput.parentElement.classList.add('focused');
});

researchTopicInput.addEventListener('blur', () => {
    researchTopicInput.parentElement.classList.remove('focused');
});

// Add loading state management
function setLoadingState(loading) {
    isResearching = loading;
    researchButton.disabled = loading || !researchTopicInput.value.trim();
    buttonText.textContent = loading ? 'Researching...' : 'Start Research';
    spinner.classList.toggle('hidden', !loading);
}

// Error handling for network issues
window.addEventListener('online', () => {
    showToast('Connection restored', 'success');
});

window.addEventListener('offline', () => {
    showToast('Connection lost', 'error');
});

// Force CSS reload for formatting changes
function forceCSSReload() {
    const links = document.querySelectorAll('link[rel="stylesheet"]');
    links.forEach(link => {
        const href = link.href;
        link.href = href.split('?')[0] + '?v=' + Date.now();
    });
}

// Add some helpful placeholder text rotation
const placeholders = [
    'Enter your research topic (e.g., "Artificial Intelligence in Healthcare")',
    'What would you like to research? (e.g., "Climate Change Solutions")',
    'Research topic (e.g., "Quantum Computing Applications")',
    'Enter topic (e.g., "Sustainable Energy Technologies")'
];

let placeholderIndex = 0;
setInterval(() => {
    if (document.activeElement !== researchTopicInput) {
        researchTopicInput.placeholder = placeholders[placeholderIndex];
        placeholderIndex = (placeholderIndex + 1) % placeholders.length;
    }
}, 3000);

// Debug: Log when CSS is loaded
console.log('CSS loaded with academic formatting v11 - Numbered headings, no # symbols');
