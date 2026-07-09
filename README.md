# Manga Translator

A desktop app (built with [arcade](https://api.arcade.academy/)/pyglet) for browsing manga on MangaDex, downloading chapters, and automatically translating them using a local AI model through **Ollama**.

## Features

- Search and browse manga directly from MangaDex
- Download chapters to your machine
- Automatically translate downloaded chapters into a target language of your choice using a local LLM (`translategemma`) and PaddleOCR
- Simple, mouse-driven UI with scrollable manga lists and cover previews

## 1. Install Ollama (required before first use)

The translation feature depends entirely on Ollama running locally — **the app will not be able to translate anything until this step is done.**

1. Download and install Ollama for your OS from **https://ollama.com/download**
2. Pull the translation model used by this app:
   ```bash
   ollama pull translategemma:latest
   ```
3. Make sure the Ollama service is running (it usually starts automatically after installation, or you can start it manually):
   ```bash
   ollama serve
   ```

Leave Ollama running in the background whenever you want to use the translation feature — the app sends translation requests to it locally.

## 2. Install Python dependencies

```bash
pip install -r requirements.txt
```


## 3. Run the app

```bash
python main.py
```

---

Once Ollama is installed and the `translategemma` model is pulled, everything else is handled inside the app — just download a manga and hit **Translate**.