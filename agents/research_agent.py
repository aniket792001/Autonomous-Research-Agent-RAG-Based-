def research_agent(sub_question, vector_store):
    docs = vector_store.similarity_search(sub_question, k=3)
    return " ".join([doc.page_content for doc in docs])
