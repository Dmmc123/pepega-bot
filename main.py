import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import os
from pymongo import MongoClient
from gpt_utils import AnswerGenerator

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global client
    # crate a db entry with 10 starting tokens
    n_start_tokens = 10
    # connect to collection
    col = client[os.environ["MONGO_INITDB_DATABASE"]][os.environ["db-collection"]]
    # check if person exists or not
    res = list(col.find({"username": update.message.from_user.username}))
    # user already has info
    if res:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"You already received your free tokens so no more free tokens for you lol\n\n"
            f"Btw you can check your /balance to see how many tokens you have left\n\n"
            f"Type /help for getting the format of question",
        )
    # no info about the user
    else:
        # create entry in collection
        col.insert_one(
            {"username": update.message.from_user.username, "tokens": n_start_tokens}
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Hello!\nYou have {n_start_tokens} tokens which you can use to ask me questions!",
        )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global client
    # connect to collection
    col = client[os.environ["MONGO_INITDB_DATABASE"]][os.environ["db-collection"]]
    # get info about user
    res = col.find({"username": update.message.from_user.username})
    tokens = list(res)[0]["tokens"]
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"You have {tokens} tokens left!"
    )


async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global client, answer_generator
    # log the input of user
    logging.log(level=logging.INFO, msg=" ".join(context.args))
    # connect to collection
    col = client[os.environ["MONGO_INITDB_DATABASE"]][os.environ["db-collection"]]
    # get info about user
    res = col.find({"username": update.message.from_user.username})
    entry = list(res)[0]
    # check if user can ask questions
    if entry["tokens"] == 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Sorry(\nYou ran out of tokens and you cannot ask questions anymore",
        )
    else:
        # get the input from command
        text = " ".join(context.args)
        if text.endswith("?"):
            # subtract one token and form response
            col.update_one(
                {"username": update.message.from_user.username},
                {"$inc": {"tokens": -1}},
            )
            # get user the balance
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Your balance is now {entry['tokens']-1}",
            )
            # query gpt-3 for answer
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=answer_generator(text)
            )
        else:
            # notify user about wrong input
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"What you asked is not a question. Place write your query as an example:\n\n"
                f"/question What hyperparameters does SVM have?",
            )


async def help_function(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="To ask the question type /question <YOUR QUESTION>. Example:\n\n /question What hyperparameters does SVM have?"
    )


def connect_init_db():
    # connect to main bot db
    client = MongoClient(
        f"mongodb://{os.environ['MONGO_INITDB_ROOT_USERNAME']}:{os.environ['MONGO_INITDB_ROOT_PASSWORD']}@db",
        27017,
    )
    db = client[os.environ["MONGO_INITDB_DATABASE"]]
    # create collection if needed
    if os.environ["db-collection"] not in db.list_collection_names():
        col = db[os.environ["db-collection"]]
        # make devs have many tokens
        col.insert_many(
            [
                {"username": "matsusha", "tokens": 1488},
                {"username": "Dmmc123", "tokens": 1337},
            ]
        )
        logging.log(
            level=logging.INFO, msg=f"Created collection {os.environ['db-collection']}!"
        )
    return client


if __name__ == "__main__":
    # connect to openai
    answer_generator = AnswerGenerator(completion_model="text-davinci-002")
    logging.log(level=logging.INFO, msg="Instantiated Answer Generator")

    # connect to mongo
    client = connect_init_db()
    logging.log(level=logging.INFO, msg="Successfully connected to MongoDB!")

    # initialize the bot app
    application = ApplicationBuilder().token(os.environ["bot-api-token"]).build()

    # make handlers
    start_handler = CommandHandler("start", start)
    balance_handler = CommandHandler("balance", balance)
    question_handler = CommandHandler("question", question)
    help_handler = CommandHandler('help', help_function)
    application.add_handler(start_handler)
    application.add_handler(balance_handler)
    application.add_handler(question_handler)
    application.add_handler(help_handler)

    # start accepting requests
    application.run_polling()
