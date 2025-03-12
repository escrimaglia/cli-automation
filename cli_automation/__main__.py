from pathlib import Path
from .main import app

app(prog_name="cla")

index_html = Path("index.html")
if not index_html.exists():
    cla_html = Path("cla.html") 
    if cla_html.exists():
        data = cla_html.read_text()
        index_html.write_text(data)

