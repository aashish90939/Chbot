import streamlit as st
import os
import openai
import chromadb
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from chromadb import EmbeddingFunction

# Load environment variables
load_dotenv()

    
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = "sk-UDiNH2rFuDEm-D18WWXxjObrWjzKkkYjc8MfYs28M-T3BlbkFJU8fXRAZdsJxG_oatkALud45atUwZ6VV1ig8hxxrrEA"

DB_PATH = os.environ.get("DB_PATH", os.path.abspath(os.path.join(os.getcwd(), "../data/database/chromadb")))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "Hsrw_database")

# Streamlit Page Configuration
st.set_page_config(page_title="University Web-Assistant", page_icon="📘", layout="wide")
# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Custom Embedding Function Using OpenAI
class MyEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self.model = "text-embedding-3-small"  

    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            response = openai.Embedding.create(
                model=self.model,
                input=text
            )
            embedding = response['data'][0]['embedding']
            embeddings.append(embedding)
        return embeddings

    def embed_query(self, query):
        response = openai.Embedding.create(
            model=self.model,
            input=query
        )
        embedding = response['data'][0]['embedding']
        return embedding

embedding_function = MyEmbeddingFunction()

# Set up Persistent Client for ChromaDB
persistent_client = chromadb.PersistentClient(path=DB_PATH)
collection = persistent_client.get_or_create_collection(COLLECTION_NAME)

# Database Embedding Setup
embedding_dimension = 1536  # text-embedding-3-small :1536 

db = Chroma(
    client=persistent_client,
    collection_name=COLLECTION_NAME,
    embedding_function=MyEmbeddingFunction(),
    collection_metadata={"hnsw:space": "cosine", "dimension": embedding_dimension}
)


    

def retrieve_and_answer(question):
    # Retrieve relevant documents using semantic search from ChromaDB
    docs = db.as_retriever(search_kwargs={"k": 2}).get_relevant_documents(question)

    # Build a structured context with each document's content and link
    context = ""
    for i, doc in enumerate(docs):
        link = doc.metadata.get('link', None)  # Extract the link from metadata
        cleaned_link = link.replace('wled-processed/', '')
        context += f"Extracted Documents {i+1}:\n{doc.page_content}\n[Source](<{cleaned_link}>)\n\n"
    
    #feed history to next query
    recent_conversations = []
    for exchange in st.session_state['chat_history'][-5:]:
        recent_conversations.append({"role": "user", "content": exchange["user"]})
        recent_conversations.append({"role": "assistant", "content": exchange["assistant"]})
    print(10*"--")   
    print(recent_conversations)
    print(10*"--")

    # role setup and prompt engineering
    messages = [
    {
        "role": "system",
        "content": (
            "You are a highly knowledgeable assistant focused on providing precise answers about university information  "
            "Base your responses strictly on the provided content, using only sources that contain relevant information.\n\n"
            "consider the chat history (recent_conversations) only to know which questions were asked and which answers were given to it , you have to answer only the current question considering the history"
            
            "Instructions:\n\n"
            
            "1. *Direct and Relevant Answers*: Answer the user's question with relevant, concise, and accurate details. "
            "Avoid using terms like 'source,' 'context,' or 'database.' Instead, simply present the answer.\n\n"
            
            "2. *Full Link Display*: At the end of your response, display full URLs without hiding them behind text (e.g., 'Source 1'). "
            "List each link only once, even if multiple documents have the answer.\n\n"
            
            "3. *Clickable Links*: Ensure URLs are clickable and directly reference the relevant document. Example format: "
            "'www.example.com/document1' or 'https://university-website.com/guide.pdf'.\n\n"
            
            "4. *Avoid Repetition*: If multiple documents contain the same answer, provide the information only once and list each unique link just once at the end.\n\n"
            
            "5. *Answer Formatting*: Avoid referencing 'documents' or 'contexts.' Provide straightforward answers and, if relevant links are found, display them at the end in a format like this:\n\n"
            "'Related links:\nhttps://university-website.com/info1\nhttps://university-website.com/info2'\n\n"
            
            "6. *No Answer Available*: If none of the documents contain the answer, respond with a message indicating that the information is not available in this dataset."
            
            #"7. *Basic Greetings and Manners* If there are some greetins as a user query please reply in good manner"
        )
    },
    *recent_conversations,  # Add recent conversation history into the messages list
    {
        "role": "user",
        "content": f"Answer the question based on the context provided. The question is:\n\n<question>{question}</question>\n\nThe contexts are:\n\n{context} and keep in mind the past history "
    }
]
    print(10*"**")   
    print(messages)
    print(10*"**")
    # Generate the chat completion using OpenAI with the structured message
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        #model="gpt-4-turbo",  # Specify the OpenAI model
        messages=messages,
        max_tokens=500,
        temperature=0.2,
        top_p=0.95
        
    )

    # Extract and return the answer with document references
    answer = response['choices'][0]['message']['content']
    return answer

import streamlit as st

# List of predefined questions
questions = [
    "How can I contact Professor Zimmer?",
    "How can I apply for a scholarship?",
    "What are the campus facilities?",
    "How do I contact the admissions office?",
     "What are the requirements for applying to a master's in information engineering?",

    
]

# Sidebar with a unified HTML structure for questions
with st.sidebar:
    st.image("../assets/image1.svg", width=200)
    st.markdown("""
    <div style='text-align: center;'>
        <h1>Uni Web-Assistant</h1>
        <p>Ask me about university services, events, and more!</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📌 Popular Questions")

    # Unified HTML for displaying questions
    st.markdown("<ol>", unsafe_allow_html=True)
    for i, question in enumerate(questions, 1):
        st.markdown(f"<li>{question}</li>", unsafe_allow_html=True)
    st.markdown("</ol>", unsafe_allow_html=True)

    # Dropdown to select a question
    selected_question = st.selectbox("Choose a question:", [""] + questions)

    # Submit button for the selected question
    if st.button("Submit Query"):
        if selected_question:
            user_input = selected_question
            response = retrieve_and_answer(user_input)
            st.session_state['chat_history'].append({
                "user": user_input,
                "assistant": response,
            })
        else:
            st.warning("Please select a question before submitting.")

    # Help Section
    with st.expander("❓ Help"):
        st.markdown("""
        - **Type your question** in the chat box below.
        - You can ask about **university events, facilities, schedules**, and more!
        - Use the dropdown to select a predefined question.
        """)
    st.markdown("<hr>", unsafe_allow_html=True)

# Main Chat Input and Persistent Chat Display
st.markdown("""
<div style='text-align: center;'>
    <h2>Welcome to the University Web-Assistant!</h2>
    <p>Remember, this chatbot can occasionally make mistakes, so make sure to verify information by visiting the official website.</p>
</div>
""", unsafe_allow_html=True)

# Capture user input
user_input = st.chat_input("How can I assist you today?")
if user_input:
    with st.spinner("Processing your query..."):
        response = retrieve_and_answer(user_input)

        # Store the user input and the assistant response in session state
        st.session_state['chat_history'].append({
            "user": user_input,
            "assistant": response,
        })

# Display chat history
if 'chat_history' in st.session_state:
    user_image = "../assets/user.png"
    assistant_image = "../assets/ai.png"
    
    for i, message in enumerate(st.session_state['chat_history']):
        # Display user message with aligned icon and text
        user_col, user_msg_col = st.columns([0.02, 0.92])
        with user_col:
            st.image(user_image, width=24)
        with user_msg_col:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; background-color: rgb(255, 255, 255); padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                    <span>{message['user']}</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

        # Display assistant message with aligned icon and text
        assistant_col, assistant_msg_col = st.columns([0.02, 0.92])
        with assistant_col:
            st.image(assistant_image, width=24)
        with assistant_msg_col:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; background-color: #cddee4; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                    <span>{message['assistant']}</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

# Add CSS for Improved Design
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #f0f2f6;
        color: #333;
        border: none;
        padding: 10px;
        border-radius: 5px;
        margin-top: 5px;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #badbe3;
        color:#333;
    }
    .st-chat-message {
        background: #eef2f7;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)
