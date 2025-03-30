import streamlit as st
from langgraph.graph import END, StateGraph, START
from arxivagent import arxiv_search
from edges import route_question
from llmagent import llm_search
from wikiagent import wiki_search
from graphstate import GraphState
from pprint import pprint

# Initialize the workflow
workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("wiki_search", wiki_search)  # web search
workflow.add_node("arxiv_search", arxiv_search)  
workflow.add_node("llm_search", llm_search)

# Build graph
workflow.add_conditional_edges(
    START,
    route_question,
    {
        "wiki_search": "wiki_search",
        "arxiv_search": "arxiv_search",
        "llm_search": "llm_search",
    },
)
workflow.add_edge("arxiv_search", END)
workflow.add_edge("wiki_search", END)
workflow.add_edge("llm_search", END)

# Compile
app = workflow.compile()

# Streamlit UI
st.title("Research Query Assistant")

# User input
user_question = st.text_input("Enter your question:", "write 100 words about fis global")

if st.button("Submit"):
    if user_question:
        inputs = {
            "question": user_question
        }
        
        # Run the workflow
        output_text = ""
        for output in app.stream(inputs):
            for key, value in output.items():
                # Node
                st.write(f"Node '{key}':")
                # Optional: print full state at each node
                # st.write(value["keys"])
                
                # Collecting final output
                if "documents" in value:
                    output_text += value["documents"].page_content + "\n"
        
        # Display final output
        st.subheader("Output:")
        st.write(output_text)
    else:
        st.warning("Please enter a question.")
