from typing import Annotated
from typing_extensions import TypedDict
import dotenv , os , getpass
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph , START, END
from langgraph.graph.message import add_messages
from IPython.display import Image, display
import requests

dotenv.load_dotenv(".env")

KEY = os.environ.get("GOOGLE_API_KEY")

if not KEY :
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Your API Key here :")

class State(TypedDict):
    answer : str
    data : list
    
graph = StateGraph(State)

def getdata(state: State) -> State:
    try:
        response = requests.get("https://jsonplaceholder.typicode.com/users/1")
        if  response.status_code==200:
            return {"data":[response.text]}
        else:
            print("Not Found")
    except Exception as e:
        print(e)
    
def chatbot(state: State)-> State:
    try:
        llm = init_chat_model(model = "gemini-2.5-flash",model_provider="google_genai")
        input_message = [HumanMessage(content=f"Summarize this data in human readable language , data is : {state["data"]}")]
        response = llm.invoke(input_message)
        print("Chatbot_response :",response.content)
        return {"answer":response.content}
    except Exception as e:
        print(e)

graph.add_node("getdata",getdata) 
graph.add_node("chatbot",chatbot) 

graph.add_edge(START,"getdata")
graph.add_edge("getdata","chatbot")
graph.add_edge("chatbot",END)

app = graph.compile()
for result in app.stream({}):
    print(result)
try:
    display(Image(app.get_graph().draw_mermaid_png()))
except Exception:
    pass

try:
    png_bytes = app.get_graph().draw_mermaid_png()

    with open("my_graph.png", "wb") as f:
        f.write(png_bytes)
except Exception:
    pass