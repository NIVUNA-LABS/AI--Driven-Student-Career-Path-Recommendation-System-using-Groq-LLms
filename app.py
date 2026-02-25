from groq import Groq
import streamlit as st
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

import PyPDF2
import docx


# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="AI Career Path System",
    layout="centered"
)


# ================= LIGHT THEME (WHITE) =================

st.markdown("""
<style>

/* Main Background */
.stApp {
    background-color: white;
    color: black;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    color: #222222;
}

/* Input Boxes */
input[type="text"],
input[type="number"],
textarea {
    background-color: white !important;
    color: black !important;
    border-radius: 8px;
    border: 1px solid #999;
    padding: 8px;
}

/* Select Box */
div[data-baseweb="select"] > div {
    background-color: white !important;
    color: black !important;
    border-radius: 8px;
    border: 1px solid #999;
}

/* Buttons */
.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
}

.stButton > button:hover {
    background-color: #1d4ed8;
}

/* File Uploader */
section[data-testid="stFileUploader"] {
    background-color: #f3f4f6;
    padding: 10px;
    border-radius: 8px;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: #f9fafb;
    color: black;
    padding: 15px;
    border-radius: 12px;
}

/* Tables */
table {
    color: black;
    background-color: white;
}

</style>
""", unsafe_allow_html=True)


# ================= TITLE =================

st.title("🚀 AI Career Path Recommendation System")


# ================= LOAD DATA =================

df = pd.read_csv(
    r"C:\Users\G.Hema Sri Devi\OneDrive\Desktop\career chatbot\data\data.csv"
)

df.columns = df.columns.str.strip().str.lower()


# ================= GROQ CLIENT =================

client = Groq(api_key="Groq key")   # <-- Add your API key


# ================= PROMPTS =================

ROADMAP_PROMPT_MARKDOWN = """
You are an expert career advisor.

Create a detailed roadmap in markdown.

User Profile:
- Current Role: {current_role}
- Skills: {skills}
- Target Role: {target_role}
- Time: {time_commitment} hrs/week

Include:
1. Skill gap
2. Learning path
3. Projects
4. Certifications
5. Interview prep
6. Salary

# 🚀 Career Roadmap
"""


ATS_PROMPT = """
You are an ATS expert.

Analyze resume for role: {role}

Give:

1. ATS Score
2. Missing Keywords
3. Strengths
4. Improvements
5. Tips

Resume:
{resume_text}

Return in markdown.
"""


# ================= SESSION =================

if "student" not in st.session_state:
    st.session_state.student = {}


# ================= AI ROADMAP =================

def generate_ai_roadmap(current_role, skills, target_role, time_commitment):

    prompt = ROADMAP_PROMPT_MARKDOWN.format(
        current_role=current_role,
        skills=", ".join(skills),
        target_role=target_role,
        time_commitment=time_commitment
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ================= RESUME READER =================

def extract_resume_text(file):

    text = ""

    if file.type == "application/pdf":

        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            text += page.extract_text() or ""


    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":

        doc_file = docx.Document(file)

        for para in doc_file.paragraphs:
            text += para.text + "\n"


    return text


# ================= ATS ANALYZER =================

def analyze_resume_ats(resume_text, role):

    prompt = ATS_PROMPT.format(
        role=role,
        resume_text=resume_text[:6000]
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ================= PDF =================

def generate_pdf(student, role, desc, matched, missing, roadmap):

    file = "career_report.pdf"

    doc = SimpleDocTemplate(file)

    styles = getSampleStyleSheet()

    content = []


    content.append(Paragraph("AI Career Guidance Report", styles["Title"]))

    content.append(Paragraph(f"Name: {student['name']}", styles["Normal"]))
    content.append(Paragraph(f"Role: {role}", styles["Normal"]))

    content.append(Paragraph("<br/>", styles["Normal"]))


    content.append(Paragraph("Role Description", styles["Heading2"]))
    content.append(Paragraph(desc, styles["Normal"]))


    content.append(Paragraph("Matched Skills", styles["Heading2"]))
    content.append(Paragraph(", ".join(matched), styles["Normal"]))


    content.append(Paragraph("Missing Skills", styles["Heading2"]))
    content.append(Paragraph(", ".join(missing), styles["Normal"]))


    content.append(Paragraph("Career Roadmap", styles["Heading2"]))
    content.append(Paragraph(roadmap.replace("\n", "<br/>"), styles["Normal"]))


    doc.build(content)

    return file


# ================= MENU =================

menu = st.selectbox(
    "Select Option",
    [
        "Student Details",
        "Enter Skills",
        "Choose Role",
        "Upload Resume (ATS Check)",
        "Get Recommendation"
    ]
)


# ================= STUDENT DETAILS =================

if menu == "Student Details":

    st.session_state.student["name"] = st.text_input("Name")

    st.session_state.student["degree"] = st.text_input("Degree")

    st.session_state.student["year"] = st.text_input("Year")

    st.session_state.student["time"] = st.number_input(
        "Study Hours / Week",
        1, 60, 10
    )


    if st.button("Save"):
        st.success("Details Saved ✅")


# ================= SKILLS =================

elif menu == "Enter Skills":

    text = st.text_area("Describe your skills & projects")


    if st.button("Extract Skills"):

        prompt = f"""
        Extract technical skills as comma list:

        {text}
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )


        skills = [
            s.strip().lower().replace(".", "")
            for s in response.choices[0].message.content.split(",")
            if len(s.strip()) > 1
        ]


        st.session_state.student["skills"] = skills

        st.success("Skills Extracted ✅")

        st.write(skills)


# ================= ROLE =================

elif menu == "Choose Role":

    role = st.selectbox(
        "Select Career",
        sorted(df["label"].unique())
    )


    if st.button("Save"):

        st.session_state.student["role"] = role.lower()

        st.success("Role Saved ✅")


# ================= RESUME ATS =================

elif menu == "Upload Resume (ATS Check)":

    st.subheader("📄 Resume ATS Analyzer")


    uploaded_file = st.file_uploader(
        "Upload Resume (PDF / DOCX)",
        type=["pdf", "docx"]
    )


    if uploaded_file and "role" in st.session_state.student:


        resume_text = extract_resume_text(uploaded_file)


        if len(resume_text.strip()) < 100:

            st.error("Resume not readable ❌")

        else:

            st.success("Resume uploaded ✅")


            if st.button("Analyze ATS Score"):


                result = analyze_resume_ats(
                    resume_text,
                    st.session_state.student["role"].title()
                )


                st.markdown(result, unsafe_allow_html=True)


    elif "role" not in st.session_state.student:

        st.warning("Please choose role first ⚠")


# ================= RECOMMENDATION =================

elif menu == "Get Recommendation":

    student = st.session_state.student


    if (
        "skills" in student and
        "role" in student and
        "name" in student and
        "time" in student
    ):


        rows = df[df["label"].str.lower() == student["role"]]


        required = []


        for s in rows["skills"]:

            required.extend([
                x.strip().lower()
                for x in s.replace(";", ",").split(",")
            ])


        required = list(set(required))


        matched = []
        missing = []


        for req in required:

            if any(req in s or s in req for s in student["skills"]):

                matched.append(req)

            else:

                missing.append(req)


        match_percentage = int(
            (len(matched) / len(required)) * 100
        ) if required else 0


        st.subheader("🎯 Career Recommendation")

        st.write("Role:", student["role"].title())

        st.metric("Skill Match", f"{match_percentage}%")


        desc = rows["description"].iloc[0]


        st.subheader("📄 Description")

        st.write(desc)


        st.subheader("🛠 Skills")


        st.markdown("### ✅ Matched")

        for s in matched:
            st.success(s)


        st.markdown("### ❌ Missing")

        for s in missing:
            st.error(s)


        st.subheader("🤖 AI Roadmap")


        roadmap = generate_ai_roadmap(
            student["role"].title(),
            student["skills"],
            student["role"].title(),
            student["time"]
        )


        st.markdown(roadmap, unsafe_allow_html=True)


        if st.button("Download Report"):


            file = generate_pdf(
                student,
                student["role"].title(),
                desc,
                matched,
                missing,
                roadmap
            )


            with open(file, "rb") as f:

                st.download_button(
                    "Download PDF",
                    f,
                    file_name=file
                )


    else:

        st.warning("Fill all details first ⚠")
