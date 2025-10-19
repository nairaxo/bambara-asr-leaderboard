import base64
from typing import Optional


def get_logo_html(logo_path: Optional[str] = None):

    path = logo_path or  "assets/images/bambara-logo.png" # if logo_path is None, use default path
    try:
        with open(path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
            return f'<img src="data:image/png;base64,{img_data}" alt="MALIBA-AI Logo" style="height: 80px; width: auto; margin-right: 25px;">'
    except FileNotFoundError:
   
        return '<div style="width: 80px; height: 80px; background: #7d3561; border-radius: 10px; margin-right: 25px; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px;">🎤</div>'
    except Exception as e:
        print(f"Error loading logo: {e}")
        return '<div style="width: 80px; height: 80px; background: #7d3561; border-radius: 10px; margin-right: 25px; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px;">🎤</div>'



new_header_html = f"""
<center>
          <br><br><br>
          {get_logo_html()}
        </p>
</center>
<br style="height:1px;">
"""

google_style_css = """
/* Citation Block */
.citation-block {
    position: relative;
    background-color: #FDF6E3 !important;
    border-radius: 8px;
    padding: 25px;
}
.citation-block pre {
    background-color: transparent;
    border: none;
    padding: 0;
    white-space: pre-wrap;
    word-break: break-all;
}
.citation-block .btn-copy {
    position: absolute;
    top: 15px;
    right: 15px;
    background-color: #D97706 !important;
    border-color: #c56a05 !important;
    color: white !important;
}
.citation-block .btn-copy:hover, .citation-block .btn-copy:focus {
    background-color: #c56a05 !important;
    color: white !important;
}

.fillable.svelte-15jxnnn.svelte-15jxnnn:not(.fill_width) {
    max-width: 1580px !important;
}
  
.flat-navy-button {
    background-color: #117b75 !important;
    color: #fff !important;
    font-weight: bold !important;
    border-radius: 5px !important;
    border: none !important;
    box-shadow: none !important;
}
.flat-navy-button:hover {
    background-color: #117b75 !important;
    color: #e8850e !important;
}

div[class*="gradio-container"] {
    background:#FFFBF5 !important;
    color:#000 !important;
}

div.svelte-1nguped {
    background: white !important;
}

.content-section {
    padding: 60px 0;
}
.content-card {
    background-color: #fff !important;
    border-radius: 12px;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
    padding: 40px;
    margin-bottom: 40px;
}

.btn-cite {
    color: #7d3561;
    font-size: 16px;
    margin: 0 3px;
}

.content-card h4 {
    font-family: "Rubik", sans-serif;
    color: #7d3561 !important;
}
.content-card h2 {
    font-family: "Rubik", sans-serif;
    font-size: 30px;
    font-weight: 600;
    line-height: 1.25;
    letter-spacing: -1px;
    color: #2f3b7d !important;
    text-transform:none;
}
.content-card h3 {
    font-size: 20px;
    color: #2f3b7d !important;
}
.content-card h3 .title {
    color: #7d3561 !important;
}

div.svelte-wv8on1{
    border-top: 0 !important;
    padding: 10px !important;
}
.padding.svelte-phx28p {
    padding:0 !important;
}

.tab-wrapper.svelte-1tcem6n.svelte-1tcem6n {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    height: 0 !important;
    padding-bottom: 0 !important;
}

.selected.svelte-1tcem6n.svelte-1tcem6n {
    background-color: #7d3561 !important;
    color: #fff !important;
}
.tabs.svelte-1tcem6n.svelte-1tcem6n {
    border-top: 0 !important;
}
button.svelte-1tcem6n.svelte-1tcem6n {
    color: #7d3561 !important;
    font-weight: bold;
    padding: 8px 5px;
    background-color: #fff !important;
}
button.svelte-1tcem6n.svelte-1tcem6n:hover {
    background-color: #de8fc2 !important;
}
.tab-container.svelte-1tcem6n.svelte-1tcem6n:after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background-color: #7d3561 !important;
}

div[class*="gradio-container"] .prose table,
div[class*="gradio-container"] .prose tr,
div[class*="gradio-container"] .prose td,
div[class*="gradio-container"] .prose th {
    border: 0 !important;
    border-top: 2px solid #dca02a;
    border-bottom: 2px solid #dca02a;
}

div[class*="gradio-container"] .prose table {
    color:#000 !important;
    border-top: 2px solid #dca02a !important;
    border-bottom: 2px solid #dca02a !important;
    margin-bottom:20px;
    margin-left: auto;
    margin-right: auto;
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}
div[class*="gradio-container"] .prose thead tr {
    border-bottom: 2px solid #dca02a !important;
}
div[class*="gradio-container"] .prose th {
    color: #7d3561 !important;
    font-weight: bold;
    padding: 8px 5px;
    vertical-align: middle;
    border: 0 !important;
}
div[class*="gradio-container"] .prose td {
    padding: 8px 5px;
    border: 0 !important;
    vertical-align: middle;
    color:#000 !important;
}
div[class*="gradio-container"] .prose th:first-child,
div[class*="gradio-container"] .prose td:first-child {
    min-width: 400px !important;
    width:400px !important;
    text-align: left !important;
}
div[class*="gradio-container"] .prose th:not(:first-child),
div[class*="gradio-container"] .prose td:not(:first-child) {
    text-align: center;
}

#model_specific_table .prose td:nth-child(2) {
    text-align: left;
}

#models_comparison_table .prose th:nth-child(2),
#models_comparison_table .prose td:nth-child(2) {
    width: 200px !important;
    text-align: left !important;
    white-space: nowrap;
}

#models_comparison_table .prose th:first-child,
#models_comparison_table .prose td:first-child {
    width: 130px !important;
    text-align: left !important;
}

#models_comparison_table .prose th:not(:nth-child(1)):not(:nth-child(2)),
#models_comparison_table .prose td:not(:nth-child(1)):not(:nth-child(2)) {
    width: 95px !important;
    text-align: center;
}

div[class*="gradio-container"] .md :not(pre)>code {
    background: #fcbb99 !important;
    border: 1px solid #763412 !important;
}
div[class*="gradio-container"] .md * {
    color: #000 !important;
}
"""
