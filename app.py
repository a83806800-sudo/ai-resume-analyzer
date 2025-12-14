import streamlit as st
import atexit

from agents import ResumeAnalysisAgent
import b_backend

# ----------------- ROLE REQUIREMENTS -----------------

ROLE_REQUIREMENTS = {
    "AI/ML Engineer": [
        "Python", "PyTorch", "TensorFlow", "Machine Learning", "Deep Learning", "MLOps",
        "Scikit-Learn", "NLP", "Computer Vision", "Reinforcement Learning", "Hugging Face",
        "Data Engineering", "Feature Engineering", "AutoML"
    ],

    "Frontend Engineer": [
        "React", "Vue", "Angular", "HTML5", "CSS3", "Javascript", "Typescript", "Next.js",
        "Svelte", "Bootstrap", "Tailwind CSS", "GraphQL", "Redux", "WebAssembly", "Three.js",
        "Performance Optimization"
    ],

    "Backend Engineer": [
        "Python", "Java", "Node.js", "REST APIs", "Cloud services", "Kubernetes", "Docker",
        "GraphQL", "Microservices", "gRPC", "Spring Boot", "Flask", "FastAPI",
        "SQL & NoSQL Databases", "Redis", "RabbitMQ", "CI/CD"
    ],

    "Data Engineer": [
        "Python", "SQL", "Apache Spark", "Hadoop", "Kafka", "ETL Pipelines", "Airflow",
        "BigQuery", "Redshift", "Data Warehousing", "Snowflake", "Azure Data Factory",
        "GCP", "AWS Glue", "DBT"
    ],

    "DevOps Engineer": [
        "Kubernetes", "Docker", "Terraform", "CI/CD", "AWS", "Azure", "GCP", "Jenkins",
        "Ansible", "Promethus", "Grafana", "Helm", "Linux Administration",
        "Networking", "Site Reliability Engineering (SRE)"
    ],

    "Full Stack Developer": [
        "JavaScript", "TypeScript", "React", "Node.js", "Express", "MongoDB", "SQL", "HTML5",
        "CSS3", "RESTful APIs", "Git", "CI/CD", "Cloud Services", "Responsive Design",
        "Authentication & Authorization"
    ],

    "Product Manager": [
        "Product Strategy", "User Research", "Agile Methodologies", "Roadmapping",
        "Market Analysis", "Stakeholder Management", "Data Analysis", "User Stories",
        "Product Lifecycle", "A/B Testing", "KPI Definition", "Prioritization",
        "Competitive Analysis", "Customer Journey Mapping"
    ],

    "Data Scientist": [
        "Python", "R", "SQL", "Machine Learning", "Statistics", "Data Visualization",
        "Pandas", "Numpy", "Scikit-learn", "Jupyter", "Hypothesis Testing",
        "Experimental Design", "Feature Engineering", "Model Evaluation"
    ],

    "Data Analyst": [
    "Python", "SQL", "R", "Data Analysis", "Data Cleaning", "Data Wrangling",
    "Data Visualization", "Tableau", "Power BI", "Excel", "Advanced Excel",
    "Pivot Tables", "Dashboards", "Statistics", "Hypothesis Testing",
    "A/B Testing", "Regression Analysis", "Time Series Analysis",
    "Pandas", "NumPy", "Jupyter", "Business Intelligence",
    "ETL", "Data Warehousing", "SQL Optimization",
    "Stakeholder Communication", "Data Storytelling"
    ]


}

# ------------------ STREAMLIT INIT ------------------

st.set_page_config(
    page_title="AI Powered Resume Analysis And Interview Preparation System",
    layout="wide",
)

if 'resume_agent' not in st.session_state:
    st.session_state.resume_agent = None

if 'resume_analyzed' not in st.session_state:
    st.session_state.resume_analyzed = False

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None


# ----------------- AGENT SETUP -----------------

def setup_agent(config):
    if not config["openai_api_key"]:
        st.error("⚠ Please enter your OpenAI API key in the sidebar.")
        return None

    if st.session_state.resume_agent is None:
        st.session_state.resume_agent = ResumeAnalysisAgent(
            api_key=config["openai_api_key"]
        )
    else:
        st.session_state.resume_agent.api_key = config["openai_api_key"]

    return st.session_state.resume_agent


def analyze_resume(agent, resume_file, role, custom_jd):
    if not resume_file:
        st.error("Please upload a resume.")
        return None

    with st.spinner("Analyzing resume..."):
        if custom_jd:
            result = agent.analyze_resume(resume_file, custom_jd=custom_jd)
        else:
            result = agent.analyze_resume(
                resume_file,
                role_requirements=ROLE_REQUIREMENTS[role]
            )

        st.session_state.resume_analyzed = True
        st.session_state.analysis_result = result
        return result


def ask_question(agent, question):
    with st.spinner("Thinking..."):
        return agent.ask_question(question)


def generate_interview_questions(agent, types, difficulty, num):
    with st.spinner("Generating questions..."):
        return agent.generate_interview_questions(types, difficulty, num)


def improve_resume(agent, areas, role):
    with st.spinner("Generating improvements..."):
        return agent.improve_resume(areas, role)


def get_improved_resume(agent, role, skills,template):
    with st.spinner("Creating improved resume..."):
        return agent.get_improved_resume(role, skills,template)


def cleanup():
    if st.session_state.resume_agent:
        st.session_state.resume_agent.cleanup()


atexit.register(cleanup)


# ---------------------- MAIN APP ----------------------

def main():
    b_backend.setup_page()
    b_backend.display_header()

    config = b_backend.setup_sidebar()
    agent = setup_agent(config)

    tabs = b_backend.create_tabs()

    # ---------------- TAB 1: Resume Analysis ----------------
    with tabs[0]:
        role, custom_jd = b_backend.role_selection_section(ROLE_REQUIREMENTS)
        uploaded_resume = b_backend.resume_upload_section()

        if st.button("Analyze Resume", type="primary"):
            if agent and uploaded_resume:
                analyze_resume(agent, uploaded_resume, role, custom_jd)

        if st.session_state.analysis_result:
            b_backend.display_analysis_results(st.session_state.analysis_result)

    # ---------------- TAB 2: Resume Q&A ----------------
    with tabs[1]:
        if st.session_state.resume_analyzed:
            b_backend.resume_qa_section(
                True,
                ask_question_func=lambda q: ask_question(agent, q)
            )
        else:
            st.warning("Please analyze a resume first.")

    # ---------------- TAB 3: Interview Questions ----------------
    with tabs[2]:
        if st.session_state.resume_analyzed:
            b_backend.interview_questions_section(
                True,
                generate_questions_func=lambda t, d, n:
                generate_interview_questions(agent, t, d, n)
            )
        else:
            st.warning("Please analyze a resume first.")

    # ---------------- TAB 4: Resume Improvements ----------------
    with tabs[3]:
        if st.session_state.resume_analyzed:
            b_backend.resume_improvement_section(
                True,
                improve_resume_func=lambda a, r: improve_resume(agent, a, r)
            )
        else:
            st.warning("Please analyze a resume first.")

    # ---------------- TAB 5: Improved Resume ----------------
    with tabs[4]:
        if st.session_state.resume_analyzed:
            b_backend.improved_resume_section(
                True,
                get_improved_resume_func=lambda r, s, template:
                get_improved_resume(agent, r, s, template)
            )
        else:
            st.warning("Please analyze a resume first.")


if __name__ == "__main__":
    main()
