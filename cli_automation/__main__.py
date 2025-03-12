from pathlib import Path
from .main import app
app(prog_name="cla")

cla_html = Path("cla.html") 
if cla_html.exists():
    data = cla_html.read_text()
    index_html = Path("index.html")
    index_html.write_text(data)

