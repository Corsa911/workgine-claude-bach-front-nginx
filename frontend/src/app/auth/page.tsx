"use client";
import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { ArrowUpRight, Eye, EyeOff } from "lucide-react";
import { api, errorText } from "@/lib/api";
export default function Auth() {
  const [login, setLogin] = useState(true),
    [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [show, setShow] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const router = useRouter();
  async function submit(e: FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      if (!login) await api.post("/auth/register", { email, password });
      const r = await api.post("/auth/login", { email, password });
      localStorage.setItem("access_token", r.data.access_token);
      router.replace("/");
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="auth-page">
      <section className="auth-story">
        <div className="brand">
          workgine<span>.</span>
        </div>
        <div>
          <p className="eyebrow">ЛЮДИ. ЗАДАЧИ. РЕЗУЛЬТАТ.</p>
          <h1>
            Хорошая работа
            <br />
            начинается
            <br />
            <em>с контакта.</em>
          </h1>
          <p>
            Находи исполнителей для своих идей.
            <br />И проекты, в которых пригодится твой опыт.
          </p>
        </div>
        <span className="story-footer">
          Один аккаунт для заказов и работы <ArrowUpRight size={20} />
        </span>
      </section>
      <section className="auth-form">
        <div>
          <p className="eyebrow">ТВОЕ РАБОЧЕЕ ПРОСТРАНСТВО</p>
          <h2>{login ? "С возвращением" : "Давай знакомиться"}</h2>
          <p className="muted">
            {login
              ? "Войди, чтобы продолжить работу."
              : "Создай аккаунт. Роль выберешь на следующем шаге."}
          </p>
          <form onSubmit={submit}>
            <label>
              Email
              <input
                autoComplete="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
              />
            </label>
            <label>
              Пароль
              <div className="password">
                <input
                  autoComplete={login ? "current-password" : "new-password"}
                  type={show ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  minLength={login ? 1 : 8}
                  maxLength={128}
                  required
                  placeholder={login ? "Введи пароль" : "Не менее 8 символов"}
                />
                <button
                  type="button"
                  className="icon-button"
                  aria-label={show ? "Скрыть пароль" : "Показать пароль"}
                  onClick={() => setShow(!show)}
                >
                  {show ? <EyeOff size={19} /> : <Eye size={19} />}
                </button>
              </div>
            </label>
            {error && (
              <p className="error" role="alert">
                {error}
              </p>
            )}
            <button className="primary full" disabled={busy}>
              {busy
                ? "Подождите…"
                : login
                  ? "Войти в кабинет"
                  : "Создать аккаунт"}
              <ArrowUpRight size={18} />
            </button>
          </form>
          <p className="auth-toggle">
            {login ? "Первый раз здесь?" : "Уже есть аккаунт?"}{" "}
            <button
              disabled={busy}
              onClick={() => {
                setLogin(!login);
                setError("");
              }}
            >
              {login ? "Зарегистрироваться" : "Войти"}
            </button>
          </p>
        </div>
      </section>
    </main>
  );
}
