import gradio as gr
from utils.utils_fuunctions import (

    load_references,
    mask_sensitive_info,
    run_command,
    git_pull,
    git_add_commit_push,
    normalize_text,
    calculate_metrics,
    format_as_percentage,
    add_medals_to_models,
    get_current_leaderboard,
    prepare_leaderboard_for_display,
    df_to_html,
    get_model_performance_table,
    compare_models,
    process_submission,
    create_main_leaderboard
)
import os
from settings.models import Settings
from assets.styles.styles import (
    get_logo_html,
    new_header_html,
    google_style_css
)

config = Settings()

run_command(["git", "config", "--global", "user.email", config.github_email])
run_command(["git", "config", "--global", "user.name", "HF Space"])

remote_url = f"https://{config.github_user}:{config.github_token}@github.com/{config.github_repo}.git"
run_command(["git", "remote", "set-url", "--push", "origin", remote_url], check=True, capture_output=True)  

git_pull()

references = load_references()

leaderboard_file = config.leaderboard_file
logo_path = config.logo_path

if not os.path.exists(leaderboard_file):
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
    git_add_commit_push("Initialize leaderboard with sample data")

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
            
                def process_submission_wrapper(model_name, csv_file):
                    return process_submission(model_name, csv_file, references)
                
                submit_btn.click(
                    fn=process_submission_wrapper,
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
