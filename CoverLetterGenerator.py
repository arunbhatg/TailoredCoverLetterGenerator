import PyPDF2
import openai
import yaml
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

# Adding some CSS styles for improved appearance
app.layout = html.Div([
    html.H1("Cover Letter Generator", style={'text-align': 'center'}),
    dcc.Textarea(id='jd-input', placeholder='Enter JD here...', style={'width': '100%'}),
    html.Button('Generate Cover Letter', id='generate-button', n_clicks=0, style={'margin-top': '10px', 'width': '100%'}),
    html.Div(id='output-text', style={'margin-top': '20px', 'white-space': 'pre-wrap', 'font-family': 'Arial'})
])

def generate_cover_letter(JD=0):
    if type(JD)!=str:
        return 0
    def load_config(filename):
        with open(filename, 'r') as file:
            return yaml.safe_load(file)

    config = load_config("config.yaml")
    pdf_file = open(config['PDF_FILE_PATH'], "rb")
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    CV = ""

    for page in pdf_reader.pages:
        text = page.extract_text()
        CV += text

    pdf_file.close()
    

    # Replace placeholders with actual content
    initial_text = config["INITIAL_TEXT"]
    initial_text = initial_text.replace("JD", JD)
    initial_text = initial_text.replace("CV", CV)
    
    openai.api_key = config['OPENAI_KEY']

    message = [{"role": "user", "content": initial_text}]
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=message,
    temperature=0.1,
    max_tokens=1000,
    frequency_penalty=0.0
    )
 
    code = response["choices"][0]["message"]["content"]

    return code

@app.callback(
    Output('output-text', 'children'),
    [Input('generate-button', 'n_clicks')],
    [State('jd-input', 'value')]
)
def update_cover_letter(n_clicks, jd):
    if n_clicks > 0:
        code = generate_cover_letter(jd)
        return code
    else:
        return ""

if __name__ == "__main__":
    app.run_server(debug=True,port=8042)
