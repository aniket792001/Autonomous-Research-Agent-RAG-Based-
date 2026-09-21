from langchain_core.prompts import PromptTemplate

def planner_agent(llm):
    prompt = PromptTemplate(
        input_variables=["query"],
        template="""
        Break the following research query into clear sub-questions:
        Query: {query}
        """
    )
    return prompt | llm
