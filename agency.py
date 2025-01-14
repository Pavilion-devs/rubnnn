from typing import List, Literal, Dict, Optional
from agency_swarm import Agent, Agency, set_openai_key, BaseTool
from pydantic import Field
import streamlit as st

# Set your OpenAI key
set_openai_key("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")

# Define tools
class AnalyzeProjectRequirements(BaseTool):
    project_name: str = Field(...)
    project_description: str = Field(...)
    project_type: Literal["Web Application", "Mobile App", "API Development",
                         "Data Analytics", "AI/ML Solution", "Other"] = Field(...)
    budget_range: Literal["$10k-$25k", "$25k-$50k", "$50k-$100k", "$100k+"] = Field(...)

    class ToolConfig:
        name = "analyze_project"
        description = "Analyzes project requirements and feasibility"

class CreateTechnicalSpecification(BaseTool):
    architecture_type: Literal["monolithic", "microservices", "serverless", "hybrid"]
    core_technologies: str
    scalability_requirements: Literal["high", "medium", "low"]

    class ToolConfig:
        name = "create_technical_spec"
        description = "Creates technical specifications based on project analysis"

# Define agents
ceo = Agent(
    name="Project Director",
    description="Experienced CEO with project evaluation expertise",
    instructions="""
    1. FIRST, use the AnalyzeProjectRequirements tool with:
       - project_name: The name from project details
       - project_description: The full project description
       - project_type: The type of project
       - budget_range: The specified budget range
    """,
    tools=[AnalyzeProjectRequirements],
    temperature=0.7
)

cto = Agent(
    name="Technical Architect",
    description="Senior technical architect with system design expertise",
    instructions="""
    1. WAIT for project analysis completion
    2. Use CreateTechnicalSpecification tool with:
       - architecture_type: Choose architecture
       - core_technologies: List main technologies
       - scalability_requirements: Set scalability needs
    """,
    tools=[CreateTechnicalSpecification]
)

product_manager = Agent(
    name="Product Manager",
    description="Experienced product manager for delivery excellence",
    instructions="""
    - Manage project scope and timeline
    - Define product requirements
    - Create potential products and features
    """,
    temperature=0.4
)

developer = Agent(
    name="Lead Developer",
    description="Senior full-stack developer",
    instructions="""
    - Plan technical implementation
    - Provide effort estimates
    - Review feasibility
    """
)

client_manager = Agent(
    name="Client Success Manager",
    description="Client delivery expert",
    instructions="""
    - Ensure satisfaction
    - Manage expectations
    - Handle feedback
    """
)

# Create agency
agency = Agency(
    [
        ceo, cto, product_manager, developer, client_manager,
        [ceo, cto],
        [ceo, product_manager],
        [cto, developer],
        [product_manager, client_manager]
    ],
    async_mode="threading"
)

# Streamlit app
def main():
    st.title("🚀 Company Planner")

    # Form for user input
    with st.form("project_form"):
        project_name = st.text_input("Project Name")
        project_description = st.text_area("Project Description")

        col1, col2 = st.columns(2)
        with col1:
            project_type = st.selectbox("Project Type", 
                ["Web Application", "Mobile App", "API Development", "Data Analytics", "AI/ML Solution", "Other"])
        with col2:
            budget_range = st.selectbox("Budget Range", ["$10k-$25k", "$25k-$50k", "$50k-$100k", "$100k+"])
        
        submit_button = st.form_submit_button("Submit")

    # Process input after form submission
    if submit_button:
        if not project_name or not project_description:
            st.error("Please fill in all fields.")
        else:
            try:
                # CEO analysis
                ceo_response = agency.get_completion(
                    message=f"""
                    Analyze this project:
                    Project Name: {project_name}
                    Project Description: {project_description}
                    Project Type: {project_type}
                    Budget Range: {budget_range}
                    """,
                    recipient_agent=ceo
                )
                # CTO specifications
                cto_response = agency.get_completion(
                    message="Review project analysis and create technical specifications",
                    recipient_agent=cto
                )
                # Product Manager response
                pm_response = agency.get_completion(
                    message="Provide product management analysis and roadmap",
                    recipient_agent=product_manager
                )

                # Display results in tabs
                tabs = st.tabs(["CEO's Analysis", "CTO's Specification", "PM's Plan"])
                with tabs[0]:
                    st.markdown(ceo_response)
                with tabs[1]:
                    st.markdown(cto_response)
                with tabs[2]:
                    st.markdown(pm_response)

            except Exception as e:
                st.error(f"An error occurred: {e}")

# Run the app
if __name__ == "__main__":
    main()
