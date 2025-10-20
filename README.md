### Work In PROGRESS. Don't Use IT ###

# Lemonade Conversation for Home Assistant

![Lemonade Conversation Logo](https://raw.githubusercontent.com/pchdomotichome/lemonade_conversation_ha/main/images/logo.svg)

**Bring your own local, private, and powerful voice assistant to Home Assistant.**

This custom integration connects Home Assistant's conversation engine to a self-hosted [Lemonade Server](https://lemonade-server.ai/), allowing you to use powerful local Large Language Models (LLMs) as a fully-featured voice and chat assistant.

---

## Features

- **Private by Design:** All processing is done locally on your Lemonade Server. No data ever leaves your network.
- **Dynamic Model Selection:** Automatically fetches and lets you choose from the models available on your Lemonade Server.
- **Conversation History:** The assistant remembers the last few turns of the conversation for contextual follow-up questions.
- **Customizable Personality:** Use a "System Prompt" to give your assistant a unique personality, from a helpful butler to a sarcastic pirate.
- **Tool Use (Coming Soon!):** Future updates will enable the assistant to control your Home Assistant devices directly.

## Installation

The easiest way to install this integration is through the [Home Assistant Community Store (HACS)](https://hacs.xyz/).

1.  **Add Custom Repository:**
    - Go to HACS > Integrations.
    - Click the three dots in the top right corner and select "Custom repositories".
    - In the "Repository" field, enter: `https://github.com/pchdomotichome/lemonade_conversation_ha`
    - In the "Category" dropdown, select "Integration".
    - Click "ADD".
2.  **Install the Integration:**
    - Search for "Lemonade Conversation" in HACS.
    - Click "Install".
3.  **Restart Home Assistant.**

*Manual installation: Copy the `custom_components/lemonade_conversation` folder to a `custom_components` folder in your Home Assistant configuration directory.*

## Configuration

1.  Go to **Settings > Devices & Services**.
2.  Click **+ ADD INTEGRATION** and search for "Lemonade Conversation".
3.  **Step 1: Connection**
    - **Base URL:** Enter the full URL of your Lemonade Server (e.g., `http://192.168.1.100:8000`).
    - **API Key (Optional):** Enter your API key if your server requires one.
4.  **Step 2: Model Selection**
    - Choose a language model from the dropdown. These are fetched live from your server.
5.  Click **Submit**.

Once installed, you can further customize the assistant by clicking **CONFIGURE** on the integration card. This will allow you to change the model and set a custom personality via the **System Prompt**.

## Creating a Voice Assistant

1.  Go to **Settings > Voice assistants**.
2.  Click **+ ADD ASSISTANT**.
3.  Give it a name (e.g., "Lemonade").
4.  In the "Conversation agent" dropdown, select **"Lemonade Assistant"**.
5.  Set your preferred Speech-to-Text (STT) and Text-to-Speech (TTS) engines.
6.  Click **Create**.

You can now talk to your new private assistant!

## Roadmap

This project is under active development. Here's what's coming next:
- **Phase 2:** Advanced model parameter tuning (temperature, top_k, etc.).
- **Phase 3:** Configurable response streaming for text chat.
- **Phase 4:** In-Context Learning (ICL) cache to speed up common queries.
- **Phase 5:** Full device control via LLM Tool Use.

---

*This integration was expertly guided and co-developed with an advanced AI programming assistant.*
