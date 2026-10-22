"use client";
import { use, useEffect, useState } from "react";
import Link from "next/link";
import { api, errorText, Order, money } from "@/lib/api";
import { useSession } from "@/components/session";
import OrderEditor from "@/components/order-editor";
export default function Detail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { me } = useSession();
  const [order, setOrder] = useState<Order | null>(null),
    [error, setError] = useState(""),
    [edit, setEdit] = useState(false),
    [busy, setBusy] = useState(false),
    [notice, setNotice] = useState(""),
    [reload, setReload] = useState(0);
  useEffect(() => {
    let live = true;
    api
      .get<Order>(`/orders/${id}`)
      .then((r) => {
        if (live) {
          setError("");
          setOrder(r.data);
          setEdit(false);
          if (new URLSearchParams(window.location.search).has("saved")) {
            setNotice("Черновик сохранен. Проверь детали перед публикацией.");
            window.history.replaceState(null, "", `/orders/${id}`);
          }
        }
      })
      .catch((e) => {
        if (live) setError(errorText(e));
      });
    return () => {
      live = false;
    };
  }, [id, reload]);
  async function publish() {
    if (!order || busy) return;
    setBusy(true);
    setError("");
    try {
      const r = await api.post<Order>(`/orders/${id}/publish`, {
        version: order.version,
      });
      setOrder(r.data);
      setNotice(
        "Заказ опубликован. Теперь он доступен другим пользователям в поиске заказов.",
      );
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  if (!order)
    return (
      <div className="empty">
        <p role="status">{error || "Загружаем заказ…"}</p>
        <Link href="/">Вернуться к списку</Link>
      </div>
    );
  const own = me?.workspace_id === order.customer_workspace_id;
  return (
    <>
      <Link className="back" href="/">
        ← К списку заказов
      </Link>
      {notice && (
        <div role="status" className="success">
          {notice}
        </div>
      )}
      <div className="page-heading">
        <div>
          <span className={`badge ${order.status}`}>
            {order.status === "draft" ? "Черновик" : "Опубликован"}
          </span>
          <h1>{order.title}</h1>
          <p className="muted">
            Создан {new Date(order.created_at).toLocaleDateString("ru-RU")}
          </p>
        </div>
      </div>
      {error && (
        <div role="alert" className="error">
          {error}{" "}
          <button onClick={() => setReload(reload + 1)}>Обновить заказ</button>
        </div>
      )}
      {edit ? (
        <>
          <OrderEditor
            key={order.version}
            order={order}
            onSaved={(updated) => {
              setOrder(updated);
              setEdit(false);
              setNotice("Изменения сохранены");
            }}
          />
          <button
            className="back"
            onClick={() => {
              if (
                window.confirm(
                  "Закрыть редактирование? Несохраненные изменения будут потеряны.",
                )
              )
                setEdit(false);
            }}
          >
            Закрыть редактирование
          </button>
        </>
      ) : (
        <div className="detail-grid">
          <section className="panel">
            <h2>О задаче</h2>
            <p className="description">{order.description}</p>
          </section>
          <aside className="panel detail-side">
            <span className="muted">Бюджет за проект</span>
            <h2>
              {order.budget_minor ? money(order.budget_minor) : "Не указан"}
            </h2>
            {own && order.status === "draft" ? (
              <>
                <button
                  className="primary full"
                  disabled={busy}
                  onClick={publish}
                >
                  {busy ? "Публикуем…" : "Опубликовать заказ"}
                </button>
                <button
                  className="secondary full"
                  onClick={() => {
                    setNotice("");
                    setEdit(true);
                  }}
                >
                  Редактировать
                </button>
                <p className="small muted">
                  После публикации заказ появится в поиске. Редактирование
                  опубликованных заказов пока недоступно.
                </p>
              </>
            ) : (
              <p className="small muted">
                {own
                  ? "Заказ доступен исполнителям. Прием откликов появится на следующем этапе."
                  : "Пока можно ознакомиться с задачей. Возможность откликнуться появится на следующем этапе."}
              </p>
            )}
          </aside>
        </div>
      )}
    </>
  );
}
