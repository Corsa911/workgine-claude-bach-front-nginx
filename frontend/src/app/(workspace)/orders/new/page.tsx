import Link from "next/link";
import OrderEditor from "@/components/order-editor";
export default function NewOrder() {
  return (
    <>
      <Link className="back" href="/">
        ← К заказам
      </Link>
      <div className="page-heading">
        <div>
          <p className="eyebrow">НОВАЯ ЗАДАЧА</p>
          <h1>Что нужно сделать?</h1>
          <p className="muted">
            Сначала сохрани черновик, затем проверь и опубликуй заказ.
          </p>
        </div>
      </div>
      <OrderEditor />
    </>
  );
}
