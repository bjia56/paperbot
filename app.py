import asyncio
import os

import arxiv
import discord

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


query = '("LLM agent" OR "language model agent" OR "autonomous agent" OR "AI agent" ' \
        'OR "prompt engineering" OR "chain-of-thought" OR "CoT" ' \
        'OR "few-shot prompting" OR "tool use" OR "function calling" ' \
        'OR "retrieval-augmented generation" OR "RAG" OR "API call" ' \
        'OR "planning with LLMs") AND (cat:cs.CL OR cat:cs.AI)'


def fetch_latest_papers():
    search = arxiv.Search(
        query=query,
        max_results=5,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    client = arxiv.Client()
    papers = []
    for paper in client.results(search):
        papers.append({
            "title": paper.title,
            "authors": ", ".join([a.name for a in paper.authors]),
            "abstract": summarize(paper.summary),
            "url": paper.entry_id
        })

    return papers


def summarize(string, num_sentence=3):
    lang = 'english'
    tknz = Tokenizer(lang)
    stemmer = Stemmer(lang)
    summarizer = Summarizer(stemmer)
    parser = PlaintextParser(string, tknz)
    parser.stop_word = get_stop_words(lang)
    summ_string = ''
    for sentence in summarizer(parser.document, num_sentence):
        summ_string += str(sentence) + ' '
    return summ_string


TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)


async def send_to_discord(papers):
    channel = client.get_channel(CHANNEL_ID)
    for paper in papers:
        msg = f"📖 **{paper['title']}**\n👨‍🔬 *{paper['authors']}*\n📜 {paper['abstract']}\n🔗 [Read more]({paper['url']})"
        await channel.send(msg)


@client.event
async def on_ready():
    print(f"Bot is ready! Logged in as {client.user}")
    seen_papers = set()
    while True:
        print("Checking for new papers...")
        papers = fetch_latest_papers()
        papers = [paper for paper in papers if paper['url'] not in seen_papers]
        seen_papers.update([paper['url'] for paper in papers])
        print(f"Found {len(papers)} new papers")
        if papers:
            await send_to_discord(papers)
        print("Sleeping...")
        await asyncio.sleep(43200)


client.run(TOKEN)