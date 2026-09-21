import streamlit as st
from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline

from rag.loader import load_documents
from rag.embeddings import get_embeddings
from rag.vector_store import create_vector_store
from agents.planner_agent import planner_agent
from agents.research_agent import research_agent
from agents.synthesis_agent import synthesis_agent

st.title("🧠 Autonomous Research Agent")

query = st.text_input("Enter your research question:")

if query:
    llm = HuggingFacePipeline(
        pipeline=pipeline("text-generation", model="google/flan-t5-base")
    )

    docs = load_documents("data/sample.pdf")
    embeddings = get_embeddings()
    vector_store = create_vector_store(docs, embeddings)

    planner = planner_agent(llm)
    plan = planner.run(query)

    context = ""
    for sub_q in plan.split("\n"):
        context += research_agent(sub_q, vector_store)

    synthesizer = synthesis_agent(llm)
    answer = synthesizer.run(context)

    st.write(answer)
