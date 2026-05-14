# 🚀 Centro di Controllo Personale - Bot Telegram

Sistema completo per il **tracking personale** + **dashboard web** + **API backend**.

## 📦 Cosa è Incluso

- **Bot Telegram** - Centro di controllo rapido per inserire dati
- **Backend FastAPI** - API per gestire i dati
- **Database SQLite** - Storage strutturato con schema standardizzato
- **Dashboard Web** - Visualizzazione grafica in tempo reale
- **Analytics** - Statistiche automatiche su soldi, mood, fumo, palestra

---

## ⚡ Quick Start

### 1. Installa dipendenze

```bash
python -m venv venv
source venv/bin/activate  # su Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configura il token Telegram

1. Apri Telegram e cerca **@BotFather**
2. Crea un nuovo bot: `/newbot`
3. Copia il token
4. Crea il file `.env`:

```bash
cp .env.example .env
```

5. Modifica `.env` e inserisci il token:

```
TELEGRAM_TOKEN=123456789:ABCDefGhIjklmnOPqrstUVwxyz
```

### 3. Avvia (in 3 terminali)

**Terminal 1 - Backend:**
```bash
python backend.py
```
Accedi a: http://localhost:8000/docs

**Terminal 2 - Bot:**
```bash
python telegram_bot.py
```

**Terminal 3 - Dashboard:**
```bash
# Opzione 1: Apri index.html nel browser
# Opzione 2: Avvia un server HTTP locale
python -m http.server 3000
# Poi vai a: http://localhost:3000
```

---

## 📱 Comandi Telegram

### 💰 Finanze

```
/soldi +1000 stipendio    # Entrata
/soldi -15 pizza          # Uscita (spesa)
/soldi -50 pranzo         # Automaticamente categorizzato
```

### 🚬 Fumo

```
/fumo 3                   # 3 sigarette fumate
/fumo reset               # Azzera contatore
```

### 🏋️ Palestra

```
/gym push                 # Allenamento push
/gym pull                 # Allenamento pull
/gym legs                 # Allenamento gambe
```

### 😊 Mood

```
/mood 8                   # Scala 1-10
/mood 5                   # Giornata così così
```

### 📝 Note

```
/note giornata produttiva   # Nota libera
/note riunione importante   # Si salva tutto
```

### ⚙️ Sistema

```
/status                     # Stato del sistema
/ai on / /ai off           # Accendi/spegni AI
/market on / /market off   # Accendi/spegni market analysis
/dashboard                 # Link al dashboard
/stats                     # Statistiche attuali
/export                    # Esporta tutti i dati in JSON
```

---

## 📊 Dashboard

Accedi a **http://localhost:3000** per vedere:

- 💰 **Bilancio** - Entrate/uscite (oggi, settimana, mese)
- 🚬 **Fumo** - Contatore e medie
- 🏋️ **Palestra** - Sessioni e frequenza
- 😊 **Mood** - Andamento mentale
- 📊 **Analytics** - Spese per categoria
- 📝 **Feed** - Ultimi 10 eventi registrati

**Si aggiorna automaticamente ogni 30 secondi** (clicca 🔄 per aggiornamento manuale).

---

## 🗄️ Database Schema

### Tabella: `events`

```sql
id              INTEGER PRIMARY KEY
type            TEXT (money, smoke, gym, mood, note, system)
value           TEXT (il valore dell'evento)
category        TEXT (food, transport, health, etc.)
note            TEXT (descrizione/dettagli)
metadata        JSON (dati aggiuntivi)
created_at      TIMESTAMP (quando è stato creato)
updated_at      TIMESTAMP (ultimo aggiornamento)
```

---

## 🔌 API Endpoints

Documentazione interattiva: **http://localhost:8000/docs**

### Principali

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| POST | `/api/events` | Crea nuovo evento |
| GET | `/api/events` | Lista eventi (ultimi 100) |
| GET | `/api/events/{type}` | Eventi di un tipo specifico |
| GET | `/api/stats` | Statistiche aggregate |
| GET | `/api/status` | Status del sistema |
| GET | `/api/analytics/money` | Analytics dettagliate spese |
| GET | `/api/analytics/mood` | Analytics mood |
| GET | `/api/export` | Esporta tutti i dati |

---

## 🛠️ Struttura File

```
botelegram/
├── telegram_bot.py       # Bot Telegram
├── backend.py            # FastAPI Backend + DB
├── index.html            # Dashboard Web
├── requirements.txt      # Dipendenze Python
├── .env.example          # Template configurazione
├── events.db             # Database SQLite (auto-creato)
└── README.md             # Questo file
```

---

## 🔄 Flusso Dati

```
Telegram Bot
    ↓
    Inserisci dati (/solmi, /fumo, etc.)
    ↓
Backend FastAPI
    ↓
    Valida + Categorizza
    ↓
SQLite Database
    ↓
    Salva evento standardizzato
    ↓
Dashboard Web
    ↓
    Legge API backend ogni 30 secondi
    ↓
Visualizza grafici + statistiche
```

---

## 📈 Caratterizzazione Automatica

### Soldi (money)

Il bot categorizza automaticamente le spese:

- **food** - pizza, burger, ristorante, kebab, dolce
- **transport** - uber, taxi, benzina, metro, bus
- **shopping** - amazon, negozio, vestiti, scarpe
- **health** - farmacia, dottore, palestra
- **work** - stipendio, lavoro, freelance
- **entertainment** - cinema, musica, gioco, libro
- **utilities** - luce, acqua, gas, internet
- **other** - tutto il resto

---

## 🚀 Prossimi Sviluppi

- [ ] Integrazione dati crypto/stocks
- [ ] AI analysis per anomaly detection
- [ ] PostgreSQL per scalabilità multi-user
- [ ] Deploy cloud (Vercel/Railway)
- [ ] Export PDF report mensili
- [ ] Notifiche automatiche su obiettivi
- [ ] Correlazione mood ↔ spese

---

## 📝 Configurazione Avanzata

### Cambiare porta del backend

In `backend.py` (ultima riga):
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Cambia da 8000 a 8001
```

### Cambiare database path

In `backend.py`:
```python
db = Database("/percorso/custom/events.db")
```

### Disabilitare CORS

In `backend.py`, commenta la sezione CORS se serve solo uso locale.

---

## 🐛 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'telegram'"

```bash
pip install python-telegram-bot
```

### ❌ "Backend non raggiungibile"

Assicurati che `python backend.py` sia in esecuzione.

### ❌ "Token Telegram non valido"

Verifica che in `.env` il token sia corretto (copiato da @BotFather).

### ❌ "Dashboard bianco"

1. Apri browser console (F12)
2. Controlla gli errori
3. Assicurati backend sia online su localhost:8000

---

## 📖 Documentazione API Swagger

Una volta che il backend è avviato, accedi a:

**http://localhost:8000/docs**

Puoi testare tutti gli endpoints direttamente dal browser!

---

## 📄 Licenza

Progetto personale - Libero di usare e modificare.

---

## 💬 Supporto

Per domande sul progetto, apri una issue nel repository GitHub.

---

**Divertiti a trackare la tua vita! 🚀📊**
