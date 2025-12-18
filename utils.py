import aiosqlite

DB_NAME = "bot_database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id INTEGER PRIMARY KEY,
                prefix TEXT DEFAULT '!',
                autorole_human INTEGER,
                autorole_bot INTEGER,
                log_channel INTEGER,
                welcome_channel INTEGER,
                welcome_message TEXT,
                farewell_message TEXT
            )
        """)
        await db.commit()

async def get_config(guild_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row # Para acceder por nombre de columna
        async with db.execute("SELECT * FROM guild_config WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            
            if row is None:
                await db.execute("INSERT INTO guild_config (guild_id) VALUES (?)", (guild_id,))
                await db.commit()
                async with db.execute("SELECT * FROM guild_config WHERE guild_id = ?", (guild_id,)) as cursor:
                    row = await cursor.fetchone()
            return row

async def update_config(guild_id, column, value):
    await get_config(guild_id) 
    
    async with aiosqlite.connect(DB_NAME) as db:
        sql = f"UPDATE guild_config SET {column} = ? WHERE guild_id = ?"
        await db.execute(sql, (value, guild_id))
        await db.commit()