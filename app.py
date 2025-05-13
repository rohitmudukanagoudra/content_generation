import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from utils.add_utils import set_bg_hack, get_base64_image
from scraper.webpage_scraper import scrape_homepage
from agents.crew_setup import build_marketing_crew

class MSightApp:
    def __init__(self):
        st.set_page_config(
            page_title="M-Sight - AI Creator in your Pocket!",
            page_icon=":sparkles:",
            layout="wide"
        )
        # Initialize session state variables
        defaults = {
            "url": None,
            "scraped": False,
            "data": None,
            "draft": False,
            "kickoff_result": None,
            "crew": None,
            "draft_task_id": None,
            "draft_text": None,
            "feedback": None,
            "feedback_submitted": False,
            "refined_result": None,
            "refined_text": None,
        }
        for key, val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = val

        self.render_header()
        self.step_scrape()
        self.step_generate_draft()
        self.step_feedback()
        self.step_video()

    def render_header(self):
        st.markdown("""
            <style>
                footer {visibility: hidden;}
                header {visibility: hidden;}
                div.block-container {padding-top:2rem;}
            </style>
        """, unsafe_allow_html=True)
        set_bg_hack('images/background.png')

        with stylable_container(
            key="container_headers",
            css_styles="""
            {
                padding: 24px;
                padding-top: 0px;
                overflow: hidden;
                box-sizing: border-box;
                position:relative;
            }
            """
        ):
            logo = get_base64_image("images/product_logo.png")
            if logo:
                st.markdown(
                    f"""<div style="text-align:center;">
                            <img src="data:image/png;base64,{logo}"
                                 style="width:47px;height:47px;border-radius:60%;">
                        </div>""",
                    unsafe_allow_html=True
                )
            st.markdown("")
            st.markdown(
                """<p style='text-align: center; color: #F3F3F3; font-family: "Proxima Nova"; font-size: 28px; font-weight: 600;'>M-Sight</p>""",
                unsafe_allow_html=True
            )
            st.markdown(
                """<p style='text-align: center; color: #F3F3F3; font-family: "Proxima Nova"; font-size: 24px; font-weight: 700;'>AI Creator in your Pocket!</p>""",
                unsafe_allow_html=True
            )
            st.markdown("")

    def step_scrape(self):
        with stylable_container(
            key="container_a",
            css_styles="""
            {
                background-color: #F3F3F3;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 24px;
                overflow: hidden;
                box-sizing: border-box;
                position:relative;
            }
            """
        ):
            st.write("### 1. Enter the URL of the website to scrape")
            with st.form("scrape_form", clear_on_submit=False):
                url_input = st.text_input(
                    "Website URL",
                    value=st.session_state.url or ""
                )
                submitted = st.form_submit_button("Load Website Data")
                if submitted and url_input:
                    st.session_state.url = url_input
                    with st.spinner("Scraping data…"):
                        st.session_state.data = scrape_homepage(url_input)
                    st.session_state.scraped = True

            if st.session_state.scraped and st.session_state.data:
                st.write("#### Titles")
                st.write(st.session_state.data["titles"])
                st.write("#### Paragraphs")
                st.write(st.session_state.data["paragraphs"])

    def step_generate_draft(self):
        if not st.session_state.scraped:
            return

        with stylable_container(
            key="container_generate",
            css_styles="""
            {
                background-color: #F3F3F3;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 24px;
                overflow: hidden;
                box-sizing: border-box;
                position:relative;
            }
            """
        ):
            st.write("### 2. Generate Draft Prompt")
            with st.form("draft_form"):
                generate = st.form_submit_button("Generate Draft Prompt")
                if generate:
                    # 1) Build and store the Crew
                    crew = build_marketing_crew()
                    st.session_state.crew = crew

                    # 2) Kick off the crew, feeding the scraped data into the first task
                    #    Task name: "AnalyzeData"
                    with st.spinner("Generating draft…"):
                        kickoff_result = crew.kickoff(
                            inputs={"AnalyzeData": st.session_state.data}
                        )
                    st.session_state.kickoff_result = kickoff_result
                    st.session_state.draft = True

                    # 3) Extract the DraftScript output (it's the 2nd task in sequence)
                    draft_output = kickoff_result.tasks_output[1]
                    st.session_state.draft_text = draft_output.raw

                    # 4) Capture the true task_id for replay
                    st.session_state.draft_task_id = crew.tasks[1].id

            if st.session_state.draft:
                st.chat_message("assistant").write(
                    st.session_state.draft_text
                )

    def step_feedback(self):
        if not st.session_state.draft:
            return

        with stylable_container(
            key="container_feedback",
            css_styles="""
            {
                background-color: #F3F3F3;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 24px;
                overflow: hidden;
                box-sizing: border-box;
                position:relative;
            }
            """
        ):
            st.write("### 3. Your Feedback / Additional Info")
            with st.form("feedback_form"):
                fb = st.text_input(
                    "Feedback",
                    value=st.session_state.feedback or ""
                )
                submit_fb = st.form_submit_button("Submit Feedback")
                if submit_fb and fb:
                    st.session_state.feedback = fb
                    with st.spinner("Refining…"):
                        # Replay only the DraftScript task (task 2) with the feedback
                        crew = st.session_state.crew
                        refined_result = crew.replay(
                            task_id=st.session_state.draft_task_id,
                            inputs={"feedback": fb}
                        )
                    st.session_state.refined_result = refined_result
                    # Extract updated draft from tasks_output[1]
                    refined_output = refined_result.tasks_output[1]
                    st.session_state.refined_text = refined_output.raw
                    st.session_state.feedback_submitted = True

            if st.session_state.feedback_submitted:
                st.chat_message("assistant").write(
                    st.session_state.refined_text
                )

    def step_video(self):
        if not st.session_state.feedback_submitted:
            return

        with stylable_container(
            key="container_video",
            css_styles="""
            {
                background-color: #F3F3F3;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 24px;
                overflow: hidden;
                box-sizing: border-box;
                position:relative;
            }
            """
        ):
            st.write("### 4. Generate Video")
            if st.button("Generate Video"):
                st.chat_message("assistant").write(
                    "Video generation service is not available yet."
                )

if __name__ == "__main__":
    MSightApp()
