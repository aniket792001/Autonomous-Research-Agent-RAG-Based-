from langchain_core.prompts import PromptTemplate

def synthesis_agent(llm):
    prompt = PromptTemplate(
        input_variables=["context"],
        template="""
        Using the information below, generate a well-structured research answer:
        {context}
        """
    )
    return prompt | llm
