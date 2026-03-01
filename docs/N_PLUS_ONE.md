# 隱含 N+1 查詢（Implicit N+1）

真正的危險是：**你根本沒寫 loop，卻還是發生 N+1。**
通常發生在 **ORM 預設 lazy loading** 的情況。

---

## Case 1：Pydantic / FastAPI 自動序列化觸發

```python
@router.get("/categories", response_model=list[CategoryWithItemsResponse])
async def list_categories(db: DbSession):
    result = await db.execute(select(Category))
    return result.scalars().all()
```

看起來完全正常。但如果 `Category.items` 是 `relationship(..., lazy="select")`（預設）：

當 FastAPI 序列化 `response_model` 時，Pydantic 會 access `category.items` → **觸發 lazy load**。

```sql
SELECT * FROM category;
-- Pydantic 序列化時
SELECT * FROM item WHERE category_id = 1;
SELECT * FROM item WHERE category_id = 2;
SELECT * FROM item WHERE category_id = 3;
...
```

**程式碼裡完全沒有寫 loop 查 DB，但還是 N+1。**
👉 這是 production 最常見事故。

**對應端點**：`GET /api/v1/items/categories-with-items/implicit-pydantic`

---

## Case 2：Property 中觸發

```python
class Category(Base):
    items = relationship("Item")

    @property
    def item_count(self):
        return len(self.items)   # 這行會觸發 lazy load
```

```python
for cat in categories:
    print(cat.item_count)
```

看起來只是算長度，實際上每個 category 都跑一次 `SELECT * FROM item WHERE category_id=?`。

**對應端點**：`GET /api/v1/items/categories-with-items/implicit-property`

---

## Case 3：List comprehension 中觸發

```python
result = await db.execute(select(Category))
categories = result.scalars().all()

data = [
    {"id": c.id, "name": c.name, "items": [i.name for i in c.items]}
    for c in categories
]
```

`c.items` 是 lazy load，結果還是 N+1。

**對應端點**：`GET /api/v1/items/categories-with-items/implicit-listcomp`

---

## Case 4：Template / Jinja2 中

```jinja2
{% for category in categories %}
  {% for item in category.items %}
     {{ item.name }}
  {% endfor %}
{% endfor %}
```

Jinja render 時 access `category.items` → N+1。

---

## 防止隱含 N+1

### 方法 1：relationship 設 `lazy="raise"`

```python
items = relationship("Item", lazy="raise")
```

忘記 eager load 時會直接拋錯。

### 方法 2：強制 eager load

```python
select(Category).options(selectinload(Category.items))
```

### 方法 3：預設使用 selectinload

```python
items = relationship("Item", lazy="selectin")
```

---

## 正確寫法（本專案）

`GET /api/v1/items/categories-with-items/eager` 使用 `selectinload`，僅 2 次查詢。

---

## 注意：Async SQLAlchemy

本專案使用 async SQLAlchemy。Lazy load 在 async 情境下可能觸發 `MissingGreenlet`（尤其 TestClient）。
隱含 N+1 端點主要作為**程式碼範例**，展示錯誤寫法。
以 sync SQLAlchemy 或實際 uvicorn 執行時，才會完整呈現 N+1 行為。
