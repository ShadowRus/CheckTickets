from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from decouple import config
import socket




def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

HOST = config('HOST', default=extract_ip())
PORT = config('PORT', default=8091)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index_s2.html", {"request": request})

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    #uvicorn.run(app, host=HOST, port=443, log_level="debug", ssl_keyfile="./localhost+3-key.pem" , ssl_certfile="./localhost+3.pem")
    uvicorn.run(app, host=HOST, port=PORT, log_level="debug")