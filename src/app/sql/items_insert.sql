INSERT INTO items (name, description, category_id) VALUES (:name, :description, :category_id) RETURNING id, name, description, category_id
