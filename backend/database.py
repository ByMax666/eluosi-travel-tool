"""
SQLite database setup and seed data for 阿杜俄旅 backend.
Single-file: uses raw sqlite3 for simplicity.
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "adu_travel.db")


def get_db():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables and seed default data if empty."""
    conn = get_db()
    c = conn.cursor()

    # --- Users ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'staff',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- Cities ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            name_ru TEXT,
            emoji TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0
        )
    """)

    # --- Attractions ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS attractions (
            id TEXT PRIMARY KEY,
            city_code TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT DEFAULT 'sight',
            cost_rub REAL DEFAULT 0,
            need_ru_guide INTEGER DEFAULT 0,
            ru_guide_cost REAL DEFAULT 0,
            FOREIGN KEY (city_code) REFERENCES cities(code) ON DELETE CASCADE
        )
    """)

    # --- Rates (key-value base pricing) ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS rates (
            key TEXT PRIMARY KEY,
            name TEXT,
            value REAL NOT NULL DEFAULT 0,
            description TEXT
        )
    """)

    # --- Projects ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL DEFAULT '新建方案',
            creator_id TEXT NOT NULL,
            creator_name TEXT,
            status TEXT DEFAULT 'draft',
            state_json TEXT NOT NULL DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users(id)
        )
    """)

    # --- Seed default data (only if tables are empty) ---
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        _seed_data(conn)

    conn.commit()
    conn.close()
    print("✅ Database initialized")


def _seed_data(conn):
    """Insert default users, cities, attractions, rates."""
    from auth import hash_password
    c = conn.cursor()

    # Users
    users = [
        ("3056898", "管理员", "admin"),
        ("staff01", "员工老王", "staff"),
    ]
    for uid, name, role in users:
        pw = "pan3056898" if uid == "3056898" else "adu123"
        c.execute("INSERT INTO users (id,name,password_hash,role) VALUES (?,?,?,?)",
                  (uid, name, hash_password(pw), role))

    # Cities (15 major Russian tourist cities)
    cities = [
        ("msk", "莫斯科", "Москва", "🏛️", 1),
        ("spb", "圣彼得堡", "Санкт-Петербург", "🌉", 2),
        ("tula", "图拉", "Тула", "🏰", 3),
        ("vladimir", "弗拉基米尔", "Владимир", "⛪", 4),
        ("suzdal", "苏兹达尔", "Суздаль", "🕌", 5),
        ("kazan", "喀山", "Казань", "🕌", 6),
        ("ekb", "叶卡捷琳堡", "Екатеринбург", "🏭", 7),
        ("sochi", "索契", "Сочи", "🏖️", 8),
        ("irkutsk", "伊尔库茨克", "Иркутск", "🌲", 9),
        ("baikal", "贝加尔湖", "Байкал", "🏔️", 10),
        ("murmansk", "摩尔曼斯克", "Мурманск", "🌌", 11),
        ("novgorod", "大诺夫哥罗德", "Великий Новгород", "🏛️", 12),
        ("pskov", "普斯科夫", "Псков", "🏰", 13),
        ("kaliningrad", "加里宁格勒", "Калининград", "🌊", 14),
        ("vladivostok", "符拉迪沃斯托克", "Владивосток", "🚢", 15),
    ]
    c.executemany("INSERT INTO cities VALUES (?,?,?,?,?)", cities)

    # Rates
    rates = [
        ("bus_hour", "大巴/小时", 3510, "35座大巴每小时卢布价"),
        ("minibus_hour", "中巴/小时", 2500, "18座中巴每小时卢布价"),
        ("guide_cn_day", "中文导游/天", 25000, "中文导游全天费用"),
        ("guide_cn_half", "中文导游/半天", 15000, "中文导游半天费用"),
        ("hotel_3", "三星酒店/间晚", 2500, "三星酒店每间每晚"),
        ("hotel_4", "四星酒店/间晚", 3500, "四星酒店每间每晚"),
        ("hotel_5", "五星酒店/间晚", 6000, "五星酒店每间每晚"),
        ("meal_lunch", "午餐/人", 1500, "午餐人均"),
        ("meal_dinner", "晚餐/人", 2000, "晚餐人均"),
        ("train_spb", "高铁莫-彼/人", 6000, "莫斯科-圣彼得堡高铁"),
        ("train_other", "高铁其他/人", 4000, "其他城际高铁"),
        ("parking", "停车/天", 2500, "每日停车费"),
        ("registration", "注册费/人", 350, "落地注册费"),
        ("highway", "高速费/天", 1500, "每日高速费"),
        ("driver_meal", "司机餐费/天", 800, "司机每日餐补"),
        ("driver_overnight", "司机过夜费/次", 3000, "司机过夜住宿补贴"),
        ("metro_day", "地铁日票/人", 500, "地铁日票人均"),
        ("airport_pickup", "接机/次", 5000, "单次接机费用"),
        ("airport_dropoff", "送机/次", 5000, "单次送机费用"),
        ("season_pct", "旺季加成%", 15, "旺季(5-9月)百分比加成"),
    ]
    c.executemany("INSERT INTO rates VALUES (?,?,?,?)", rates)

    # Attractions (Moscow only as seed - rest can be added through admin)
    attractions = [
        ("msk01", "msk", "红场", "sight", 0, 0, 0),
        ("msk02", "msk", "圣瓦西里大教堂", "sight", 1200, 0, 0),
        ("msk03", "msk", "克里姆林宫", "sight", 1500, 1, 1500),
        ("msk04", "msk", "军械库", "sight", 2000, 1, 2000),
        ("msk05", "msk", "钻石馆", "sight", 1900, 0, 0),
        ("msk06", "msk", "特列季亚科夫画廊", "sight", 1200, 1, 11800),
        ("msk07", "msk", "莫斯科地铁游览", "sight", 180, 0, 0),
        ("msk08", "msk", "麻雀山观景台", "sight", 0, 0, 0),
        ("msk09", "msk", "莫斯科大学", "sight", 0, 0, 0),
        ("msk10", "msk", "基督救世主大教堂", "sight", 0, 0, 0),
        ("msk11", "msk", "武装力量大教堂+爱国者公园", "sight", 1100, 0, 0),
        ("msk12", "msk", "古姆百货", "free", 0, 0, 0),
        ("msk13", "msk", "列宁墓", "sight", 0, 0, 0),
        ("msk14", "msk", "国家历史博物馆", "sight", 800, 0, 0),
        ("spb01", "spb", "冬宫/埃尔米塔日", "sight", 2500, 1, 2000),
        ("spb02", "spb", "夏宫", "sight", 2000, 0, 0),
        ("spb03", "spb", "叶卡捷琳娜宫", "sight", 1800, 1, 3000),
        ("spb04", "spb", "彼得保罗要塞", "sight", 800, 0, 0),
        ("spb05", "spb", "滴血救世主教堂", "sight", 600, 0, 0),
        ("spb06", "spb", "伊萨基辅大教堂", "sight", 600, 0, 0),
        ("spb07", "spb", "涅瓦大街", "free", 0, 0, 0),
        ("spb08", "spb", "俄罗斯博物馆", "sight", 1200, 0, 0),
        ("tula01", "tula", "图拉克里姆林宫", "sight", 500, 0, 0),
        ("tula02", "tula", "武器博物馆", "sight", 800, 0, 0),
        ("tula03", "tula", "蜜糖饼博物馆", "sight", 800, 0, 0),
        ("tula04", "tula", "亚斯纳亚波良纳庄园", "sight", 1200, 0, 0),
    ]
    c.executemany("INSERT INTO attractions VALUES (?,?,?,?,?,?,?)", attractions)

    print("✅ Seed data inserted")

print("database.py loaded")
