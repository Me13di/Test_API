import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import PhotoImage

import base64
import requests
import fitz  # PyMuPDF
import os 
from dotenv import load_dotenv

load_dotenv()

class ChatInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface OpenAI")

        # Variables d'instance
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.message_history = [{"role": "system", "content": "L'intégralité de la conversation doit être en français ,ton objectif est d'être un assistant juridique "}]
        self.assistant_message = ""
        self.image_path = ""
        self.pdf_path = ""
        self.texte = ""

        # Configuration de l'interface utilisateur
        self.setup_ui()

    def setup_ui(self):
        tk.Button(self.root, text="Select PDF", command=self.select_pdf).pack()
        self.pdf_label = tk.Label(self.root, text="No PDF Selected")
        self.pdf_label.pack()

        tk.Button(self.root, text="Image", command=self.select_image).pack()
        self.image_label = tk.Label(self.root, text="image pas selectionné")
        self.image_label.pack()

        tk.Label(self.root, text="Enter Your Prompt:").pack()
        self.prompt_entry = tk.Text(self.root, height=2, width=80)
        self.prompt_entry.pack()

        tk.Button(self.root, text="Send Request", command=self.send_request).pack()
        self.response_text = tk.Text(self.root, height=35, width=100)
        self.response_text.pack()

        

        
    def select_image(self):
        self.image_path = filedialog.askopenfilename()
        self.image_label.config(text=f"Selected Image: {self.image_path}")

    def select_pdf(self):
        self.pdf_path = filedialog.askopenfilename()
        self.pdf_label.config(text=f"Selected PDF: {self.pdf_path}")
        self.texte = self.convert_pdf_to_images(self.pdf_path)

    def send_request(self):
        user_prompt = self.prompt_entry.get("1.0", tk.END).strip()
        self.prompt_entry.delete("1.0", tk.END)

        if not user_prompt:
            return  # Ne rien faire si le prompt est vide

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        user_message = {"role": "user", "content": user_prompt}
        self.message_history.append(user_message)
        print(self.message_history)
        self.message_history.append({"role": "assistant", "content": self.texte})
        print(self.message_history)
        if self.image_path:
            model="gpt-4-vision-preview"
        else:
            model="gpt-4-0613"
        print(model)
        payload = {"model": model, "messages": self.message_history.copy(), "max_tokens": 100}

        if self.image_path:
            base64_image = self.encode_image(self.image_path)
            user_message["content"] = [{"type": "text", "text": user_prompt},
                                       {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_json = response.json()
        new_response = response_json["choices"][0].get("message", {}).get("content", "")

        self.assistant_message += "\nVous: " + user_prompt + "\nAssistant: " + new_response
        self.response_text.configure(state=tk.NORMAL)
        self.response_text.insert(tk.END, "\nVous: " + user_prompt + "\nAssistant: " + new_response)
        self.response_text.configure(state=tk.DISABLED)
        self.message_history.append({"role": "assistant", "content": new_response})

        self.image_path = ""
        self.image_label.config(text="No Image Selected")

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def convert_pdf_to_images(self, pdf_path):
        document = fitz.open(pdf_path)
        texte = ""
        for page in document:
            texte += page.get_text()
        return texte
# Utilisation de la classe
root = tk.Tk()
root.tk.call('source', 'azure.tcl')
root.tk.call('set_theme', 'dark')  
app = ChatInterface(root)
root.mainloop()