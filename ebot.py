import discord
from discord.ext import commands, tasks
import os
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from selenium.webdriver.common.by import By
import requests

import asyncio
import time
from concurrent.futures.thread import ThreadPoolExecutor
from selenium.webdriver.chrome.options import Options

from selenium import webdriver


headersdashjson = {
    'Authorization': f'Bot Token',
    'Content-Type': 'application/json',
}

class EBot(commands.Bot):
    def __init__(self):
        super().__init__(
            intents = discord.Intents().all(),
            command_prefix="e+",
            help_command=None,
        )
        self.async_db = AsyncIOMotorClient('mongodb://localhost:27017/')
        self.sync_db = MongoClient('mongodb://localhost:27017')

bot = EBot()

@bot.hybrid_command(name = "login", with_app_command = True, description = "ログインします")
@commands.cooldown(1, 10, type=commands.BucketType.user)
async def login(ctx, 学校コード: str, id: str, パスワード: str):
    def Run():
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options = options)
        driver.get('https://ela.education.ne.jp/students')
        driver.implicitly_wait(10)
        driver.find_element(By.NAME,"school_code").send_keys(学校コード)
        driver.find_element(By.NAME,"login_id").send_keys(id)
        driver.find_element(By.NAME, "password").send_keys(パスワード)
        driver.find_element(By.ID,"login").click()
        driver.get('https://ela.education.ne.jp/students/home/infoes')
        driver.implicitly_wait(10)
        name = driver.find_element(By.NAME, "user-name").get_attribute('value')
        sequence = driver.find_element(By.NAME, "sequence").get_attribute('value')
        jsonda = {
            'content': f'「{name}」さんにログインしました。\n出席番号: {sequence}'
        }
        js = requests.post(f"https://discordapp.com/api/channels/{ctx.channel.id}/messages", headers=headersdashjson, json=jsonda).json()
        driver.quit()
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, Run)
    await ctx.reply("ログイン完了。")

@bot.hybrid_command(name = "drill-clear", with_app_command = True, description = "ドリルをクリアします。")
@commands.cooldown(1, 10, type=commands.BucketType.user)
async def drill_clear(ctx, 学校コード: str, id: str, パスワード: str, ドリルurl: str):
    def Run():
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options = options)
        driver.get('https://ela.education.ne.jp/students')
        driver.implicitly_wait(10)
        driver.find_element(By.NAME,"school_code").send_keys(学校コード)
        driver.find_element(By.NAME,"login_id").send_keys(id)
        driver.find_element(By.NAME, "password").send_keys(パスワード)
        driver.find_element(By.ID,"login").click()
        driver.get(ドリルurl)
        driver.implicitly_wait(10)
        while True:
            try:
                an = driver.execute_script("""javascript:
        for (var group_id in drill.question.answer_groups) {
            group_id = Number(group_id)
            var max_score_weight = 0
            for (p = 0; p < drill.question.answer_groups[group_id].patterns.length; p++) {
                max_score_weight = Math.max(max_score_weight, drill.question.answer_groups[group_id].patterns[p].score_weight)
            }


            for (var p= 0; p < drill.question.answer_groups[group_id].patterns.length; p++) {                // パターン loop
                if (drill.question.answer_groups[group_id].patterns[p].score_weight >= max_score_weight) {   // 最高得点(つまり正解)？
                        for (var answer_id in drill.question.answer_groups[group_id].patterns[p].answer_ids) {
                            answer_id = Number(answer_id)

                            var answer_value = drill.question.answer_groups[group_id].patterns[p].answer_ids[answer_id]
                            return answer_value
                        }
                }
            }
        }
        """)
                driver.execute_script(f"drill.click('questionanswer-01-{an}');")
                an = driver.execute_script("""javascript:drill.onJudge()""")
                driver.execute_script("""javascript:drill.onJudge()""")
            except:
                jsonda = {
                    'content': f'クリア完了'
                }
                js = requests.post(f"https://discordapp.com/api/channels/{ctx.channel.id}/messages", headers=headersdashjson, json=jsonda).json()
                driver.quit()
					 return
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, Run)

bot.run("Token")