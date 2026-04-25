import requests
import time
from datetime import datetime
import schedule
import threading

TOKEN = '8598325234:AAF45kz5_amxH53l3BTxYaQn4PVHTG22yb0'
API_FOOTBALL_KEY = 'SUA_CHAVE_AQUI'
URL = f'https://api.telegram.org/bot{TOKEN}'

def enviar_mensagem(chat_id, texto):
    requests.post(f'{URL}/sendMessage', data={'chat_id': chat_id, 'text': texto, 'parse_mode': 'HTML'})

def buscar_jogos_over_reais():
    hoje = datetime.now().strftime('%Y-%m-%d')
    headers = {'x-apisports-key': API_FOOTBALL_KEY}
    try:
        url = f'https://v3.football.api-sports.io/fixtures?date={hoje}&league=71-72-39-140-135'
        jogos = requests.get(url, headers=headers).json()['response']
        sinais = []
        for jogo in jogos[:10]:
            casa_id = jogo['teams']['home']['id']
            casa_nome = jogo['teams']['home']['name']
            fora_nome = jogo['teams']['away']['name']
            hora = jogo['fixture']['date'][11:16]
            stats_casa = requests.get(f'https://v3.football.api-sports.io/teams/statistics?team={casa_id}&league={jogo["league"]["id"]}&season=2024', headers=headers).json()['response']
            gols_casa = float(stats_casa['goals']['for']['average']['total'])
            gols_sofridos_casa = float(stats_casa['goals']['against']['average']['total'])
            media_total = gols_casa + gols_sofridos_casa
            if media_total >= 2.8:
                chance = min(95, int(media_total * 28))
                sinais.append(f"\n⚽ <b>{hora} | {casa_nome} x {fora_nome}</b>\n📊 Média: {media_total:.1f} gols/jogo\n📈 Chance Over: {chance}%\n💰 <b>ENTRADA RECOMENDADA</b>\n")
        if not sinais: return "❌ <b>NENHUM SINAL HOJE</b>\n<i>Filtro anti-red ativado.</i>"
        return "\n".join(sinais[:3])
    except: return "Erro na API. Coloca sua chave da API-Football depois."

def enviar_sinal_automatico():
    print("Enviando sinal das 10h...")

schedule.every().day.at("10:00").do(enviar_sinal_automatico)
threading.Thread(target=lambda: [schedule.run_pending() or time.sleep(60) for _ in iter(int, 1)]).start()

offset = 0
print("✅ BOT WANDERSON OVER TIPS ONLINE - NÍVEL 3!")
while True:
    try:
        updates = requests.get(f'{URL}/getUpdates', params={'offset': offset, 'timeout': 30}).json()
        for update in updates['result']:
            offset = update['update_id'] + 1
            msg = update.get('message')
            if not msg or 'text' not in msg: continue
            chat_id, texto, nome = msg['chat']['id'], msg['text'], msg['from']['first_name']
            if texto == '/start': enviar_mensagem(chat_id, f"⚽ <b>Wanderson Over Tips 5.0 NÍVEL 3</b> ⚽\n\nBot 24h + Agendamento 10h!\n\n/over - Sinal manual")
            elif texto == '/over': 
                enviar_mensagem(chat_id, "🎯 <b>ANALISANDO COM STATS REAIS...</b>")
                enviar_mensagem(chat_id, f"🔥 <b>SINAIS PREMIUM</b> 🔥\n{buscar_jogos_over_reais()}\n\n<i>Protege a banca, {nome}! 💚</i>")
    except: time.sleep(5)