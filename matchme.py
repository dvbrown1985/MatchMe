import requests
import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup
import google.generativeai as genai

GENAI_API_KEY = "AIzaSyAfxmrmwhu62afqajL84gI5hta6LDUs9yc"  # Replace with your actual API key
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-001")

LOGO = "MatchMe.png"
image = Image.open('MatchMe.png')

st.logo(LOGO)

if "messages" not in st.session_state:
    st.session_state.messages = []
    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Configure Streamlit app settings
st.set_page_config(
    page_title="MatchMe",
    page_icon="🧩 ",
    layout="centered",
)

container1 = st.container(border=True)
with container1:
    st.image(image, caption=None, use_container_width=True)

# Disclaimer
expander = st.expander("Disclaimer and Product Information")
expander.write('''

    This is a prototype under development and may contain bugs or errors. It is intended for educational and research purposes only. 
    
    If you test the prototype, please note the following:

    - The app might be rate-limited with sub-optimal performance due to free services and usage limitations.

    - Limits on the number of concurrent users are in effect.

    The outputs are developed and output from the Google Gemini LLM.
    
    MatchMe is powered by the following resources:
    
    - Beautiful Soup
    - Google Gemini
    - Python
    - Streamlit

    ''')

container_1 = st.container(border=True)
with container_1:
    st.markdown("""
    <div>
        <h3 style="text-align:center;">Match Your Resume. Get the Job.</h3>
        <p style="font-size:17px; line-height:1.6;">
            MatchMe is designed to analyze a job posting against a job seeker's education, experience, and skills. 
        </p>
        <p style="font-size:17px; line-height:1.6;">
            Simply provide a job posting URL and information from your resume and AI will do the rest. 
        </p>
    </div>
    """, unsafe_allow_html=True)

with st.form("my_form"):

    st.info('For best results, please input job postings obtained directly from career sites. Job postings from aggregators like Indeed or LinkedIn may be blocked.')
    
    job_posting_url = st.text_input("Please Input the Job Posting URL")

    # Define 'label' before using it
    label = "Please Input Your Education, Skills, and Work Experience"  # Or any other suitable label

    job_seeker_experience = st.text_area(
        label=label, 
        height=None, 
        max_chars=None, 
        key=None, 
        help=None, 
        on_change=None, 
        args=None, 
        kwargs=None, 
        placeholder=None, 
        disabled=False, 
        label_visibility="visible"
    )

    # Only one submit button is needed
    submitted = st.form_submit_button(label="Submit", type="secondary", use_container_width=True)  # Combined options

    if submitted: # Check if the form was submitted
        # Process the form data here
        
        container_2 = st.container(border=True)
        with container_2:
            with st.spinner("Scraping job posting..."):
                # Send a GET request to the webpage
                response = requests.get(job_posting_url)

                # Check if the request was successful
                if response.status_code == 200:
                    # Parse the HTML content using BeautifulSoup
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract all the text from the page
                    job_description = soup.get_text(separator="\n", strip=True)
                    st.success('Job Posting Scraped!', icon="🤖")
                else:
                    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

        clean_job_description = f"""
            **Instructions:** You are a helpful assistant tasked with extracting specific information from job postings based on provided text.  Please extract and provide *only* the following information, formatted as specified below.  Disregard any other information present in the text, including but not limited to company descriptions, company logos, location information, demographic questions, voluntary self-identification sections (disability, veteran status, etc.), equal opportunity statements, privacy policies, application forms, or calls to action to apply.  Focus *only* on the job description, required qualifications, and required experience.
            **Task:** Here is the provided text to review: {job_description}
            ** Example Output **:

            1. About the role:.
                This paragraph introduces the role or job and most likely represents the role in a narrative format.
            2. What you'll be doing:
                - job duties and activities in a bullet point format. Each job duty or activity should be it's own bullet point.
            3. What you should bring, experience, qualifications
                - job qualifications, attributes, and experience.

            **Important Considerations:**

            * If a section (job description, qualifications, or experience) is not explicitly present in the job posting, simply write "N/A" after the corresponding heading (e.g., "Required Qualifications: N/A").
            * Focus on extracting the information as written and completely.  Do not attempt to interpret or infer anything that is not explicitly stated in the job posting.
            * If the job posting lists "preferred or nice to have" qualifications or experience in addition to "required" ones, include the preferred items in the appropriate section (qualifications or experience) and clearly label them as "Preferred" within the section.

            """

        container_3 = st.container(border=True)
        with container_3:
            with st.spinner("Cleaning Job Posting..."):
                response = model.generate_content(clean_job_description)
                cleaned_job_description = "".join(chunk.candidates[0].content.parts[0].text for chunk in response)
            st.success('Job Posting Cleaned!', icon="🤖")

        analyze_experience_against_job_description = f"""
            **Instructions:** You are a helpful assistant tasked with comparing a job seeker's experience against a job posting. You need to analyze the the provided job seeker experience such as education, experience, and skills to determine if the job seeker is a **Strong Match**, **Partial Match**, or **Weak Match** against the job posting. 
            **Information for analysis:** 
            - Here is the job posting text to review: {cleaned_job_description}
            - Here is the job seeker's experience to review: {job_seeker_experience}

            ** Example Output **: Do not add additional narrative or context other than the structure listed below. Output format must be in markdown. Do not output any HTML code or tags such as <br>. You must include a line break before and after each category in the example output.
    
                1. Overall match assessment: Make this line Bold. Use Line Breaks to make the content readable and intuitive. Use bullet points to segment the output. Make sure the bullet points are indented. 
                    - **Strong Match** List the reasons why the job seeker's experience is a strong match to the job posting. Or,
                    - **Partial Match** List the reasons why the job seeker's experience is a partial match to the job posting. Or,
                    - **Weak Match** List the reasons why the job seeker's experience is a weak match to the job posting.
                    <insert line break> do not output <br>
                2. Relevant Experience: Make this line Bold. Use Line Breaks to make the content readable and intuitive. Use bullet points to segment the output.Make sure the bullet points are indented.Make sure the bullet points are indented.
                    - List the relevant job seekers experience and explain how and why it matches the requirements of the job postings.
                    <insert line break> do not output <br>
                3. Experience Gaps: Make this line Bold. Use Line Breaks to make the content readable and intuitive. Use bullet points to segment the output. Make sure the bullet points are indented. Make sure the bullet points are indented.
                    - List any experience requirements not present in the job seeker's provided experience. Provide an explanation as to why this required experience is important to the role.
                    <insert line break> do not output <br>
                3. Skills Assessment: Make this line Bold. Use Line Breaks to make the content readable and intuitive. Use bullet points to segment the output. Make sure the bullet points are indented.
                    - List the relevant job seeker skills that are most applicable to this role and how they can be applied to the role.
                    <insert line break> do not output <br>
                4. Skill Gap Analysis: Make this line Bold. Use Line Breaks to make the content readable and intuitive. Use bullet points to segment the output. Make sure the bullet points are indented.
                    - List any missing skills not listed in the job seeker experience that are required in the job posting. Provide a concise recommendation on how to develop the skill.
                    <insert line break> do not output <br>
                5. Creating a Tailored Resume: Make this line Bold. Use Line Breaks to make the content readable and intuitive. Use bullet points to segment the output. Make sure the bullet points are indented.
                    - Provide 5 to 7 recommendations to the job seeker for creating a tailored resume for the job posting that highlights their strengths and qualifications.
                    <insert line break> do not output <br>
                6. Creating a Cover Letter: Make this line Bold. Use Line Breaks to make the content readable and intuitive. Use bullet points to segment the output. Make sure the bullet points are indented.
                    - Provide 5 to 7 recommendations to the job seeker for creating a tailored cover letter for the job posting that highlights their strengths and qualifications.
                    <insert line break> do not output <br>
                7. Interview Questions for the Employer: Make this line Bold. Use Line Breaks to make the content readable and intuitive. Use bullet points to segment the output. Make sure the bullet points are indented.
                    - Provide 5 to 7 recommended interview questions for the job seeker to ask of the hiring team.
                    <insert line break> do not output <br>
                8. Interview Questions to Prepare the Job Seeker: Make this line Bold. Make this line Bold. Use Line Breaks to make the content readable and intuitive. Use bullet points to segment the output. Make sure the bullet points are indented.
                    - Provide 5 to 7 questions for the job seeker to reflect upon in order to prepare them for a discussion with the hiring team.
                    <insert line break> do not output <br>
            """

        container_4 = st.container(border=True)
        with container_4:
            with st.spinner("Analyzing Job Post and Job Seeker Qualifications..."):
                response1 = model.generate_content(analyze_experience_against_job_description)
                match_assessment = "".join(chunk.candidates[0].content.parts[0].text for chunk in response1)
            st.success('Matching Analysis Complete!', icon="🤖")

        st.session_state.messages.append({"role": "assistant", "content": match_assessment})
        
        with st.chat_message("assistant"):
            st.markdown(match_assessment)
