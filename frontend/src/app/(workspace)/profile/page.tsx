"use client";
import { useEffect, useState, FormEvent } from "react";
import { api, errorText } from "@/lib/api";
export default function Profile() {
  const [description, setDescription] = useState(""),
    [rate, setRate] = useState("0"),
    [baseline, setBaseline] = useState(""),
    [loading, setLoading] = useState(true),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [saved, setSaved] = useState(false);
  useEffect(() => {
    api
      .get("/profiles/me")
      .then((r) => {
        const d = r.data.description || "",
          v = String(r.data.hourly_rate_minor / 100);
        setDescription(d);
        setRate(v);
        setBaseline(JSON.stringify([d, v]));
      })
      .catch((e) => setError(errorText(e)))
      .finally(() => setLoading(false));
  }, []);
  const dirty = JSON.stringify([description, rate]) !== baseline;
  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      await api.put("/profiles/me", {
        description,
        hourly_rate_minor: Math.round(Number(rate) * 100),
      });
      setBaseline(JSON.stringify([description, rate]));
      setSaved(true);
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">ПРОФИЛЬ ИСПОЛНИТЕЛЯ</p>
          <h1>Расскажи о своем опыте</h1>
          <p className="muted">
            Начни с описания услуг и стоимости часа работы.
          </p>
        </div>
      </div>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {loading ? (
        <p>Загружаем профиль…</p>
      ) : (
        <form className="panel profile-form" onSubmit={submit}>
          <label>
            О тебе и твоих услугах
            <textarea
              rows={8}
              maxLength={10000}
              value={description}
              onChange={(e) => {
                setDescription(e.target.value);
                setSaved(false);
              }}
              placeholder="Какие задачи решаешь? В чем твой опыт и сильные стороны?"
            />
          </label>
          <label>
            Стоимость часа, ₸
            <input
              type="number"
              required
              min={0}
              max={20000000}
              step="0.01"
              value={rate}
              onChange={(e) => {
                setRate(e.target.value);
                setSaved(false);
              }}
            />
          </label>
          <div className="form-footer">
            <span role="status" className="muted">
              {saved
                ? "Изменения сохранены"
                : dirty
                  ? "Есть несохраненные изменения"
                  : "Изменений нет"}
            </span>
            <button className="primary" disabled={busy || !dirty}>
              {busy ? "Сохраняем…" : "Сохранить профиль"}
            </button>
          </div>
        </form>
      )}
    </>
  );
}
