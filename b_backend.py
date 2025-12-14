# app.py
import streamlit as st
import base64
import io
import matplotlib.pyplot as plt
import traceback
import sys

# ----------------- UI / Helper functions -----------------


def setup_page():
    """Apply CSS and small JS fallback for logo errors."""
    apply_custom_css()

    # Add logo error fallback script (kept simple & safe)
    st.markdown(
        """
        <script>
        document.addEventListener('DOMContentLoaded' , function(){
            var logoImg = document.querySelector('.logo-image');
            if (logoImg){
                logoImg.onerror = function(){
                    var logoContainer = document.querySelector('.logo-container');
                    if (logoContainer) {
                        logoContainer.innerHTML = '<div style="font-size : 40px; color: white; text-align:center">/</div>';
                    }
                };
            }
        });
        </script>
        """,
        unsafe_allow_html=True,
    )


def display_header():
    """Render header with optional logo.jpg if present."""
    try:
        with open("logo.jpg", "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode()
            logo_html = f'<img src="data:image/jpeg;base64,{logo_base64}" alt="Logo" class="logo-image" style="max-height:200px;">'
    except Exception:
        logo_html = '<div style="font-size:50px; text-align: center; color: white;"></div>'

    st.markdown(
        f"""
        <div class="main-header">
            <div class="header-container">
                <div class="logo-container" style="text-align:center; margin-bottom:20px;">
                    {logo_html}
                </div>
                <div class="title-container" style="text-align:center;">
                    <h1 style="margin:0; color: white;">AI Powered Resume Analysis & Interview Preparation System</h1>
                    <p style="margin:0; color: #cccccc;">Smart Resume Analysis • Interview Preparation • Upgraded Resume </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_custom_css(accent_color="#d32f2f"):
    """Apply custom CSS with corrected braces and selectors."""
    st.markdown(
        f"""
        <style>
        /* Main container - target Streamlit main class minimally */
        .main {{
            background-color: #000000 !important;
            color: white !important;
        }}

        /* Activate tabs and highlights based on accent color (best-effort selector) */
        [role="tab"][aria-selected="true"] {{
            background-color: #000000 !important;
            border-bottom: 3px solid {accent_color} !important;
            color: {accent_color} !important;
        }}

        /* Buttons styled with accent color */
        .stButton button {{
            background-color: {accent_color} !important;
            color: white !important;
        }}

        .stButton button:hover {{
            filter: brightness(85%);
        }}

        /* Warning message */
        div.stAlert {{
            
            color: white !important;
        }}

        /* Input fields */
        .stTextInput input, .stTextArea textarea, .stSelectbox div {{
            background-color: #222222 !important;
            color: white !important;
        }}

        /* horizontal rule black and accent color gradient */
        hr {{
            border: none;
            height: 2px;
            background-image: linear-gradient(to right, black 50%, {accent_color} 50%);
        }}

        /* general markdown text */
        .stMarkdown, .stMarkdown p {{
            color: white !important;
        }}

        /* skill tags styling */
        .skill-tag {{
            display: inline-block;
            background-color: {accent_color};
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            margin: 5px;
            font-weight: bold;
        }}

        .skill-tag.missing {{
            background-color: rgba(68,68,68,0.6);
            color: #ccc;
        }}

        /* horizontal layout for strengths and improvements */
        .strengths-improvements {{
            display: flex;
            gap: 20px;
        }}

        .strengths-improvements > div {{
            flex: 1;
        }}

        /* card styling for sections */
        .card {{
            background-color: #111111;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid {accent_color};
        }}

        /* improvements suggestion styling */
        .improvement-item {{
            background-color: #222222;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}

        /* before after comparison */
        .comparison-container {{
            display: flex;
            gap: 20px;
            margin-top: 15px;
        }}

        .comparison-box {{
            flex: 1;
            background-color: #333333;
            padding: 15px;
            border-radius: 5px;
            color: #fff;
            font-family: monospace;
        }}

        /* weakness detail styling */
        .weakness-detail {{
            background-color: #330000;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #ff6666;
        }}

        /* solution styling */
        .solution-detail {{
            background-color: #003300;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #66ff66;
        }}

        /* example detail styling */
        .example-detail {{
            background-color: #000033;
            padding: 20px 15px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #6666ff;
        }}

        /* download button styling */
        .download-btn {{
            display: inline-block;
            background-color: {accent_color};
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            text-decoration: none;
            margin: 10px 0;
            text-align: center;
            
        }}

        .download-btn:hover {{
            filter: brightness(85%);
        }}

        /* pie chart container note */
        .pie-chart-container {{
            padding: 10px;
            background-color: #111111;
            border-radius: 10px;
            margin-bottom: 15px;
        }}
        
        
        </style>
        """,
        unsafe_allow_html=True,
    )


def setup_sidebar():
    import streamlit as st
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input("OpenAI API Key", type="password")
    return {"openai_api_key": api_key}


def role_selection_section(role_requirements):
    """Role selection card. Returns (role, custom_jd_file_or_None)."""
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        role = st.selectbox("Select the role you're applying for:", list(role_requirements.keys()))

    with col2:
        upload_jd = st.checkbox("Upload custom job description instead")

    custom_jd = None

    if upload_jd:
        custom_jd_file = st.file_uploader("Upload job description (PDF or TXT)", type=["pdf", "txt"])
        if custom_jd_file:
            st.success("Custom job description uploaded!")
            custom_jd = custom_jd_file

    if not upload_jd:
        st.info(f"Required skills: {', '.join(role_requirements[role])}")
        st.markdown(f"<p>Cutoff score for selection: <b>{75}/100</b></p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    return role, custom_jd


def resume_upload_section():
    """Resume upload UI. Returns uploaded file object or None."""
    st.markdown(
        """
        <div class="card">
            <h3 style="color:white"> Upload Your Resume</h3>
            <p style="color:#ccc">Supported format: PDF,DOCX</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_resume = st.file_uploader("", type=["pdf","docx"], label_visibility="collapsed")
    return uploaded_resume


def create_score_pie_chart(score):
    """Create a professional donut chart for the score visualization and return fig."""
    fig, ax = plt.subplots(figsize=(4, 4), facecolor='#111111')

    sizes = [score, max(0, 100 - score)]
    labels = ['', '']
    colors = ["#d32f2f", "#333333"]
    explode = (0.05, 0)

    wedges, texts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        explode=explode,
        startangle=90,
        wedgeprops={'width': 0.5, 'edgecolor': 'black', 'linewidth': 1},
    )

    center_circle = plt.Circle((0, 0), 0.25, fc='#111111')
    ax.add_artist(center_circle)

    ax.set_aspect('equal')

    ax.text(0, 0, f"{score}%", ha='center', va='center', fontsize=24, fontweight='bold', color='white')

    status = "PASS" if score >= 75 else "FAIL"
    status_color = "#4CAF50" if score >= 75 else "#d32f2f"
    ax.text(0, -0.15, status, ha='center', va='center', fontsize=14, fontweight='bold', color=status_color)

    ax.set_facecolor('#111111')
    plt.tight_layout()

    return fig


def display_analysis_results(analysis_result):
    """Render analysis results card (expects a dict)."""
    if not analysis_result:
        return

    overall_score = analysis_result.get('overall_score', 0)
    selected = analysis_result.get("selected", False)
    skill_scores = analysis_result.get("skill_scores", {})
    detailed_weakness = analysis_result.get("detailed_weakness", []) or analysis_result.get("detailed_weaknesses", [])
    strengths = analysis_result.get("strengths", [])
    missing_skills = analysis_result.get("missing_skills", [])

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align: right; font-size: 0.8rem; color: #888; margin-bottom: 10px;">Powered by Shashank And Madhavesh</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric("Overall Score", f"{overall_score}/100")
        fig = create_score_pie_chart(overall_score)
        st.pyplot(fig)

    with col2:
        if selected:
            st.markdown("<h2 style='color: #4CAF50;'>Congratulations! You have been shortlisted.</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='color: #d32f2f;'>Unfortunately, you were not selected.</h2>", unsafe_allow_html=True)
        st.write(analysis_result.get('reasoning', ''))

    st.markdown('<hr>', unsafe_allow_html=True)

    st.markdown('<div class="strengths-improvements">', unsafe_allow_html=True)

    # strengths
    st.markdown('<div>', unsafe_allow_html=True)
    st.subheader("Strengths")
    if strengths:
        for skill in strengths:
            st.markdown(f'<div class="skill-tag">{skill} ({skill_scores.get(skill, "N/A")}/10)</div>', unsafe_allow_html=True)
    else:
        st.write("No notable strengths identified.")
    st.markdown('</div>', unsafe_allow_html=True)

    # weaknesses
    st.markdown('<div>', unsafe_allow_html=True)
    st.subheader("Areas for improvement")
    if missing_skills:
        for skill in missing_skills:
            st.markdown(f'<div class="skill-tag missing">{skill} ({skill_scores.get(skill, "N/A")}/10)</div>', unsafe_allow_html=True)
    else:
        st.write("No significant areas for improvements.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Detailed weakness section
    if detailed_weakness:
        st.markdown('<hr>', unsafe_allow_html=True)
        st.subheader("Detailed Weakness Analysis")

        for weakness in detailed_weakness:
            skill_name = weakness.get('skill', '')
            score = weakness.get('score', 0)

            with st.expander(f"{skill_name} (Score: {score}/10)"):
                detail = weakness.get('detail', 'No specific details provided.')
                if isinstance(detail, str) and (detail.strip().startswith('```json') or '{' in detail):
                    detail = "The resume lacks concrete examples or well-formatted details for this skill."

                st.markdown(f'<div class="weakness-detail"><strong>Issue:</strong> {detail}</div>', unsafe_allow_html=True)

                if 'suggestions' in weakness and weakness['suggestions']:
                    st.markdown("<strong>How to improve:</strong>", unsafe_allow_html=True)
                    for i, suggestion in enumerate(weakness['suggestions']):
                        st.markdown(f'<div class="solution-detail">{i+1}. {suggestion}</div>', unsafe_allow_html=True)

                if 'example' in weakness and weakness['example']:
                    st.markdown("<strong>Example addition:</strong>", unsafe_allow_html=True)
                    st.markdown(f'<div class="example-detail">{weakness["example"]}</div>', unsafe_allow_html=True)

    st.markdown("___")

    # Downloadable report content
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        report_content = f"""# AI Powered Recruitment - Resume Analysis Report

## Overall Score: {overall_score}/100

Status: {"✅ Shortlisted" if selected else "❌ Not Selected"}

## Analysis Reasoning
{analysis_result.get('reasoning', 'No reasoning provided.')}

## Strengths
{', '.join(strengths) if strengths else 'None identified'}

## Missing / Improvement Areas
{', '.join(missing_skills) if missing_skills else 'None'}

## Detailed weakness Analysis
"""
        for weakness in detailed_weakness:
            skill_name = weakness.get('skill', '')
            score = weakness.get('score', 0)
            detail = weakness.get('detail', 'No specific details provided.')
            if isinstance(detail, str) and (detail.strip().startswith('```json') or '{' in detail):
                detail = "The resume lacks examples of this skill."

            report_content += f"\n### {skill_name} (Score: {score}/10)\n"
            report_content += f"Issue: {detail}\n"

            if 'suggestions' in weakness and weakness['suggestions']:
                report_content += "\nImprovement suggestions:\n"
                for i, sugg in enumerate(weakness['suggestions']):
                    report_content += f"- {sugg}\n"

            if 'example' in weakness and weakness['example']:
                report_content += f"\nExample: {weakness['example']}\n"

        report_content += "\n---\nAnalysis provided by AI Recruitment Agent"

        report_b64 = base64.b64encode(report_content.encode()).decode()
        href = f'<a class="download-btn" href="data:text/plain;base64,{report_b64}" download="resume_analysis.txt">📊 Download Analysis Report</a>'
        st.markdown(href, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def resume_qa_section(has_resume, ask_question_func=None):
    """Resume Q&A section — FIXED (no experimental_rerun)."""
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Ask Questions About the Resume")

    user_question = st.text_input(
        "Enter your question:",
        placeholder="E.g., What is the candidate's latest project?"
    )

    # Manual user question
    if user_question and ask_question_func and st.button("Ask this question"):
        with st.spinner("Generating answer..."):
            try:
                response = ask_question_func(user_question)
            except Exception as e:
                response = f"Error while answering question: {e}"

        st.markdown(
            '<div style="background-color:#111122; padding:15px; border-radius:6px; border-left:5px solid #d32f2f;">',
            unsafe_allow_html=True,
        )
        st.write(response)
        st.markdown("</div>", unsafe_allow_html=True)

    # Example Q&A buttons — FIXED (no rerun)
    with st.expander("Example Questions (Recruiter-style)"):
        example_questions = [
            "What is the candidate's most recent role?",
            "What are the candidate's primary technical skills?",
            "How many years of experience does the candidate have?",
            "Does the candidate mention leadership or team management?",
            "What projects has the candidate completed?",
            "Are there measurable achievements in the resume?",
            "Does the resume show domain expertise?",
        ]

        for question in example_questions:
            if st.button(f"🔹 {question}", key=f"exa_{question}"):
                with st.spinner("Generating answer..."):
                    try:
                        response = ask_question_func(question)
                    except Exception as e:
                        response = f"Error while answering question: {e}"

                st.markdown(
                    f'<div style="margin-top:10px; background-color:#111122; padding:15px; border-radius:6px; border-left:5px solid #1976d2;">'
                    f'<b>Q:</b> {question}<br><br>',
                    unsafe_allow_html=True,
                )
                st.write(response)
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def interview_questions_section(has_resume, generate_questions_func=None):
    """Generate interview questions based on selected types and difficulty."""
    if not has_resume:
        st.markdown("Please upload and analyze a resume first.")
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        question_types = st.multiselect(
            "Select question types:",
            ["Basic", "Technical", "Experience", "Scenario", "Coding", "Behavioral"],
            default=["Basic", "Technical"],
        )

    with col2:
        difficulty = st.select_slider(
            "Question difficulty:", options=["Easy", "Medium", "Hard"], value="Medium"
        )

    num_questions = st.slider("Number of questions:", 3, 15, 5)

    if st.button("Generate Interview Questions"):
        if generate_questions_func:
            with st.spinner("Generating personalized interview questions..."):
                questions = generate_questions_func(
                    question_types, difficulty, num_questions
                )

                download_content = f"# AI Powered - Interview Questions\n\n"
                download_content += f"Difficulty: {difficulty}\n"
                download_content += f"Types: {', '.join(question_types)}\n\n"

                for i, item in enumerate(questions):
                    if isinstance(item, (list, tuple)) and len(item) == 2:
                        q_type, question = item
                    else:
                        q_type = "General"
                        question = str(item)

                    with st.expander(f"{q_type}: {question[:50]}..."):
                        st.write(question)

                        if q_type == "Coding":
                            st.code("# Write your solution here", language="python")

                    download_content += f"## {i+1}. {q_type} Question\n\n"
                    download_content += f"{question}\n\n"
                    if q_type == "Coding":
                        download_content += "```python\n# Write your solution here\n```\n\n"

                download_content += "\n---\nQuestions generated by AI Powered Resume Analyzer And Interview Question Generator"

                if questions:
                    st.markdown("---")
                    questions_bytes = download_content.encode()
                    b64 = base64.b64encode(questions_bytes).decode()
                    href = f'<a class="download-btn" href="data:text/markdown;base64,{b64}" download="interview_question.md">📝 Download All Questions</a>'
                    st.markdown(href, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def resume_improvement_section(has_resume, improve_resume_func=None):
    """Generate resume improvement suggestions and allow downloads."""
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)

    improvements_areas = st.multiselect(
        "Select areas to improve:",
        [
            "Content",
            "Format",
            "Skills Highlighting",
            "Experience Description",
            "Education",
            "Projects",
            "Achievements",
            "Overall Structure",
        ],
        default=["Content", "Skills Highlighting"],
    )

    target_role = st.text_input(
        "Target role (optional):", placeholder="e.g., Senior Data Scientist at VCTM"
    )

    if st.button("Generate Resume Improvements"):
        if improve_resume_func:
            with st.spinner("Analyzing and generating improvements..."):
                improvements = improve_resume_func(improvements_areas, target_role)

                download_content = (
                    f"# AI Powered Resume Analyzer And Interview Question Generator\n\n"
                )
                download_content += (
                    f"Target Role: {target_role if target_role else 'Not specific'}\n\n"
                )

                for area, suggestions in improvements.items():
                    with st.expander(f"Improvements for {area}", expanded=True):
                        st.markdown(
                            f"<p>{suggestions.get('description', '')}</p>",
                            unsafe_allow_html=True,
                        )

                        st.subheader("Specific Suggestions")
                        for i, suggestion in enumerate(
                            suggestions.get("specific", [])
                        ):
                            st.markdown(
                                f'<div class="solution-detail"><strong>{i+1}. </strong> {suggestion}</div>',
                                unsafe_allow_html=True,
                            )

                        if "before_after" in suggestions:
                            st.markdown(
                                '<div class="comparison-container">',
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                '<div class="comparison-box">', unsafe_allow_html=True
                            )
                            st.markdown(
                                "<strong>Before:</strong>", unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<pre>{suggestions['before_after'].get('before','')}</pre>",
                                unsafe_allow_html=True,
                            )
                            st.markdown("</div>", unsafe_allow_html=True)

                            st.markdown(
                                '<div class="comparison-box">', unsafe_allow_html=True
                            )
                            st.markdown(
                                "<strong>After:</strong>", unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<pre>{suggestions['before_after'].get('after','')}</pre>",
                                unsafe_allow_html=True,
                            )
                            st.markdown("</div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)

                    download_content += f"## Improvements for {area}\n\n"
                    download_content += f"{suggestions.get('description','')}\n\n"
                    download_content += "### Specific Suggestions \n\n"
                    for i, suggestion in enumerate(suggestions.get("specific", [])):
                        download_content += f"{i+1}. {suggestion}\n"
                    download_content += "\n"

                    if "before_after" in suggestions:
                        download_content += "### Before\n\n"
                        download_content += (
                            f"```\n{suggestions['before_after'].get('before','')}\n```\n\n"
                        )
                        download_content += "### After\n\n"
                        download_content += (
                            f"```\n{suggestions['before_after'].get('after','')}\n```\n\n"
                        )

                download_content += "\n---\n Provided by AI resume enhancer."

                st.markdown("---")
                report_bytes = download_content.encode()
                b64 = base64.b64encode(report_bytes).decode()
                href = f'<a class="download-btn" href="data:text/markdown;base64,{b64}" download="resume_improvements.md"> Download All Suggestions</a>'
                st.markdown(href, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def improved_resume_section(has_resume, get_improved_resume_func=None):
    """Generate an improved resume and allow downloads."""
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)

    target_role = st.text_input(
        "Target role:", placeholder="e.g., Senior Software Engineer"
    )
    highlight_skills = st.text_area(
        "Paste your JD to get updated Resume",
        placeholder="e.g., Python, React, Cloud Architecture",
    )

    template_style = st.selectbox(
    "Choose Resume Template Style:",
    ["Classic", "Modern", "Minimal", "ATS Friendly", "Creative"]
    )


    if st.button("Generate Improved Resume"):
        if get_improved_resume_func:
            with st.spinner("Creating improved resume..."):
                improved_resume = get_improved_resume_func(
                    target_role, highlight_skills,template_style
                )

                st.subheader("Improved Resume")
                st.text_area("", improved_resume, height=400)
                 # ⭐ NEW — PDF Generation (calling agent inside Streamlit)
                # ⭐ FIXED PDF Generation
                try:
                    agent = st.session_state.get("resume_agent")

                    if agent is None:
                        raise Exception("Agent not initialized. Please analyze a resume first.")

                    pdf_bytes = agent.generate_pdf_resume(improved_resume, template_style)

                    st.download_button(
                        label="📄 Download as PDF",
                        data=pdf_bytes,
                        file_name=f"Improved_Resume_{template_style}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")
                    st.text(traceback.format_exc())


                col1, col2 = st.columns(2)

                with col1:
                    resume_bytes = improved_resume.encode()
                    b64 = base64.b64encode(resume_bytes).decode()
                    href = f'<a class="download-btn" href="data:file/txt;base64,{b64}" download="improved_resume.txt"> Download as TXT</a>'
                    st.markdown(href, unsafe_allow_html=True)

                with col2:
                    md_content = f"""# {target_role if target_role else 'Professional'} Resume
{improved_resume}

----
Resume Enhanced By AI
"""
                    md_bytes = md_content.encode()
                    md_b64 = base64.b64encode(md_bytes).decode()
                    md_href = f'<a class="download-btn" href="data:text/markdown;base64,{md_b64}" download="improved_resume.md"> Download as Markdown</a>'
                    st.markdown(md_href, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def create_tabs():
    return st.tabs(
        [
            "Resume Analysis",
            "Resume Q&A",
            "Interview Question",
            "Resume Improvement",
            "Improved Resume",
        ]
    )
