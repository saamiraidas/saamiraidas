import streamlit as st 
from supabase import create_client,Client
from dotenv import load_dotenv
import os

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client =create_client(url,key)

def get_todos():
    respose = supabase.table('todos').select('*').execute()
    return respose.data


def data_todo(task):
    supabase.table('todo').insert({'task' : task}).execute()
    
    
st.title("Supabase Todo App") 

task = st.text_input("Add a new task:")   
if st.button("Add task"):
    if task:
        add_todo(task)
        st.success("Task added!")
    else:
        st.error("Plaese enter a task.") 
        
st.write("### Todo List:")
todos = get_todos()
if todos:
    for todo in todos:
        st.write(f"-{todo['task']}")
        
        
else:
    st.write("No task available.")                   