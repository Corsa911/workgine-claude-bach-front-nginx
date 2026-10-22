"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowUpRight, Plus, Search, FolderOpen } from "lucide-react";
import { api, errorText, Order, Category, money } from "@/lib/api";
import { useSession } from "@/components/session";
export default function Dashboard() {
  const { me } = useSession();
  const customer = me?.active_role === "customer";
  const [orders, setOrders] = useState<Order[]>([]),
    [categories, setCategories] = useState<Category[]>([]),
    [status, setStatus] = useState(""),
    [search, setSearch] = useState(""),
    [q, setQ] = useState(""),
    [category, setCategory] = useState(""),
    [offset, setOffset] = useState(0),
    [loadedKey, setLoadedKey] = useState(""),
    [error, setError] = useState(""),
    [retry, setRetry] = useState(0);
  useEffect(() => {
    let live = true;
    api
      .get<Category[]>("/catalog/categories")
      .then((r) => {
        if (live) setCategories(r.data);
      })
      .catch(() => {});
    return () => {
      live = false;
    };
  }, []);
  const requestKey = JSON.stringify([
    customer,
    status,
    q,
    category,
    offset,
    retry,
  ]);
  const busy = loadedKey !== requestKey;
  useEffect(() => {
    let live = true;
    api
      .get<Order[]>("/orders", {
        params: {
          scope: customer ? "mine" : "market",
          status_filter: customer && status ? status : undefined,
          q,
          category_id: category || undefined,
          offset,
          limit: 12,
        },
      })
      .then((r) => {
        if (live) {
          setOrders(r.data);
          setError("");
        }
      })
      .catch((e) => {
        if (live) setError(errorText(e));
      })
      .finally(() => {
        if (live) setLoadedKey(requestKey);
      });
    return () => {
      live = false;
    };
  }, [customer, status, q, category, offset, retry, requestKey]);
  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            {customer ? "ТВОИ ИДЕИ В РАБОТЕ" : "НОВЫЕ ВОЗМОЖНОСТИ"}
          </p>
          <h1>{customer ? "Мои заказы" : "Найди свой следующий проект"}</h1>
          <p className="muted">
            {customer
              ? "Все задачи и их статусы в одном месте."
              : "Выбирай задачи, в которых твой опыт принесет результат."}
          </p>
        </div>
        {customer && (
          <Link className="primary" href="/orders/new">
            <Plus size={18} />
            Создать заказ
          </Link>
        )}
      </div>
      <section className="banner">
        <div>
          <span className="banner-tag">
            {customer ? "ОТ ИДЕИ К ДЕЙСТВИЮ" : "ТВОЯ ЭКСПЕРТИЗА ИМЕЕТ ЗНАЧЕНИЕ"}
          </span>
          <h2>
            {customer
              ? "Большие проекты начинаются\nс понятной задачи."
              : "Расскажи, что у тебя\nполучается лучше всего."}
          </h2>
          <p>
            {customer
              ? "Опиши результат, сроки и бюджет. Это поможет найти своего специалиста."
              : "Заполни профиль, чтобы подготовиться к новым проектам."}
          </p>
          {!customer && (
            <Link href="/profile">
              Заполнить профиль <ArrowUpRight size={17} />
            </Link>
          )}
        </div>
        <div className="banner-art" aria-hidden="true">
          <div />
          <div />
          <div />
          <span>W</span>
        </div>
      </section>
      <section className="orders-section">
        <div className="list-toolbar">
          {customer ? (
            <div className="tabs">
              {[
                ["", "Все заказы"],
                ["draft", "Черновики"],
                ["published", "Опубликованные"],
              ].map(([value, label]) => (
                <button
                  key={value}
                  className={status === value ? "selected" : ""}
                  onClick={() => {
                    setStatus(value);
                    setOffset(0);
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          ) : (
            <h2>Открытые заказы</h2>
          )}
          <span className="muted small">
            {busy ? "Обновляем…" : `На странице: ${orders.length}`}
          </span>
        </div>
        <form
          className="filters"
          onSubmit={(e) => {
            e.preventDefault();
            setQ(search);
            setOffset(0);
          }}
        >
          <div className="search">
            <Search size={18} />
            <input
              aria-label="Поиск по названию"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Поиск по названию заказа"
            />
          </div>
          <select
            aria-label="Категория"
            value={category}
            onChange={(e) => {
              setCategory(e.target.value);
              setOffset(0);
            }}
          >
            <option value="">Все категории</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          <button className="secondary">Найти</button>
        </form>
        {error && !busy ? (
          <div role="alert" className="empty">
            <p className="error">{error}</p>
            <button className="secondary" onClick={() => setRetry(retry + 1)}>
              Повторить
            </button>
          </div>
        ) : busy ? (
          <div className="empty" role="status">
            Загружаем заказы…
          </div>
        ) : !orders.length ? (
          <div className="empty">
            <FolderOpen size={35} />
            <h3>
              {q || category || status || offset
                ? "Заказы не найдены"
                : customer
                  ? "Здесь появится твой первый заказ"
                  : "Пока нет открытых заказов"}
            </h3>
            <p>
              {customer
                ? "Создай задачу или измени параметры поиска."
                : "Загляни позже или измени параметры поиска. Твои собственные заказы здесь не показываются."}
            </p>
            {customer && (
              <Link href="/orders/new" className="primary">
                Создать заказ
              </Link>
            )}
          </div>
        ) : (
          <div className="order-list">
            {orders.map((order) => (
              <Link
                href={`/orders/${order.id}`}
                className="order-card"
                key={order.id}
              >
                <div>
                  <div className="card-meta">
                    <span className={`badge ${order.status}`}>
                      {order.status === "draft" ? "Черновик" : "Опубликован"}
                    </span>
                    <span>
                      {categories.find((c) => c.id === order.category_id)
                        ?.name || "Без категории"}
                    </span>
                  </div>
                  <h3>{order.title}</h3>
                  <p>{order.description}</p>
                  <span className="small muted">
                    {new Date(order.created_at).toLocaleDateString("ru-RU")}
                  </span>
                </div>
                <div className="card-price">
                  <strong>
                    {order.budget_minor
                      ? money(order.budget_minor)
                      : "Бюджет не указан"}
                  </strong>
                  <span>
                    За проект <ArrowUpRight size={18} />
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
        <div className="pagination">
          <button
            disabled={busy || offset === 0}
            onClick={() => setOffset(Math.max(0, offset - 12))}
          >
            Назад
          </button>
          <span>Страница {offset / 12 + 1}</span>
          <button
            disabled={busy || orders.length < 12}
            onClick={() => setOffset(offset + 12)}
          >
            Дальше
          </button>
        </div>
      </section>
    </>
  );
}
