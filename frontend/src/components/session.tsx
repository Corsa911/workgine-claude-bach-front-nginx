"use client";
import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeftRight,
  BriefcaseBusiness,
  LogOut,
  Search,
  UserRound,
  Plus,
  ArrowUpRight,
} from "lucide-react";
import { api, errorText, Me, Role } from "@/lib/api";
const Context = createContext<{ me: Me | null; reload: () => Promise<void> }>({
  me: null,
  reload: async () => {},
});
export const useSession = () => useContext(Context);
export function Shell({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const router = useRouter();
  const path = usePathname();
  const reload = useCallback(async () => {
    const r = await api.get<Me>("/auth/me");
    setMe(r.data);
  }, []);
  useEffect(() => {
    if (!localStorage.getItem("access_token")) {
      router.replace("/auth");
      return;
    }
    api
      .get<Me>("/auth/me")
      .then((r) => setMe(r.data))
      .catch((e) => setError(errorText(e)));
  }, [router]);
  async function changeRole(role: Role) {
    setBusy(true);
    setError("");
    try {
      const r = await api.patch<Me>("/auth/me/role", { active_role: role });
      setMe(r.data);
      router.push("/");
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  if (!me)
    return (
      <main className="loading">
        <div className="brand">
          workgine<span>.</span>
        </div>
        <p role="status">{error || "Открываем твой кабинет…"}</p>
        {error && (
          <button onClick={() => window.location.reload()}>Повторить</button>
        )}
      </main>
    );
  if (!me.active_role)
    return (
      <main className="onboarding">
        <div className="brand">
          workgine<span>.</span>
        </div>
        <p className="eyebrow">ОДИН АККАУНТ · ДВЕ ВОЗМОЖНОСТИ</p>
        <h1>С чего начнем?</h1>
        <p className="muted">
          Выбери свою первую роль. Переключиться можно в любой момент.
        </p>
        <div className="role-cards">
          <button disabled={busy} onClick={() => changeRole("customer")}>
            <BriefcaseBusiness size={30} />
            <h2>Заказать услугу</h2>
            <p>Опиши задачу и опубликуй заказ для исполнителей.</p>
            <span>
              Я заказчик <ArrowUpRight size={18} />
            </span>
          </button>
          <button disabled={busy} onClick={() => changeRole("executor")}>
            <Search size={30} />
            <h2>Найти работу</h2>
            <p>Расскажи о своем опыте и найди подходящий заказ.</p>
            <span>
              Я исполнитель <ArrowUpRight size={18} />
            </span>
          </button>
        </div>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
      </main>
    );
  const customer = me.active_role === "customer";
  return (
    <Context.Provider value={{ me, reload }}>
      <div className="app">
        <aside className="sidebar">
          <Link href="/" className="brand">
            workgine<span>.</span>
          </Link>
          <div className="workspace-label">ЛИЧНЫЙ КАБИНЕТ</div>
          <button
            className="role-switch"
            disabled={busy}
            onClick={() => changeRole(customer ? "executor" : "customer")}
            title="Переключить роль"
          >
            <span>
              <small>Сейчас ты</small>
              <strong>{customer ? "Заказчик" : "Исполнитель"}</strong>
            </span>
            <ArrowLeftRight size={18} />
          </button>
          <nav>
            <Link className={path === "/" ? "active" : ""} href="/">
              {customer ? (
                <BriefcaseBusiness size={19} />
              ) : (
                <Search size={19} />
              )}{" "}
              {customer ? "Мои заказы" : "Поиск заказов"}
            </Link>
            {customer ? (
              <Link
                className={path === "/orders/new" ? "active" : ""}
                href="/orders/new"
              >
                <Plus size={19} />
                Создать заказ
              </Link>
            ) : (
              <Link
                className={path === "/profile" ? "active" : ""}
                href="/profile"
              >
                <UserRound size={19} />
                Мой профиль
              </Link>
            )}
          </nav>
          <div className="sidebar-note">
            <span className="dot" /> Все начинается с задачи
            <p>
              {customer
                ? "Расскажи, какой результат тебе нужен."
                : "Твой следующий проект уже может быть здесь."}
            </p>
          </div>
          <div className="account">
            <span className="avatar">{me.email[0].toUpperCase()}</span>
            <span className="account-email">{me.email}</span>
            <button
              className="icon-button"
              aria-label="Выйти"
              onClick={() => {
                localStorage.removeItem("access_token");
                router.replace("/auth");
              }}
            >
              <LogOut size={18} />
            </button>
          </div>
        </aside>
        <div className="main-area">
          <header className="topbar">
            <span>
              Рабочее пространство <span className="slash">/</span>{" "}
              {customer ? "Заказчик" : "Исполнитель"}
            </span>
            <span className="topbar-hint">От идеи к результату</span>
          </header>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          <main className="content">{children}</main>
        </div>
      </div>
    </Context.Provider>
  );
}
