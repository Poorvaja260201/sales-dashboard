import requests

def explain_results(question, df):

    data_str = df.to_string(index=False)

    prompt = f"""
    You are a senior business analyst.

    Question:
    {question}

    Data:
    {data_str}

    Give clear, data-backed insights.
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    response_json = response.json()
    return response_json.get('response', 'No response from model')
