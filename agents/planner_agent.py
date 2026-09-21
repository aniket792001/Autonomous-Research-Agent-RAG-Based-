from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def planner_agent(llm):
    prompt = PromptTemplate(
        input_variables=["query"],
        template="""
        Break the following research query into clear sub-questions:
        Query: {query}
        """
    )
    return LLMChain(llm=llm, prompt=prompt)
