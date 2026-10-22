import axios from "axios";
export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "/api/v1",
  timeout: 15000,
});
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      typeof window !== "undefined" &&
      error.response?.status === 401 &&
      !error.config?.url?.includes("/auth/login")
    ) {
      localStorage.removeItem("access_token");
      window.location.replace("/auth");
    }
    return Promise.reject(error);
  },
);
export function errorText(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.response?.status === 429)
      return "Слишком много попыток. Подождите несколько секунд и попробуйте снова.";
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail))
      return (
        "Проверьте заполнение полей: " +
        detail
          .map((item) => item.loc?.slice(1).join(".") || "данные")
          .join(", ")
      );
    if (!error.response)
      return "Не удалось связаться с сервером. Проверьте подключение и попробуйте еще раз.";
  }
  return "Не удалось выполнить действие. Попробуйте еще раз.";
}
export type Role = "customer" | "executor";
export type Me = {
  id: string;
  email: string;
  workspace_id: string;
  workspace_name: string;
  active_role: Role | null;
};
export type Category = { id: string; name: string };
export type Order = {
  id: string;
  title: string;
  description: string;
  category_id: string | null;
  budget_minor: number;
  currency: string;
  status: string;
  version: number;
  customer_workspace_id: string;
  created_at: string;
};
export const money = (amount: number) =>
  new Intl.NumberFormat("ru-KZ", {
    style: "currency",
    currency: "KZT",
    maximumFractionDigits: 2,
  }).format(amount / 100);
