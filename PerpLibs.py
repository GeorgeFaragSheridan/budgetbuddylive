from dotenv import load_dotenv
import requests
import os
import logging

load_dotenv()

def Request(query):
    '''
    takes in a request as a string, outputs full JSON
    '''
    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise."
            },
            {
                "role": "user",
                "content": f"{query}"
            }
        ],
        "max_tokens": 2048,
        "temperature": 0.2,
        "top_p": 0.9,
        "return_images": False,
        "return_related_questions": False,
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1,
        "web_search_options": {"search_context_size": "high"}
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers).json()

    #see docs for parsing usage
    return(response)
    
def AnalyzeData(Datatype, context ,raw):

    '''
    Asks perplexity to analyze a certain input datatype (eg. csv) for a context (eg. abnormal datapoints)
    and then takes in the raw data as a third argument. Returns the full json file
    '''
    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise."
            },
            {
                "role": "user",
                "content": f"analyze the following data as if it had the datatype{Datatype}. \
                    analyze it in the context of, surrounding or with the goal to {context}\
                        only analyze the data after the semicolon ; {raw}"
            }
        ],
        "max_tokens": 123,
        "temperature": 0.2,
        "top_p": 0.9,
        "return_images": False,
        "return_related_questions": False,
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1,
        "web_search_options": {"search_context_size": "high"}
    }
    headers = {
        "Authorization": f"Bearer {os.getenv("PERPLEXITY_API_KEY")}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers).json()

    #see docs for parsing usage
    return(response)

def Textonly(json):
    '''
    converts the json to to just the raw text output
    '''
    return json["choices"][0]["message"]["content"]

def TextAndRefs(json):
    '''
    Returns 2 objects, the first being the list of references and the second being the raw output
    '''

    return json["citations"],json["choices"][0]["message"]["content"]