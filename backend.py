import sys
sys.path.append('/home/otzpt/Documentos/tinyllm2')
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import tiktoken
from model import GPT
from search_index import search

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

def generate_response(prompt):
    # searchs for relevant passages
    enc = tiktoken.get_encoding("gpt2")
    # builds the prompt
    results = search(prompt, k = 3)
    context = "\n\n".join([r.text for r in results])
    full_prompt = f"{context}\n\nQuestion: {prompt}\nAnswer: "
    # generates tokens same loop as chat.py
    ids = enc.encode(full_prompt)
    ids = ids[-256:]
    ids_tensor = torch.tensor([ids], device = device)

    for _ in range(100):
        with torch.no_grad():
            logits = model(ids_tensor[:, -256:])
        # decodes and returns answer(text)
        last_logits = logits[:, -1, :]
        probs = torch.softmax(last_logits, dim = -1)
        next_id = torch.multinomial(probs, num_samples = 1)
        ids_tensor = torch.cat([ids_tensor, next_id], dim = 1)
    # outputs decoded answer
    output_ids = ids_tensor[0].tolist()
    return enc.decode(output_ids)

@app.route('/chat', methods=['POST'])
def chat():
    # reads message
    message = request.json.get('message')
    response = generate_response(message) # calls generate response
    # returns output
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(port=5000)
