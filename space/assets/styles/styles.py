import base64
from typing import Optional


def get_logo_html(logo_path: Optional[str] = None):
    """Load and encode logo image, with fallback"""
    path = logo_path or "assets/images/bambara-logo.png"
    try:
        with open(path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
            return f'<img src="data:image/png;base64,{img_data}" alt="MALIBA-AI Logo" style="height: 100px; width: auto;">'
    except (FileNotFoundError, Exception) as e:
        # Fallback to emoji icon
        return '<div style="width: 100px; height: 100px; background: linear-gradient(135deg, #7d3561 0%, #2f3b7d 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center; color: white; font-size: 48px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">🎤</div>'


# Professional header with centered logo and title
professional_header_html = f"""
<div style="text-align: center; padding: 40px 20px 30px 20px; background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); border-bottom: 3px solid #7d3561;">
    <div style="display: inline-block; margin-bottom: 20px;">
        {get_logo_html()}
    </div>
    <h1 style="font-family: 'Segoe UI', 'Arial', sans-serif; font-size: 42px; font-weight: 700; color: #2f3b7d; margin: 20px 0 10px 0; letter-spacing: -0.5px;">
        Bambara ASR Leaderboard
    </h1>
    <p style="font-size: 18px; color: #7d3561; font-weight: 500; margin: 0;">
        Evaluating Automatic Speech Recognition for Bambara Language
    </p>
    <p style="font-size: 14px; color: #666; margin-top: 15px; font-style: italic;">
        A collaboration between <strong>MALIBA-AI</strong>, <strong>RobotsMali AI4D-LAB</strong>, and <strong>Djelia</strong>
    </p>
</div>
"""


# Professional CSS styling inspired by modern academic leaderboards
professional_css = """
/* ============================================
   GLOBAL STYLES & LAYOUT
   ============================================ */
   
.fillable.svelte-15jxnnn.svelte-15jxnnn:not(.fill_width) {
    max-width: 1400px !important;
    margin: 0 auto;
}

div[class*="gradio-container"] {
    background: #f8f9fa !important;
    color: #212529 !important;
    font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

div.svelte-1nguped {
    background: white !important;
}

/* ============================================
   HEADER NAVIGATION BUTTONS
   ============================================ */
   
.flat-navy-button {
    background: linear-gradient(135deg, #2f3b7d 0%, #1a2456 100%) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    border-radius: 8px !important;
    border: none !important;
    box-shadow: 0 2px 4px rgba(47, 59, 125, 0.2) !important;
    padding: 10px 20px !important;
    transition: all 0.3s ease !important;
}

.flat-navy-button:hover {
    background: linear-gradient(135deg, #7d3561 0%, #5c2847 100%) !important;
    box-shadow: 0 4px 8px rgba(125, 53, 97, 0.3) !important;
    transform: translateY(-2px) !important;
}

/* ============================================
   CONTENT CARDS
   ============================================ */

.content-card {
    background-color: #ffffff !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    padding: 32px !important;
    margin-bottom: 32px !important;
    border: 1px solid #e9ecef !important;
}

.content-card h2 {
    font-family: 'Segoe UI', sans-serif;
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #2f3b7d !important;
    margin-bottom: 20px !important;
    border-bottom: 3px solid #7d3561;
    padding-bottom: 12px;
}

.content-card h3 {
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #2f3b7d !important;
    margin-top: 24px !important;
}

.content-card h3 .title {
    color: #7d3561 !important;
    font-weight: 700 !important;
}

/* ============================================
   BEST MODEL HIGHLIGHT SECTION
   ============================================ */
   
.best-model-card {
    background: linear-gradient(135deg, #fff8e7 0%, #fffbf5 100%) !important;
    border-left: 5px solid #ffc107 !important;
    padding: 24px !important;
    border-radius: 12px !important;
    margin-bottom: 30px !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07) !important;
}

/* FIXED: Best model text visibility */
.best-model-card h3 {
    color: #2f3b7d !important;
}

.best-model-card ul {
    list-style: none !important;
    padding-left: 0 !important;
}

.best-model-card li {
    color: #212529 !important;
    font-size: 16px !important;
    margin-bottom: 8px !important;
}

.best-model-card strong {
    color: #7d3561 !important;
    font-weight: 700 !important;
}

/* ============================================
   TABS STYLING
   ============================================ */

.tab-wrapper.svelte-1tcem6n.svelte-1tcem6n {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    border-bottom: 2px solid #e9ecef !important;
    margin-bottom: 30px !important;
}

.tabs.svelte-1tcem6n.svelte-1tcem6n {
    border-top: 0 !important;
    background: transparent !important;
}

button.svelte-1tcem6n.svelte-1tcem6n {
    color: #6c757d !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 12px 24px !important;
    background-color: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    transition: all 0.3s ease !important;
}

button.svelte-1tcem6n.svelte-1tcem6n:hover {
    color: #7d3561 !important;
    background-color: #f8f9fa !important;
    border-radius: 8px 8px 0 0 !important;
}

.selected.svelte-1tcem6n.svelte-1tcem6n {
    color: #2f3b7d !important;
    background-color: transparent !important;
    border-bottom: 3px solid #7d3561 !important;
    font-weight: 700 !important;
}

/* ============================================
   TABLE STYLING
   ============================================ */

div[class*="gradio-container"] .prose table {
    width: 100% !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    margin: 24px 0 !important;
    background: white !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
}

div[class*="gradio-container"] .prose thead {
    background: linear-gradient(135deg, #2f3b7d 0%, #1a2456 100%) !important;
}

div[class*="gradio-container"] .prose th {
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    padding: 16px 12px !important;
    border: none !important;
    text-align: center !important;
}

div[class*="gradio-container"] .prose th:first-child {
    text-align: left !important;
    padding-left: 24px !important;
}

div[class*="gradio-container"] .prose tbody tr {
    border-bottom: 1px solid #e9ecef !important;
    transition: background-color 0.2s ease !important;
}

div[class*="gradio-container"] .prose tbody tr:hover {
    background-color: #f8f9fa !important;
}

div[class*="gradio-container"] .prose tbody tr:last-child {
    border-bottom: none !important;
}

div[class*="gradio-container"] .prose td {
    padding: 14px 12px !important;
    color: #212529 !important;
    font-size: 14px !important;
    border: none !important;
    text-align: center !important;
}

div[class*="gradio-container"] .prose td:first-child {
    font-weight: 600 !important;
    color: #2f3b7d !important;
    text-align: left !important;
    padding-left: 24px !important;
}

/* Medal styling */
div[class*="gradio-container"] .prose td:first-child:has(.emoji) {
    font-size: 16px !important;
}

/* ============================================
   SPECIFIC TABLE COLUMN WIDTHS
   ============================================ */

/* Main leaderboard */
div[class*="gradio-container"] .prose th:first-child,
div[class*="gradio-container"] .prose td:first-child {
    min-width: 350px !important;
}

/* Model-specific table */
#model_specific_table .prose td:nth-child(2) {
    text-align: left !important;
    font-weight: 500 !important;
}

/* Comparison table */
#models_comparison_table .prose th:nth-child(2),
#models_comparison_table .prose td:nth-child(2) {
    width: 200px !important;
    text-align: left !important;
    font-weight: 600 !important;
}

#models_comparison_table .prose th:first-child,
#models_comparison_table .prose td:first-child {
    width: 150px !important;
    text-align: left !important;
}

/* ============================================
   FORM CONTROLS
   ============================================ */

input[type="text"], textarea, .input-field {
    border: 2px solid #dee2e6 !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    font-size: 14px !important;
    transition: border-color 0.3s ease !important;
}

input[type="text"]:focus, textarea:focus, .input-field:focus {
    border-color: #7d3561 !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(125, 53, 97, 0.1) !important;
}

button[variant="primary"] {
    background: linear-gradient(135deg, #7d3561 0%, #5c2847 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 12px 32px !important;
    border-radius: 8px !important;
    border: none !important;
    font-size: 15px !important;
    box-shadow: 0 4px 6px rgba(125, 53, 97, 0.2) !important;
    transition: all 0.3s ease !important;
}

button[variant="primary"]:hover {
    background: linear-gradient(135deg, #5c2847 0%, #441d35 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 12px rgba(125, 53, 97, 0.3) !important;
}

/* ============================================
   CITATION BLOCK
   ============================================ */

.citation-section {
    background: #ffffff !important;
    border-radius: 12px !important;
    padding: 24px !important;
    border-left: 4px solid #7d3561 !important;
}

.citation-section h2 {
    color: #2f3b7d !important;
}

.citation-section h3 {
    color: #7d3561 !important;
}

.citation-section p {
    color: #212529 !important;
}

.citation-section ul {
    color: #212529 !important;
}

.citation-section li {
    color: #212529 !important;
}

.citation-section strong {
    color: #2f3b7d !important;
}

.citation-section pre {
    background: #f8f9fa !important;
    border: 1px solid #dee2e6 !important;
    border-radius: 8px !important;
    padding: 16px !important;
    overflow-x: auto !important;
    font-size: 13px !important;
    line-height: 1.6 !important;
}

.citation-section code {
    color: #212529 !important;
    font-family: 'Courier New', monospace !important;
}

/* ============================================
   MARKDOWN CONTENT - FIXED TEXT VISIBILITY
   ============================================ */

div[class*="gradio-container"] .prose h1 {
    color: #2f3b7d !important;
    font-weight: 700 !important;
}

div[class*="gradio-container"] .prose h2 {
    color: #000000 !important;
    font-weight: 700 !important;
    margin-top: 32px !important;
    margin-bottom: 16px !important;
}

div[class*="gradio-container"] .prose h3 {
    color: #2f3b7d !important;
    font-weight: 600 !important;
    margin-top: 24px !important;
    margin-bottom: 12px !important;
}

div[class*="gradio-container"] .prose p {
    color: #212529 !important;
    line-height: 1.7 !important;
    margin-bottom: 16px !important;
}

div[class*="gradio-container"] .prose ul, 
div[class*="gradio-container"] .prose ol {
    color: #212529 !important;
    line-height: 1.7 !important;
    padding-left: 24px !important;
}

div[class*="gradio-container"] .prose li {
    color: #212529 !important;
    margin-bottom: 8px !important;
}

div[class*="gradio-container"] .prose strong {
    color: #2f3b7d !important;
    font-weight: 600 !important;
}

div[class*="gradio-container"] .prose code {
    background: #f8f9fa !important;
    border: 1px solid #dee2e6 !important;
    color: #7d3561 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.9em !important;
}

div[class*="gradio-container"] .prose pre {
    background: #f8f9fa !important;
    border: 1px solid #dee2e6 !important;
    border-radius: 8px !important;
    padding: 16px !important;
    overflow-x: auto !important;
}

div[class*="gradio-container"] .prose pre code {
    background: transparent !important;
    border: none !important;
    color: #212529 !important;
    padding: 0 !important;
}

/* ============================================
   DROPDOWN STYLING
   ============================================ */

.dropdown {
    border: 2px solid #dee2e6 !important;
    border-radius: 8px !important;
    background: white !important;
}

/* ============================================
   RESPONSIVE DESIGN
   ============================================ */

@media (max-width: 768px) {
    .fillable.svelte-15jxnnn.svelte-15jxnnn:not(.fill_width) {
        max-width: 100% !important;
        padding: 0 16px !important;
    }
    
    .content-card {
        padding: 20px !important;
    }
    
    div[class*="gradio-container"] .prose th,
    div[class*="gradio-container"] .prose td {
        padding: 10px 8px !important;
        font-size: 12px !important;
    }
}

/* ============================================
   UTILITY CLASSES
   ============================================ */

.text-center {
    text-align: center !important;
}

.mb-4 {
    margin-bottom: 24px !important;
}

.mt-4 {
    margin-top: 24px !important;
}
"""