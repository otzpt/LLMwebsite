import sys
sys.path.append('/home/otzpt/Documentos/tinyllm2')
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import tiktoken
from model import GPT
from search_index import search

# if anyone decides to maintain this code
# good luck with that it is hard to read
# or maybe its a skill issue its my first time
# doing something like this

app = Flask(__name__)
CORS(app)
# loads the model
def load_model():
    # creates GPT and loads model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = GPT(d_model = 768, n_heads = 12, n_layer = 12, vocab_size = 50257, block_size = 256)
    model = model.to(device)

    #loads the checkpoint
    checkpoint = torch.load('/home/otzpt/Documentos/tinyllm2/checkpoints/976000.pt', map_location = device)
    state_dict = checkpoint['model']
    state_dict = {k.replace('_orig_mod.', ''): v for k, v in state_dict.items()}
    model.load_state_dict(state_dict)
    model.eval()

    #returns the values
    return model, device

model, device = load_model()  # runs once when server starts

BLOCK_SIZE = 256
MAX_NEW_TOKENS = 60

def generate_response(prompt):
    # searchs for relevant passages
    enc = tiktoken.get_encoding("gpt2")

    # builds the prompt
    results = search(prompt, k = 3)
    context = "\n\n".join([r.text for r in results])
    full_prompt = f"{context}\n\nQuestion: {prompt}\nAnswer: "

    # generates tokens same loop as chat.py, now with kv_cache
    # leave room for MAX_NEW_TOKENS: positions only grow with a cache, no
    # more sliding the window each step
    ids = enc.encode(full_prompt)[-(BLOCK_SIZE - MAX_NEW_TOKENS):]
    ids_tensor = torch.tensor([ids], device = device)
    prompt_len = len(ids) # stores how many tokens origin promt was/is

    with torch.no_grad():
        logits, kv_cache = model(ids_tensor)  # prefill: whole prompt at once
        for _ in range(MAX_NEW_TOKENS):
            # decodes and returns answer(text)
            last_logits = logits[:, -1, :]
            probs = torch.softmax(last_logits, dim = -1)
            next_id = torch.multinomial(probs, num_samples = 1)
            ids_tensor = torch.cat([ids_tensor, next_id], dim = 1)
            logits, kv_cache = model(next_id, kv_cache)  # decode: just the new token
    # formating
    # this should fix the answer being more than 100 words of encoding
    # and decoding
    generated_ids = ids_tensor[0][prompt_len:].tolist()  # only new tokens
    answer = enc.decode(generated_ids).strip()

    #cuts last phrase completly if there is a '.'
    last_period = answer.rfind('.')
    if last_period != -1:
        answer = answer[:last_period + 1]

    return answer

@app.route('/chat', methods=['POST'])
def chat():
    # reads message
    message = request.json.get('message')
    response = generate_response(message) # calls generate response
    # returns output
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(port=5000)
