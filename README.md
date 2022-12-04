# PEPEGA
Prompt Engineering with Paragraph Embeddings for Generating Answers (PEPEGA)

## Description

This a code for launching Telegram bot which is capable of answering ML-related questions through GPT-3 based service

## Examples 

![image](https://user-images.githubusercontent.com/54360024/205514358-ccffc147-d99d-4b9b-8719-317eaf39b4f3.png)

## How to use

The bot is publicly available at https://t.me/PepegaAIBot

### Custom Telegram bot

If you want to use adopt on your own bot, follow the next steps:

1. Clone the repo
2. Create `.env` file with the following fields:
    * `db_login` - login for admin in MongoDB
    * `db_pass`- password for admin in MongoDB
    * `db_name`- name for root database in MongoDB
    * `bot_api_token` - Telegram bot API token
    * `openai_api_token` - OpenAI api token
3. Run the bot service using `docker-compose up`

### Custom data

For now, the embedded paragraphs consist of ~200 articles about classical ML and a bit of DL. If you want to query PEPEGA on your custom data, do the following:

1. Replace `paragraphs.json` with your custom list of paragraphs which are gonna act as context for GPT-3 prompt
2. Use previously built `paragraphs.json` file to build [pynndescent](https://github.com/lmcinnes/pynndescent) index with cosine distance, pickle it, and replace with current `index.pkl` file


