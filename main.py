import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3

# Initialize database
def init_db():
    conn = sqlite3.connect('filters.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS filters
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
    conn.commit()
    conn.close()

# Add filter to database
def add_filter(filter_name):
    conn = sqlite3.connect('filters.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO filters (name) VALUES (?)", (filter_name,))
        conn.commit()
        success = True
    except:
        success = False
    conn.close()
    return success

# Get all filters from database
def get_all_filters():
    conn = sqlite3.connect('filters.db')
    c = conn.cursor()
    c.execute("SELECT name FROM filters ORDER BY name")
    filters = [row[0] for row in c.fetchall()]
    conn.close()
    return filters

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Anime Filter Bot!\n\n"
        "Use /filter [anime_name] to add a new anime filter\n"
        "Use /filters to see all available filters\n"
        "Use /stop to stop the bot"
    )

# Add filter command
async def add_filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide an anime name. Example: /filter Naruto")
        return
    
    filter_name = " ".join(context.args)
    if add_filter(filter_name):
        await update.message.reply_text(f"Added filter: {filter_name}")
    else:
        await update.message.reply_text(f"Filter '{filter_name}' already exists!")

# Show all filters
async def show_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters = get_all_filters()
    if not filters:
        await update.message.reply_text("No filters added yet. Use /filter [name] to add one.")
        return
    
    # Create buttons in rows of 2 for better mobile layout
    keyboard = []
    for i in range(0, len(filters), 2):
        row = []
        if i < len(filters):
            row.append(InlineKeyboardButton(filters[i], callback_data=filters[i]))
        if i + 1 < len(filters):
            row.append(InlineKeyboardButton(filters[i+1], callback_data=filters[i+1]))
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Click on an anime to copy its name:", reply_markup=reply_markup)

# Handle button clicks
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(f"Copied '{query.data}' to clipboard!", show_alert=True)

# Stop command
async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Stopping the bot...")
    # For Render, we don't want to actually stop the application

def main():
    # Initialize database
    init_db()
    
    
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("filter", add_filter_command))
    application.add_handler(CommandHandler("filters", show_filters))
    application.add_handler(CommandHandler("stop", stop_bot))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
