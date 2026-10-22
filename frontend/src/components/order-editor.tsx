"use client";
import { useState, useEffect, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { api, errorText, Order, Category } from "@/lib/api";
export default function OrderEditor({
  order,
  onSaved,
}: {
  order?: Order;
  onSaved?: (order: Order) => void;
}) {
  const router = useRouter();
  const [title, setTitle] = useState(order?.title || ""),
    [description, setDescription] = useState(order?.description || ""),
    [category, setCategory] = useState(order?.category_id || ""),
    [budget, setBudget] = useState(
      order ? String(order.budget_minor / 100) : "",
    ),
    [categories, setCategories] = useState<Category[]>([]),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const changed =
    !order ||
    title !== order.title ||
    description !== order.description ||
    category !== (order.category_id || "") ||
    Math.round(Number(budget) * 100) !== order.budget_minor;
  useEffect(() => {
    api
      .get<Category[]>("/catalog/categories")
      .then((r) => setCategories(r.data))
      .catch((e) => setError(errorText(e)));
  }, []);
  useEffect(() => {
    const warn = (e: BeforeUnloadEvent) => {
      if (changed) {
        e.preventDefault();
        e.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [changed]);
  async function save(e: FormEvent) {
    e.preventDefault();
    if (busy) return;
    setError("");
    setBusy(true);
    try {
      const payload = {
        title,
        description,
        category_id: category || null,
        budget_minor: Math.round(Number(budget || 0) * 100),
      };
      const r = order
        ? await api.put<Order>(`/orders/${order.id}`, {
            ...payload,
            version: order.version,
          })
        : await api.post<Order>("/orders", payload);
      if (onSaved) {
        onSaved(r.data);
      } else {
        router.push(`/orders/${r.data.id}?saved=1`);
      }
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className="editor" onSubmit={save}>
      <div className="form-section">
        <span className="step">01</span>
        <div>
          <h2>Расскажи о задаче</h2>
          <p className="muted">
            Понятное описание поможет исполнителю оценить объем работы.
          </p>
          <label>
            Название заказа
            <input
              required
              minLength={3}
              maxLength={255}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Например, разработать фирменный стиль кофейни"
            />
          </label>
          <label>
            Описание
            <textarea
              required
              maxLength={20000}
              rows={7}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Что нужно сделать? Какой результат ожидаешь? Укажи сроки и важные детали."
            />
          </label>
          <small className="muted">
            Для публикации нужно описание от 20 символов.
          </small>
        </div>
      </div>
      <div className="form-section">
        <span className="step">02</span>
        <div>
          <h2>Уточни условия</h2>
          <div className="form-columns">
            <label>
              Категория
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                <option value="">Выбрать категорию</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Бюджет за проект, ₸
              <input
                type="number"
                min={0}
                max={20000000}
                step="0.01"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                placeholder="Например, 150000"
              />
            </label>
          </div>
          <p className="muted small">
            Категорию и бюджет можно уточнить перед публикацией.
          </p>
        </div>
      </div>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <div className="form-footer">
        <span className="muted">
          {order && !changed ? "Изменений нет" : "Черновик виден только тебе"}
        </span>
        <button disabled={busy || !changed} className="primary">
          {busy ? "Сохраняем…" : "Сохранить черновик"}
        </button>
      </div>
    </form>
  );
}
