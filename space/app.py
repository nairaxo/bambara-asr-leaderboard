import gradio as gr
import pandas as pd
from datasets import load_dataset
from jiwer import wer, cer
import os
from datetime import datetime
import re
import numpy as np

from settings.models import Settings
from assets.styles.styles import (
    get_logo_html, 
    new_header_html, 
    google_style_css
)

config = Settings()

try :
    dataset = load_dataset(config.dataset_url, name=config.dataset_config, token=config.hf_token)["eval"]
    references = {row["id"]: row["text"] for row in dataset}
except Exception as e : 
    raise ValueError(f"Failed to load the dataset: {e}")


leaderboard_file = config.leaderboard_file
logo_path = config.logo_path

if not os.path.exists(leaderboard_file):
    # this is a just for testing purpose, in real scenario the file should be created when the first submission is made (I will come back to this later)
    sample_data = [
                    ["MALIBA-AI/bambara-whisper-base", 0.2264, 0.1094, 0.1679, "2025-03-15 10:30:45"],
                    ["OpenAI/whisper-large-v3", 0.3264, 0.1594, 0.2429, "2025-03-15 10:30:45"],
                    ["Meta/seamless-m4t-v2", 0.4156, 0.2134, 0.3149, "2025-03-15 10:30:45"],
    ]

    pd.DataFrame(sample_data, 
                 columns=[
                          "Model_Name", 
                          "WER", 
                          "CER", 
                          "Combined_Score", 
                          "timestamp"
                          ]).to_csv(leaderboard_file, index=False)


def normalize_text(text):
    if not isinstance(text, str):
        text = str(text)
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def calculate_metrics(predictions_df):
    results = []
    total_ref_words = 0
    total_ref_chars = 0

    for _, row in predictions_df.iterrows():
        id_val = row["id"]
        if id_val not in references:
            continue
            
        reference = normalize_text(references[id_val])
        hypothesis = normalize_text(row["text"])
        
        if not reference or not hypothesis:
            continue
            
        reference_words = reference.split()
        reference_chars = list(reference)
        
        try:
            sample_wer = wer(reference, hypothesis)
            sample_cer = cer(reference, hypothesis)
            
            sample_wer = min(sample_wer, 2.0)  
            sample_cer = min(sample_cer, 2.0)  
            
            total_ref_words += len(reference_words)
            total_ref_chars += len(reference_chars)
            
            results.append({
                "id": id_val,
                "reference": reference,
                "hypothesis": hypothesis,
                "ref_word_count": len(reference_words),
                "ref_char_count": len(reference_chars),
                "wer": sample_wer,
                "cer": sample_cer
            })
        except Exception as e:
            print(f"Error processing sample {id_val}: {str(e)}")
            pass
    

    if not results:
        raise ValueError("No valid samples for WER/CER calculation")
        
    avg_wer = sum(item["wer"] for item in results) / len(results)
    avg_cer = sum(item["cer"] for item in results) / len(results)
    
    return avg_wer, avg_cer, results

def format_as_percentage(value):
    return f"{value * 100:.2f}%"

def add_medals_to_models(df, score_col="Combined_Score"):
    score_float_col = "__score_float"
    df[score_float_col] = df[score_col].apply(lambda x: float(x.replace('%', '')) if isinstance(x, str) and '%' in x else float(x) if x != "---" else np.nan)
    df = df.sort_values(by=score_float_col, ascending=True, kind="mergesort").reset_index(drop=True)  
    
    def get_rank_symbols(scores):
        unique_scores = sorted(set([s for s in scores if not pd.isna(s)]))  
        symbols = ["🏆", "🥈", "🥉"]
        score_to_symbol = {s: symbols[i] for i, s in enumerate(unique_scores[:3])}
        return [score_to_symbol.get(s, "") for s in scores]
    
    df['rank_symbol'] = get_rank_symbols(df[score_float_col].tolist())
    df['Model_Name'] = df['rank_symbol'] + ' ' + df['Model_Name']
    df = df.drop(columns=['rank_symbol', score_float_col])
    return df

def get_current_leaderboard():
    try:
        if os.path.exists(leaderboard_file):
            current_leaderboard = pd.read_csv(leaderboard_file)
            if "Combined_Score" not in current_leaderboard.columns:
                current_leaderboard["Combined_Score"] = current_leaderboard["WER"] * 0.7 + current_leaderboard["CER"] * 0.3
                current_leaderboard.to_csv(leaderboard_file, index=False)
            return current_leaderboard
        else:
            return pd.DataFrame(columns=["Model_Name", "WER", "CER", "Combined_Score", "timestamp"])
    except Exception as e:
        print(f"Error getting leaderboard: {str(e)}")
        return pd.DataFrame(columns=["Model_Name", "WER", "CER", "Combined_Score", "timestamp"])


def prepare_leaderboard_for_display(df, sort_by="Combined_Score"):
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=["Rank", "Model Name", "WER (%)", "CER (%)", "Combined Score (%)", "Timestamp"])
    
    display_df = df.copy()
    display_df = display_df.sort_values(sort_by, ascending=True)  
    display_df.insert(0, "Rank", range(1, len(display_df) + 1))
    
    for col in ["WER", "CER", "Combined_Score"]:
        if col in display_df.columns:
            display_df[f"{col} (%)"] = display_df[col].apply(lambda x: f"{x * 100:.2f}")
    
    display_df = display_df.rename(columns={
        "Model_Name": "Model Name",
        "timestamp": "Timestamp",
        "Combined_Score (%)": "Combined Score (%)"
    })
    
    display_cols = ["Rank", "Model Name", "WER (%)", "CER (%)", "Combined Score (%)", "Timestamp"]
    display_df = display_df[[col for col in display_cols if col in display_df.columns]]
    
    return display_df

def df_to_html(df):
    if df.empty:
        return "<p>No data available</p>"
    df.columns.name = None
    html = df.to_html(index=False, escape=False)
    return html

def get_model_performance_table(model_name):
    current_lb = get_current_leaderboard()
    model_data = current_lb[current_lb['Model_Name'] == model_name]
    
    if model_data.empty:
        return pd.DataFrame([{"Info": f"No data available for model: {model_name}"}])
    
    model_row = model_data.iloc[0]
    

    metrics_data = [
        ["Bambara ASR", "Word Error Rate (WER)", f"{model_row['WER'] * 100:.2f}%"],
        ["Bambara ASR", "Character Error Rate (CER)", f"{model_row['CER'] * 100:.2f}%"],
        ["Bambara ASR", "Combined Score", f"{model_row['Combined_Score'] * 100:.2f}%"],
    ]
    
    table = pd.DataFrame(metrics_data, columns=["Task", "Metric", "Score"])
    return table

def compare_models(model_1_name, model_2_name):
    if model_1_name == model_2_name:
        return pd.DataFrame([{"Info": "Please select two different models to compare."}])
    
    current_lb = get_current_leaderboard()
    model1_data = current_lb[current_lb['Model_Name'] == model_1_name]
    model2_data = current_lb[current_lb['Model_Name'] == model_2_name]
    
    if model1_data.empty or model2_data.empty:
        return pd.DataFrame([{"Info": "One or both selected models have no data to compare."}])
    
    m1 = model1_data.iloc[0]
    m2 = model2_data.iloc[0]
    
    def format_diff(val1, val2):
        diff = val1 - val2
        if abs(diff) < 0.001:
            return f"{diff:.3f}"
        elif diff > 0:  
            return f"<span style='color:red; font-weight:bold;'>+{diff:.3f}</span>"
        else:  
            return f"<span style='color:green; font-weight:bold;'>{diff:.3f}</span>"
    
    comparison_data = [
        ["ASR Performance", "Word Error Rate (WER)", f"{m1['WER']:.3f}", f"{m2['WER']:.3f}", format_diff(m1['WER'], m2['WER'])],
        ["ASR Performance", "Character Error Rate (CER)", f"{m1['CER']:.3f}", f"{m2['CER']:.3f}", format_diff(m1['CER'], m2['CER'])],
        ["ASR Performance", "Combined Score", f"{m1['Combined_Score']:.3f}", f"{m2['Combined_Score']:.3f}", format_diff(m1['Combined_Score'], m2['Combined_Score'])],
    ]
    
    comp_df = pd.DataFrame(comparison_data, columns=["Category", "Metric", model_1_name, model_2_name, "Difference"])
    return comp_df

def process_submission(model_name, csv_file):
    if not model_name or not model_name.strip():
        return "Error: Please provide a model name.", None
        
    if not csv_file:
        return "Error: Please upload a CSV file.", None
    
    try:
        df = pd.read_csv(csv_file)
        
        if len(df) == 0:
            return "Error: Uploaded CSV is empty.", None
            
        if set(df.columns) != {"id", "text"}:
            return f"Error: CSV must contain exactly 'id' and 'text' columns. Found: {', '.join(df.columns)}", None
            
        if df["id"].duplicated().any():
            dup_ids = df[df["id"].duplicated()]["id"].unique()
            return f"Error: Duplicate IDs found: {', '.join(map(str, dup_ids[:5]))}", None

        missing_ids = set(references.keys()) - set(df["id"])
        extra_ids = set(df["id"]) - set(references.keys())
        
        if missing_ids:
            return f"Error: Missing {len(missing_ids)} IDs in submission. First few missing: {', '.join(map(str, list(missing_ids)[:5]))}", None
            
        if extra_ids:
            return f"Error: Found {len(extra_ids)} extra IDs not in reference dataset. First few extra: {', '.join(map(str, list(extra_ids)[:5]))}", None
        
        try:
            avg_wer, avg_cer, detailed_results = calculate_metrics(df)
            
            if avg_wer < 0.001:
                return "Error: WER calculation yielded suspicious results (near-zero). Please check your submission CSV.", None
                
        except Exception as e:
            return f"Error calculating metrics: {str(e)}", None
        
        leaderboard = pd.read_csv(leaderboard_file)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        combined_score = avg_wer * 0.7 + avg_cer * 0.3
        
        if model_name in leaderboard["Model_Name"].values:
            idx = leaderboard[leaderboard["Model_Name"] == model_name].index
            leaderboard.loc[idx, "WER"] = avg_wer
            leaderboard.loc[idx, "CER"] = avg_cer
            leaderboard.loc[idx, "Combined_Score"] = combined_score
            leaderboard.loc[idx, "timestamp"] = timestamp
            updated_leaderboard = leaderboard
        else:
            new_entry = pd.DataFrame(
                [[model_name, avg_wer, avg_cer, combined_score, timestamp]],
                columns=["Model_Name", "WER", "CER", "Combined_Score", "timestamp"]
            )
            updated_leaderboard = pd.concat([leaderboard, new_entry])
        
        updated_leaderboard = updated_leaderboard.sort_values("Combined_Score")
        updated_leaderboard.to_csv(leaderboard_file, index=False)
        
        display_leaderboard = prepare_leaderboard_for_display(updated_leaderboard)
        
        return f"Submission processed successfully! WER: {format_as_percentage(avg_wer)}, CER: {format_as_percentage(avg_cer)}, Combined Score: {format_as_percentage(combined_score)}", df_to_html(display_leaderboard)
        
    except Exception as e:
        return f"Error processing submission: {str(e)}", None


def create_main_leaderboard():
    current_data = get_current_leaderboard()
    if len(current_data) == 0:
        return pd.DataFrame(columns=["Model Name", "WER (%)", "CER (%)", "Combined Score (%)", "Timestamp"])
    
    display_df = current_data.copy()
    
    for col in ["WER", "CER", "Combined_Score"]:
        if col in display_df.columns:
            display_df[f"{col} (%)"] = display_df[col].apply(lambda x: f"{x * 100:.2f}")
    
    display_df = add_medals_to_models(display_df, score_col="Combined_Score")
    
    display_df = display_df.rename(columns={
        "Model_Name": "Model Name",
        "timestamp": "Timestamp",
        "Combined_Score (%)": "Combined Score (%)"
    })
    
    final_cols = ["Model Name", "WER (%)", "CER (%)", "Combined Score (%)", "Timestamp"]
    display_df = display_df[[col for col in final_cols if col in display_df.columns]]
    
    return display_df


current_data = get_current_leaderboard()
MODEL_NAME_LIST = sorted(current_data['Model_Name'].unique()) if len(current_data) > 0 else []

favicon_head = '<link rel="icon" type="image/x-icon" href="/file=favicon.ico">'

with gr.Blocks(theme=gr.themes.Default(), title="Bambara ASR Benchmark Leaderboard", css=google_style_css, head=favicon_head) as demo:
    gr.HTML(new_header_html)
    
    with gr.Row():
        gr.Button("MALIBA-AI", link="https://huggingface.co/MALIBA-AI", elem_classes=['flat-navy-button'])
        gr.Button("Dataset Repository", link="https://huggingface.co/datasets/sudoping01/bambara-speech-recognition-benchmark", elem_classes=['flat-navy-button'])
        gr.Button("GitHub Repo", link="https://github.com/sudoping01/bambara-asr-benchmark", elem_classes=['flat-navy-button'])
        gr.Button("Paper", link="#", elem_classes=['flat-navy-button'])
        gr.Button("Tasks", link="#", elem_classes=['flat-navy-button'])
    
    with gr.Group(elem_classes="content-card"):
        gr.Markdown("<br>")
        
       
        if len(current_data) > 0:
            best_model = current_data.sort_values("Combined_Score").iloc[0]
            gr.Markdown(f"""
            ### 🏆 Current Best Model: **{best_model['Model_Name']}**
            * WER: **{best_model['WER']*100:.2f}%**
            * CER: **{best_model['CER']*100:.2f}%**
            * Combined Score: **{best_model['Combined_Score']*100:.2f}%**
            """)
        
        with gr.Tabs() as tabs:
            with gr.Tab("Main Leaderboard", id="main"):
                gr.HTML("<br><br><center><h2>Main Leaderboard</h2></center><br>")
                main_leaderboard = create_main_leaderboard()
                gr.HTML(df_to_html(main_leaderboard))
            
            with gr.Tab("Model-Specific Performance", id="models", elem_id="model_specific_table"):
                gr.HTML("<br><br><center><h2>Model-Specific Performance</h2></center><br>")
                
                if MODEL_NAME_LIST:
                    initial_model = MODEL_NAME_LIST[0]
                    initial_title_html = f"<h3><span class='title'>Model name:</span> {initial_model}</h3>"
                    model_title_component = gr.HTML(initial_title_html)
                    
                    model_dropdown = gr.Dropdown(
                        choices=MODEL_NAME_LIST, 
                        label="Select Model", 
                        interactive=True,
                        value=initial_model
                    )
                    
                    model_table_component = gr.HTML(df_to_html(get_model_performance_table(initial_model)))
                    
                    def update_model_display(model_name):
                        table = get_model_performance_table(model_name)
                        title = f"<h3><span class='title'>Model name:</span> {model_name}</h3>"
                        return title, df_to_html(table)
                    
                    model_dropdown.change(
                        fn=update_model_display, 
                        inputs=model_dropdown, 
                        outputs=[model_title_component, model_table_component]
                    )
                else:
                    gr.HTML("<p>No models available for comparison.</p>")
            
            with gr.Tab("Compare Models", id="compare"):
                gr.HTML("<br><br><center><h2>Compare Two Models</h2></center><br>")
                
                if len(MODEL_NAME_LIST) >= 2:
                    with gr.Row():
                        model_1_dd = gr.Dropdown(MODEL_NAME_LIST, label="Select Model 1", interactive=True)
                        model_2_dd = gr.Dropdown(MODEL_NAME_LIST, label="Select Model 2", interactive=True)
                    compare_btn = gr.Button("Compare")
                    
                    explanation_note = """
                    **Note on the 'Difference' Column:**
                    * This value is calculated as: `(Score of Model 1) - (Score of Model 2)`.
                    * For ASR tasks (where lower is better): A negative value in <span style='color:green; font-weight:bold;'>green</span> indicates that **Model 1** performed better.
                    * A positive value in <span style='color:red; font-weight:bold;'>red</span> indicates that **Model 2** performed better.
                    """
                    explanation_note_md = gr.Markdown(explanation_note, visible=False)
                    
                    with gr.Column(elem_id="models_comparison_table"):
                        comparison_output = gr.HTML("<p style='text-align:center;'>Select two models and click Compare to see the results.</p>")
                    
                    def update_comparison_display(m1, m2):
                        if not m1 or not m2:
                            return gr.update(visible=False), "<p style='text-align:center;'>Please select two models to compare.</p>"
                        
                        comp_df = compare_models(m1, m2)
                        return gr.update(visible=True), df_to_html(comp_df)
                    
                    compare_btn.click(
                        fn=update_comparison_display,
                        inputs=[model_1_dd, model_2_dd],
                        outputs=[explanation_note_md, comparison_output]
                    )
                else:
                    gr.HTML("<p>At least 2 models are required for comparison.</p>")
            
            with gr.Tab("📊 Submit New Results", id="submit"):
                gr.HTML("<br><br><center><h2>Submit New Model Results</h2></center><br>")
                gr.Markdown(
                    """
                    ### Submit a new model for evaluation
                    
                    Upload a CSV file with your model's predictions on the Bambara ASR benchmark dataset.
                    
                    **Required CSV format:**
                    * Must contain exactly two columns: `id` and `text`
                    * The `id` column should match the reference dataset IDs
                    * The `text` column should contain your model's transcriptions
                    * Ensure all reference IDs are included in your submission
                    """
                )
                
                with gr.Row():
                    model_name_input = gr.Textbox(
                        label="Model Name", 
                        placeholder="e.g., MALIBA-AI/bambara-whisper-large"
                    )
                    gr.Markdown("*Use a descriptive name to identify your model*")
                
                with gr.Row():
                    csv_upload = gr.File(
                        label="Upload CSV File", 
                        file_types=[".csv"]
                    )
                    gr.Markdown("*CSV with columns: id, text*")
                    
                submit_btn = gr.Button("Submit", variant="primary")
                output_msg = gr.Textbox(label="Status", interactive=False)
                
                submission_leaderboard_display = gr.HTML(
                    df_to_html(create_main_leaderboard()),
                    label="Updated Leaderboard"
                )
                
                submit_btn.click(
                    fn=process_submission,
                    inputs=[model_name_input, csv_upload],
                    outputs=[output_msg, submission_leaderboard_display]
                )
            
            with gr.Tab("📝 Benchmark Dataset", id="dataset"):
                gr.HTML("<br><br><center><h2>About the Benchmark Dataset</h2></center><br>")
                gr.Markdown(
                    """
                    ## Bambara ASR Benchmark Dataset
                    
                    This leaderboard uses the **[sudoping01/bambara-speech-recognition-benchmark](https://huggingface.co/datasets/sudoping01/bambara-speech-recognition-benchmark)** dataset for evaluation.
                    
                    ### Dataset Characteristics
                    
                    * **Language**: Bambara (native to Mali and surrounding regions)
                    * **Task**: Automatic Speech Recognition (ASR)
                    * **Domain**: Diverse speech samples covering various topics and speaking styles
                    * **Speakers**: Multiple native Bambara speakers with different accents and dialects
                    * **Audio Quality**: Various recording conditions to test model robustness
                    
                    ### Evaluation Metrics
                    
                    **Word Error Rate (WER)**
                    * Primary metric for ASR evaluation
                    * Measures accuracy at the word level
                    * Calculated as: (Substitutions + Insertions + Deletions) / Total Words
                    * Lower values indicate better performance
                    
                    **Character Error Rate (CER)**
                    * Complementary metric for character-level accuracy
                    * More fine-grained than WER
                    * Better captures partial word matches
                    * Particularly useful for morphologically rich languages like Bambara
                    
                    **Combined Score**
                    * Weighted combination: 70% WER + 30% CER
                    * Provides balanced evaluation considering both word and character accuracy
                    * Used as the primary ranking metric
                    
                    ### How to Submit Results
                    
                    1. **Download the dataset** from the Hugging Face repository
                    2. **Process the audio files** with your ASR model
                    3. **Generate predictions** in the required CSV format:
                    <pre style="background-color:#eef6ff; color:black; padding:10px; border-radius:8px;">
                   
                       ```csv
                       id,text
                       sample_001,"your model's transcription here"
                       sample_002,"another transcription"
                       ...
                       ```
                    
                    </pre>
                    4. **Submit your results** using the "Submit New Results" tab
                    
                    ### Evaluation Guidelines
                    
                    * All text is normalized (lowercase, punctuation removed) before evaluation
                    * Submissions must include predictions for all reference samples
                    * Duplicate IDs or missing samples will result in submission rejection
                    * Results are automatically validated for format and completeness
                    
                    ### Technical Details
                    
                    * **Text Normalization**: Removes punctuation, converts to lowercase, normalizes whitespace
                    * **Error Calculation**: Uses the `jiwer` library for standard WER/CER computation
                    * **Quality Assurance**: Extreme outliers are capped to prevent result manipulation
                    * **Reproducibility**: All evaluation code is open-source and transparent
                    """
                )
    

    with gr.Group(elem_classes="content-card"):
        gr.Markdown("<br>")
        gr.HTML("<h2>Citation</h2>")
        gr.Markdown(
            """
            If you use the Bambara ASR benchmark for your scientific publication, or if you find the resources in this leaderboard useful, please cite our work:
            <pre style="background-color:#eef6ff; color:black; padding:10px; border-radius:8px;">
            <code>
            @article{bambara_asr_benchmark_2025,
                title={Bambara ASR Benchmark: Evaluating Speech Recognition for a Low-Resource African Language},
                author={MALIBA-AI Team and RobotsMali AI4D-LAB and Djelia},
                journal={arXiv preprint},
                year={2025},
                url={https://huggingface.co/datasets/sudoping01/bambara-speech-recognition-benchmark}
            }
            </code>
            </pre>
            
            ### About the Collaboration
            
            This benchmark is a collaborative effort between:
            * **MALIBA-AI**
            * **Djelia**
            * **RobotsMali AI4D-LAB**

            **Mission**: "No Malian Language Left Behind" - Empowering Mali's linguistic diversity through AI innovation.
            """, 
            elem_classes="citation-section"
        )
    
    gr.HTML(
        """
        <center>
            <br><br>
            <p style="color: #7d3561; font-size: 18px; font-weight: bold;">
                A collaboration between MALIBA-AI, RobotsMali AI4D-LAB, and Djelia
            </p>
            <p style="color: #2f3b7d; font-size: 14px;">
                Advancing Speech Recognition Technology for African Languages
            </p>
            <br>
        </center>
        """
    )

if __name__ == "__main__":
    demo.launch(share=True)