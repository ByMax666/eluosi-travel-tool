"""
阿杜俄旅 · 后端API服务
FastAPI + SQLite
"""

import json
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(__file__))

from database import get_db, init_db
from auth import verify_password, create_access_token, decode_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("🚀 阿杜俄旅 API 已启动: http://localhost:8766")
    yield

app = FastAPI(title="阿杜俄旅 API", version="0.31", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)


# ===== Models =====

class LoginRequest(BaseModel):
    username: str
    password: str

class ProjectCreate(BaseModel):
    name: str
    state: dict = {}

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[dict] = None
    status: Optional[str] = None

class WholeDBUpdate(BaseModel):
    rates: dict = {}
    attractions: list = []


# ===== Auth Deps =====

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="未登录")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="登录已过期")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="无效令牌")
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return dict(user)


def require_admin(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


# ===== Auth =====

@app.post("/api/login")
def login(req: LoginRequest):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (req.username,)).fetchone()
    conn.close()
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="账号或密码错误")
    token = create_access_token({"sub": user["id"], "role": user["role"]})
    return {
        "token": token,
        "user": {"id": user["id"], "name": user["name"], "role": user["role"]}
    }


@app.get("/api/me")
def get_me(user: dict = Depends(get_current_user)):
    return {"id": user["id"], "name": user["name"], "role": user["role"]}


# ===== Projects =====

@app.get("/api/projects")
def list_projects(user: dict = Depends(get_current_user)):
    conn = get_db()
    rows = conn.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [{
        "id": r["id"], "name": r["name"],
        "creator_id": r["creator_id"], "creator_name": r["creator_name"],
        "status": r["status"], "state": json.loads(r["state_json"]),
        "created_at": r["created_at"], "updated_at": r["updated_at"],
    } for r in rows]


@app.post("/api/projects")
def create_project(proj: ProjectCreate, user: dict = Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute(
        "INSERT INTO projects (name,creator_id,creator_name,status,state_json,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",
        (proj.name, user["id"], user["name"], "draft",
         json.dumps(proj.state, ensure_ascii=False), now, now))
    pid = c.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    conn.close()
    return {
        "id": row["id"], "name": row["name"],
        "creator_id": row["creator_id"], "creator_name": row["creator_name"],
        "status": row["status"], "state": json.loads(row["state_json"]),
        "created_at": row["created_at"], "updated_at": row["updated_at"],
    }


@app.put("/api/projects/{pid}")
def update_project(pid: int, proj: ProjectUpdate, user: dict = Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="方案不存在")
    now = datetime.utcnow().isoformat()
    if proj.name is not None:
        c.execute("UPDATE projects SET name=?,updated_at=? WHERE id=?", (proj.name, now, pid))
    if proj.state is not None:
        c.execute("UPDATE projects SET state_json=?,updated_at=? WHERE id=?",
                  (json.dumps(proj.state, ensure_ascii=False), now, pid))
    if proj.status is not None:
        c.execute("UPDATE projects SET status=?,updated_at=? WHERE id=?", (proj.status, now, pid))
    conn.commit()
    updated = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    conn.close()
    return {
        "id": updated["id"], "name": updated["name"],
        "creator_id": updated["creator_id"], "creator_name": updated["creator_name"],
        "status": updated["status"], "state": json.loads(updated["state_json"]),
        "created_at": updated["created_at"], "updated_at": updated["updated_at"],
    }


@app.delete("/api/projects/{pid}")
def delete_project(pid: int, user: dict = Depends(get_current_user)):
    conn = get_db()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="方案不存在")
    conn.execute("DELETE FROM projects WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    return {"ok": True}


# ===== Base Data =====

@app.get("/api/db")
def get_full_db():
    conn = get_db()
    cities = [dict(r) for r in conn.execute("SELECT * FROM cities ORDER BY sort_order").fetchall()]
    attractions = [dict(r) for r in conn.execute("SELECT * FROM attractions").fetchall()]
    rates_rows = conn.execute("SELECT * FROM rates").fetchall()
    conn.close()

    attrs_by_city = {}
    for a in attractions:
        code = a["city_code"]
        attrs_by_city.setdefault(code, []).append({
            "id": a["id"], "name": a["name"], "type": a["type"],
            "cost": a["cost_rub"],
            "needRu": bool(a["need_ru_guide"]),
            "ruCost": a["ru_guide_cost"],
        })

    rates = {r["key"]: r["value"] for r in rates_rows}
    cities_dict = {c["code"]: {"name": c["name"], "nameRu": c["name_ru"], "emoji": c["emoji"]} for c in cities}

    return {
        "cities": cities_dict,
        "attractions": attrs_by_city,
        "rates": rates,
        "citiesList": [dict(c) for c in cities],
    }


@app.put("/api/db")
def update_full_db(data: WholeDBUpdate, user: dict = Depends(require_admin)):
    conn = get_db()
    c = conn.cursor()
    for key, value in data.rates.items():
        c.execute("INSERT INTO rates(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=?",
                  (key, value, value))
    if data.attractions:
        c.execute("DELETE FROM attractions")
        for a in data.attractions:
            c.execute(
                "INSERT INTO attractions(id,city_code,name,type,cost_rub,need_ru_guide,ru_guide_cost) VALUES(?,?,?,?,?,?,?)",
                (a.get("id"), a.get("city_code"), a.get("name"), a.get("type", "sight"),
                 a.get("cost", 0), 1 if a.get("needRu") else 0, a.get("ruCost", 0)))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.put("/api/rates")
def update_rates(rates: dict, user: dict = Depends(require_admin)):
    conn = get_db()
    c = conn.cursor()
    for key, value in rates.items():
        c.execute("INSERT INTO rates(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=?",
                  (key, value, value))
    conn.commit()
    conn.close()
    return {"ok": True}


# ===== Health =====

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.31"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8766))
    uvicorn.run(app, host="0.0.0.0", port=port)
