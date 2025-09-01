# Projeto-LegendaryPost

from telethon import TelegramClient, events, Button
import json
import os

# === Configurações ===

api_id = 7981034987
api_hash = 'f33777d7b5da3287c98f49bb543f710f'
bot_token = '7651405515:AAFPOhBwCUCnLoTrc8VuCm3dQz6TQ5L1Gmk'
OWNER_ID = '7981034987'

ADMINS_FILE = 'admins.json'
CONFIG_FILE = 'config.json'
ESTILO_FILE = 'estilo.json'
PERMISSOES_FILE = 'permissoes.json'

bot = TelegramClient('legendarypost', api_id, api_hash).start(bot_token=bot_token)

def load_json(file, default):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

admins = load_json(ADMINS_FILE, [OWNER_ID])
admins = list(set(admins))
save_json(ADMINS_FILE, admins)

config = load_json(CONFIG_FILE, {})
estilo = load_json(ESTILO_FILE, {})
permissoes = load_json(PERMISSOES_FILE, {
    "texto": True,
    "audio": True,
    "video": True,
    "foto": True,
    "sticker": True,
    "gif": True
})

state = {}

def gerar_botoes_permissoes():
    return [
        [Button.text("Mensagens de Texto:"), Button.text("❤️ ON | texto"), Button.text("💚 OFF | texto")],
        [Button.text("Áudio:"), Button.text("❤️ ON | audio"), Button.text("💚 OFF | audio")],
        [Button.text("Vídeos:"), Button.text("❤️ ON | video"), Button.text("💚 OFF | video")],
        [Button.text("GIFs:"), Button.text("❤️ ON | gif"), Button.text("💚 OFF | gif")],
        [Button.text("Stickers:"), Button.text("❤️ ON | sticker"), Button.text("💚 OFF | sticker")],
        [Button.text("Imagens:"), Button.text("❤️ ON | foto"), Button.text("💚 OFF | foto")],
        [Button.text("⬅️ Voltar ao menu principal")]
    ]

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = str(event.sender_id)
    if user_id in admins:
        buttons = [
            [Button.text("➕ Enviar Novo POST")],
            [Button.text("📋 Gerenciar Canais")],
            [Button.text("🎨 Estilo de Post")],
            [Button.text("🛠️ Painel ADM")],
            [Button.text("🔒 Permissões de Botões")],
            [Button.text("💬 Suporte")]
        ]
        await event.respond("✅ Menu principal\nEscolha uma opção:", buttons=buttons)
    else:
        await event.respond(
            "🌸 Bot Oficial de Legendas Automáticas\n"
            "📢 Para Canais do Telegram\n"
            "✨ Criado por @ContaMod_Gerenciador\n\n"
            "🚫 Você não está autorizado(a) a usar este bot.\n"
            "💌 Para solicitar acesso, entre em contato com o DEV.",
            buttons=[[Button.text("💬 Suporte")]]
        )

@bot.on(events.NewMessage())
async def mensagens(event):
    user_id = str(event.sender_id)
    text = event.raw_text.strip()

    if text == "⬅️ Voltar ao menu principal":
        if user_id in state:
            del state[user_id]
        await start(event)
        return

    if text == "💬 Suporte":
        await event.reply("💬 *Suporte*\nFale com: @ContaMod_Gerenciador")
        return

    if user_id not in admins:
        return

    if text == "➕ Enviar Novo POST":
        state[user_id] = {"step": "canal_id"}
        await event.reply("📌 Envie o *ID do canal* (começando com -100):", buttons=[[Button.text("⬅️ Voltar ao menu principal")]])

    elif text == "🔒 Permissões de Botões":
        state[user_id] = {"step": "permissoes"}
        await event.reply("🔒 *Permissões de Botões*\nEscolha ON ou OFF para cada tipo de mídia:", buttons=gerar_botoes_permissoes())

    elif text == "📋 Gerenciar Canais":
        if not config:
            await event.reply("⚠️ Nenhum canal configurado.")
            return

        buttons = []
        for cid in config.keys():
            try:
                chat = await bot.get_entity(int(cid))
                nome = f"@{chat.username}" if chat.username else chat.title
                label = f"{cid} - {nome}"
                buttons.append([Button.text(label)])
            except:
                buttons.append([Button.text(f"{cid} - (Canal desconhecido)")])

        buttons.append([Button.text("⬅️ Voltar ao menu principal")])
        await event.reply("📋 *Canais configurados:*", buttons=buttons)
        state[user_id] = {"step": "gerenciar"}

    elif text == "🎨 Estilo de Post":
        if not config:
            await event.reply("⚠️ Nenhum canal configurado.")
            return
        buttons = [[Button.text(cid)] for cid in config.keys()]
        buttons.append([Button.text("⬅️ Voltar ao menu principal")])
        await event.reply("🎨 *Escolha o canal:*", buttons=buttons)
        state[user_id] = {"step": "escolher_estilo"}

    elif text == "🛠️ Painel ADM":
        adm_list = ""
        for uid in admins:
            try:
                user = await bot.get_entity(int(uid))
                nome = f"@{user.username}" if user.username else user.first_name
                adm_list += f"👤 {uid} - {nome}\n"
            except:
                adm_list += f"👤 {uid}\n"
        buttons = [
            [Button.text("➕ Permissão para Novo ADM")],
            [Button.text("➖ Remover ADM")],
            [Button.text("⬅️ Voltar ao menu principal")]
        ]
        await event.reply(f"🛠️ *Painel ADM*\n{adm_list}", buttons=buttons)
        state[user_id] = {"step": "painel_adm"}

    elif user_id in state:
        step = state[user_id]["step"]

        if step == "canal_id":
            if not text.startswith("-100"):
                await event.reply("⚠️ O ID do canal deve começar com -100.")
                return
            config[text] = {"texto": "", "sticker_id": "", "botao": {"nome": "", "link": ""}}
            save_json(CONFIG_FILE, config)
            state[user_id] = {"step": "texto", "canal": text}
            await event.reply("✏️ Envie o *texto da legenda* do post:", buttons=[[Button.text("⬅️ Voltar ao menu principal")]])

        elif step == "texto":
            canal = state[user_id]["canal"]
            config[canal]["texto"] = text
            save_json(CONFIG_FILE, config)
            state[user_id]["step"] = "sticker"
            await event.reply("🌟 Agora envie o *sticker*:", buttons=[[Button.text("⬅️ Voltar ao menu principal")]])

        elif step == "sticker":
            if event.sticker:
                canal = state[user_id]["canal"]
                config[canal]["sticker_id"] = event.file.id
                save_json(CONFIG_FILE, config)
                state[user_id]["step"] = "botao"
                await event.reply("🔗 Envie o botão no formato: Texto | Link", buttons=[[Button.text("⬅️ Voltar ao menu principal")]])
            else:
                await event.reply("⚠️ Envie um sticker válido.")

        elif step == "botao":
            canal = state[user_id]["canal"]
            try:
                nome, link = map(str.strip, text.split("|", 1))
                config[canal]["botao"] = {"nome": nome, "link": link}
                save_json(CONFIG_FILE, config)
                del state[user_id]
                await event.reply("✅ Configuração concluída.")
                await start(event)
            except:
                await event.reply("⚠️ Formato inválido. Use: Texto | Link")

        elif step == "permissoes":
            if "| " in text:
                status, chave = text.split("| ")
                chave = chave.strip()
                if chave in permissoes:
                    permissoes[chave] = True if "ON" in status else False
                    save_json(PERMISSOES_FILE, permissoes)
                    await event.reply(
                        f"✅ Permissão para *{chave}* definida como *{'ON ❤️' if permissoes[chave] else 'OFF 💚'}*.",
                        buttons=gerar_botoes_permissoes()
                    )

        elif step == "gerenciar":
            canal_id = text.split(" - ")[0].strip()
            if canal_id in config:
                state[user_id] = {"step": "editar", "canal": canal_id}
                buttons = [
                    [Button.text("✏ Editar Texto")],
                    [Button.text("❌ Remover Texto")],
                    [Button.text("🌟 Editar Sticker")],
                    [Button.text("❌ Remover Sticker")],
                    [Button.text("🔗 Editar Botão")],
                    [Button.text("❌ Remover Botão")],
                    [Button.text("🗑️ Apagar Canal")],
                    [Button.text("⬅️ Voltar ao menu principal")]
                ]
                await event.reply(f"⚙ *Gerenciar Canal:* `{canal_id}`", buttons=buttons)
            else:
                await event.reply("⚠️ Canal não encontrado.")

        elif step == "editar":
            canal = state[user_id]["canal"]
            if text == "✏ Editar Texto":
                state[user_id]["step"] = "novo_texto"
                await event.reply("✏ Envie o novo *texto da legenda*:")
            elif text == "❌ Remover Texto":
                config[canal]["texto"] = ""
                save_json(CONFIG_FILE, config)
                await event.reply("✅ Texto removido.")
            elif text == "🌟 Editar Sticker":
                state[user_id]["step"] = "novo_sticker"
                await event.reply("🌟 Envie o novo *sticker*:")
            elif text == "❌ Remover Sticker":
                config[canal]["sticker_id"] = ""
                save_json(CONFIG_FILE, config)
                await event.reply("✅ Sticker removido.")
            elif text == "🔗 Editar Botão":
                state[user_id]["step"] = "novo_botao"
                await event.reply("🔗 Envie o novo botão no formato: Texto | Link")
            elif text == "❌ Remover Botão":
                config[canal]["botao"] = {"nome": "", "link": ""}
                save_json(CONFIG_FILE, config)
                await event.reply("✅ Botão removido.")
            elif text == "🗑️ Apagar Canal":
                del config[canal]
                save_json(CONFIG_FILE, config)
                del state[user_id]
                await event.reply("🗑️ Canal removido com sucesso.")
            elif text == "⬅️ Voltar ao menu principal":
                del state[user_id]
                await start(event)

        elif step == "novo_texto":
            canal = state[user_id]["canal"]
            config[canal]["texto"] = text
            save_json(CONFIG_FILE, config)
            await event.reply("✅ Texto atualizado.")
            del state[user_id]
            await start(event)

        elif step == "novo_sticker":
            canal = state[user_id]["canal"]
            if event.sticker:
                config[canal]["sticker_id"] = event.file.id
                save_json(CONFIG_FILE, config)
                await event.reply("✅ Sticker atualizado.")
                del state[user_id]
                await start(event)
            else:
                await event.reply("⚠️ Envie um sticker válido.")

        elif step == "novo_botao":
            canal = state[user_id]["canal"]
            try:
                nome, link = map(str.strip, text.split("|", 1))
                config[canal]["botao"] = {"nome": nome, "link": link}
                save_json(CONFIG_FILE, config)
                await event.reply("✅ Botão atualizado.")
                del state[user_id]
                await start(event)
            except:
                await event.reply("⚠️ Formato inválido. Use: Texto | Link")

        elif step == "escolher_estilo":
            if text in config:
                state[user_id] = {"step": "definir_estilo", "canal": text}
                buttons = [
                    [Button.text("📌 Modo Replay")],
                    [Button.text("📌 Modo Sequencial")],
                    [Button.text("⬅️ Voltar ao menu principal")]
                ]
                await event.reply(f"🎨 *Estilo para:* `{text}`", buttons=buttons)

        elif step == "definir_estilo":
            canal = state[user_id]["canal"]
            if text == "📌 Modo Replay":
                estilo[canal] = "replay"
                save_json(ESTILO_FILE, estilo)
                await event.reply("✅ Estilo definido como *Replay*.")
            elif text == "📌 Modo Sequencial":
                estilo[canal] = "sequencial"
                save_json(ESTILO_FILE, estilo)
                await event.reply("✅ Estilo definido como *Sequencial*.")
            del state[user_id]

        elif step == "painel_adm":
            if text == "➕ Permissão para Novo ADM":
                if user_id != OWNER_ID:
                    await event.reply("⚠️ Apenas o proprietário pode adicionar ADM.")
                    return
                state[user_id]["step"] = "novo_adm"
                await event.reply("👤 Envie o ID do novo ADM:")
            elif text == "➖ Remover ADM":
                if user_id != OWNER_ID:
                    await event.reply("⚠️ Apenas o proprietário pode remover ADM.")
                    return
                state[user_id]["step"] = "remover_adm"
                await event.reply("👤 Envie o ID do ADM a ser removido:")

        elif step == "novo_adm":
            uid = text.strip()
            if uid not in admins:
                admins.append(uid)
                save_json(ADMINS_FILE, admins)
                await event.reply("✅ Novo ADM adicionado.")
            else:
                await event.reply("⚠️ Esse ADM já existe.")
            del state[user_id]
            await start(event)

        elif step == "remover_adm":
            uid = text.strip()
            if uid != OWNER_ID and uid in admins:
                admins.remove(uid)
                save_json(ADMINS_FILE, admins)
                await event.reply("✅ ADM removido.")
            else:
                await event.reply("⚠️ Não é possível remover esse ADM.")
            del state[user_id]
            await start(event)

@bot.on(events.NewMessage())
async def responder_post(event):
    canal_id = str(event.chat_id)
    if event.is_channel and not event.out and canal_id in config:

        tipo = None
        if event.photo:
            tipo = "foto"
        elif event.video:
            tipo = "video"
        elif event.audio or event.voice:
            tipo = "audio"
        elif event.gif:
            tipo = "gif"
        elif event.sticker:
            return
        else:
            tipo = "texto"

        if not permissoes.get(tipo, True):
            return

        c = config[canal_id]
        estilo_canal = estilo.get(canal_id, "replay")
        msg = c["texto"]

        if estilo_canal == "sequencial" and event.message.message:
            msg = event.message.message + "\n" + (c["texto"] or "")

        buttons = None
        if c["botao"]["nome"] and c["botao"]["link"]:
            buttons = [Button.url(c["botao"]["nome"], c["botao"]["link"])]

        try:
            await event.edit(msg, buttons=buttons)
        except:
            pass

        if permissoes.get("sticker", True) and c["sticker_id"]:
            await bot.send_file(event.chat_id, c["sticker_id"])

bot.run_until_disconnected()


