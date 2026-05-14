"""
Telegram Bot - Centro di Controllo
Raccoglie dati: soldi, fumo, palestra, mood, note
Invia al backend FastAPI
"""

import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import httpx
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Configurazione logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carica variabili ambiente
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Stati per conversazioni (se necessario)
AWAITING_AMOUNT, AWAITING_CATEGORY, AWAITING_NOTE = range(3)


class EventManager:
    """Gestisce l'invio eventi al backend"""
    
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
        self.client = httpx.AsyncClient()
    
    async def send_event(self, event_type: str, value, category: str = None, note: str = None, metadata: dict = None):
        """Invia evento standardizzato al backend"""
        payload = {
            "type": event_type,
            "value": value,
            "category": category,
            "note": note,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        try:
            response = await self.client.post(
                f"{self.backend_url}/api/events",
                json=payload
            )
            response.raise_for_status()
            return True, "✅ Salvato"
        except Exception as e:
            logger.error(f"Errore invio evento: {e}")
            return False, f"❌ Errore: {str(e)}"


# Istanza globale
event_manager = EventManager(BACKEND_URL)


# ============ COMANDI PRINCIPALI ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start"""
    welcome_text = """
🚀 *Benvenuto nel Centro di Controllo Personale!*

Comandi disponibili:

💰 *Finanze*
`/soldi +100 stipendio` - Entrata
`/soldi -15 pizza` - Uscita

🚬 *Fumo*
`/fumo 3` - Sigarette fumate oggi
`/fumo reset` - Azzera contatore

🏋️ *Palestra*
`/gym push` - Allenamento push
`/gym pull` - Allenamento pull
`/gym legs` - Allenamento gambe

😊 *Mood*
`/mood 8` - Scala 1-10

📝 *Note*
`/note giornata molto produttiva` - Nota libera

⚙️ *Sistema*
`/status` - Status del sistema
`/ai on` - Accendi AI
`/ai off` - Spegni AI
`/market on` - Accendi analisi mercato
`/market off` - Spegni analisi mercato

🔗 *Dashboard*
`/dashboard` - Visualizza link dashboard

📊 *Dati*
`/stats` - Statistiche personali
`/export` - Esporta dati
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def money_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce /soldi"""
    if not context.args:
        await update.message.reply_text("Uso: `/soldi +100 stipendio` oppure `/soldi -15 pizza`", parse_mode='Markdown')
        return
    
    try:
        # Parsa: /soldi +100 stipendio
        amount_str = context.args[0]
        amount = float(amount_str)
        note = " ".join(context.args[1:]) if len(context.args) > 1 else ""
        
        # Categorizza automaticamente
        category = categorize_money(note)
        
        success, msg = await event_manager.send_event(
            event_type="money",
            value=amount,
            category=category,
            note=note
        )
        
        emoji = "➕" if amount > 0 else "➖"
        await update.message.reply_text(
            f"{emoji} Soldi: {amount:+.2f}€\n"
            f"Categoria: {category}\n"
            f"Nota: {note}\n"
            f"{msg}",
            parse_mode='Markdown'
        )
    except ValueError:
        await update.message.reply_text("❌ Importo non valido. Uso: `/soldi +100 stipendio`", parse_mode='Markdown')


async def smoke_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce /fumo"""
    if not context.args:
        await update.message.reply_text("Uso: `/fumo 3` oppure `/fumo reset`", parse_mode='Markdown')
        return
    
    try:
        arg = context.args[0].lower()
        
        if arg == "reset":
            success, msg = await event_manager.send_event(
                event_type="smoke",
                value=0,
                note="reset giornaliero"
            )
            await update.message.reply_text(f"🚬 Contatore azzerato\n{msg}")
        else:
            count = int(arg)
            success, msg = await event_manager.send_event(
                event_type="smoke",
                value=count
            )
            await update.message.reply_text(f"🚬 {count} sigaretta{'e' if count != 1 else ''}\n{msg}")
    except ValueError:
        await update.message.reply_text("❌ Valore non valido", parse_mode='Markdown')


async def gym_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce /gym"""
    if not context.args:
        await update.message.reply_text("Uso: `/gym push` oppure `/gym pull` oppure `/gym legs`", parse_mode='Markdown')
        return
    
    split = context.args[0].lower()
    valid_splits = ["push", "pull", "legs"]
    
    if split not in valid_splits:
        await update.message.reply_text(f"❌ Split non valido. Scegli tra: {', '.join(valid_splits)}")
        return
    
    success, msg = await event_manager.send_event(
        event_type="gym",
        value=1,
        category=split
    )
    
    emojis = {"push": "💪", "pull": "🎯", "legs": "🦵"}
    await update.message.reply_text(f"{emojis.get(split, '🏋️')} {split.upper()}\n{msg}")


async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce /mood"""
    if not context.args:
        await update.message.reply_text("Uso: `/mood 8` (scala 1-10)", parse_mode='Markdown')
        return
    
    try:
        score = int(context.args[0])
        if not 1 <= score <= 10:
            raise ValueError
        
        success, msg = await event_manager.send_event(
            event_type="mood",
            value=score
        )
        
        mood_emoji = "😭" if score <= 3 else "😐" if score <= 6 else "😊" if score <= 8 else "🤩"
        await update.message.reply_text(f"{mood_emoji} Mood: {score}/10\n{msg}")
    except ValueError:
        await update.message.reply_text("❌ Inserisci un numero tra 1 e 10")


async def note_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce /note"""
    if not context.args:
        await update.message.reply_text("Uso: `/note testo della nota`", parse_mode='Markdown')
        return
    
    note_text = " ".join(context.args)
    
    success, msg = await event_manager.send_event(
        event_type="note",
        value=note_text,
        category="personal"
    )
    
    await update.message.reply_text(f"📝 Nota salvata\n{msg}")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stato del sistema"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/api/status")
            data = response.json()
        
        status_text = f"""
✅ *Sistema Online*

📊 Backend: {data.get('backend', 'OK')}
🤖 AI: {'🟢 ON' if data.get('ai_enabled', False) else '🔴 OFF'}
📈 Market Analysis: {'🟢 ON' if data.get('market_enabled', False) else '🔴 OFF'}
💾 Ultimi eventi: {data.get('events_count', 0)}
        """
        await update.message.reply_text(status_text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Backend non raggiungibile: {e}")


async def ai_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Accendi AI"""
    success, msg = await event_manager.send_event(
        event_type="system",
        value="ai_enabled",
        note="ai turned on"
    )
    await update.message.reply_text("🤖 AI accesa ✅")


async def ai_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Spegni AI"""
    success, msg = await event_manager.send_event(
        event_type="system",
        value="ai_disabled",
        note="ai turned off"
    )
    await update.message.reply_text("🤖 AI spenta ❌")


async def market_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Accendi analisi mercato"""
    success, msg = await event_manager.send_event(
        event_type="system",
        value="market_enabled",
        note="market analysis turned on"
    )
    await update.message.reply_text("📈 Analisi mercato accesa ✅")


async def market_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Spegni analisi mercato"""
    success, msg = await event_manager.send_event(
        event_type="system",
        value="market_disabled",
        note="market analysis turned off"
    )
    await update.message.reply_text("📈 Analisi mercato spenta ❌")


async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Link al dashboard"""
    dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:3000")
    await update.message.reply_text(
        f"📊 [Apri Dashboard]({dashboard_url})",
        parse_mode='Markdown'
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Statistiche personali"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/api/stats")
            stats = response.json()
        
        stats_text = f"""
📊 *Statistiche Personali*

💰 Oggi: {stats.get('today_balance', 0):+.2f}€
💰 Settimana: {stats.get('week_balance', 0):+.2f}€
💰 Mese: {stats.get('month_balance', 0):+.2f}€

🚬 Sigarette oggi: {stats.get('smokes_today', 0)}
🚬 Media settimanale: {stats.get('smokes_weekly_avg', 0):.1f}

🏋️ Allenamenti mese: {stats.get('gym_sessions_month', 0)}

😊 Mood medio: {stats.get('mood_avg', 0):.1f}/10
        """
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Errore nel caricamento statistiche: {e}")


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Esporta dati"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/api/export")
            
        await update.message.reply_document(
            document=response.content,
            filename=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Errore esportazione: {e}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce errori globali"""
    logger.error(msg="Eccezione mentre si gestisce un aggiornamento:", exc_info=context.error)


# ============ UTILITY FUNCTIONS ============

def categorize_money(note: str) -> str:
    """Categorizza automaticamente una transazione in base alla nota"""
    keywords = {
        "food": ["pizza", "cibo", "burger", "pasta", "ristorante", "kebab", "dolce", "dessert"],
        "transport": ["uber", "taxi", "benzina", "metro", "bus", "viaggio"],
        "shopping": ["amazon", "negozio", "acquisto", "vestiti", "scarpe", "abiti"],
        "health": ["farmacia", "dottore", "medico", "palestra", "sport"],
        "work": ["stipendio", "lavoro", "freelance", "pagamento", "commissione"],
        "entertainment": ["cinema", "musica", "gioco", "streaming", "libro"],
        "utilities": ["luce", "acqua", "gas", "internet", "telefono"],
    }
    
    note_lower = note.lower()
    for category, words in keywords.items():
        if any(word in note_lower for word in words):
            return category
    
    return "other"


def main() -> None:
    """Avvia il bot"""
    # Crea l'applicazione
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Registra i gestori
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("soldi", money_command))
    app.add_handler(CommandHandler("fumo", smoke_command))
    app.add_handler(CommandHandler("gym", gym_command))
    app.add_handler(CommandHandler("mood", mood_command))
    app.add_handler(CommandHandler("note", note_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("ai", ai_on))
    app.add_handler(CommandHandler("ai_on", ai_on))
    app.add_handler(CommandHandler("ai_off", ai_off))
    app.add_handler(CommandHandler("market_on", market_on))
    app.add_handler(CommandHandler("market_off", market_off))
    app.add_handler(CommandHandler("dashboard", dashboard_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("export", export_command))
    
    # Gestore errori
    app.add_error_handler(error_handler)
    
    # Avvia il bot
    logger.info("🚀 Bot avviato. Premi Ctrl+C per fermare.")
    app.run_polling()


if __name__ == '__main__':
    main()
