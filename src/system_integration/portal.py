# ruff: noqa: E501
"""Shared staff & store-manager portal FastAPI application."""

from datetime import UTC, datetime
from html import escape
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

PORTAL_LINKS = [
    ("portal", "ポータル", "/ui/portal"),
    ("product", "商品管理", "/ui/products"),
    ("menu", "メニュー", "/ui/menus"),
    ("guest", "座席・顧客", "/ui/tables"),
    ("order", "注文かんばん", "/ui/orders/kanban"),
    ("accounting", "会計", "/ui/accounting/checkout"),
    ("sales", "売上", "/ui/sales/daily"),
    ("dine_in", "店内QR", "/ui/dine-in/session"),
    ("takeout", "持ち帰り", "/ui/takeout/login"),
]

SUBSYSTEM_CARDS = [
    ("product-management", "商品管理", "分類・価格・アレルギー・カロリー・持帰可否", "/ui/products", "📦"),
    ("menu-management", "メニュー管理", "店内・持ち帰りメニューのノーコード作成・公開", "/ui/menus", "📖"),
    ("guest-management", "顧客・座席管理", "来客受付・座席ステータス・QR・ポイント", "/ui/tables", "🪑"),
    ("order-management", "注文管理", "統合注文かんばん（受付→調理→提供）＆請求", "/ui/orders/kanban", "📋"),
    ("accounting-management", "会計管理", "現金/カード/QR決済・領収書・連携通知", "/ui/accounting/checkout", "💳"),
    ("sales-management", "売上管理", "日次・月次・年次の売上集計レポート", "/ui/sales/daily", "📈"),
    ("dine-in-ordering", "店内注文", "席QR認証・テーブル注文・席発持ち帰り", "/ui/dine-in/session", "📱"),
    ("takeout-ordering", "持ち帰り注文", "SNSログイン・事前予約・受取可能通知", "/ui/takeout/login", "🛍️"),
]


def _safe_json(client: Any, path: str, default: Any) -> Any:
    if client is None:
        return default
    try:
        res = client.get(path)
        if res.status_code == 200:
            return res.json()
    except Exception:
        return default
    return default


def _render_shell(*, title: str, subtitle: str, active_subtab: str, body_html: str) -> str:
    nav_html = "".join(
        f'<a class="nav-pill{" active" if key == "portal" else ""}" href="{href}">{escape(label)}</a>'
        for key, label, href in PORTAL_LINKS
    )
    subtabs = [
        ("dashboard", "統合ダッシュボード", "/ui/portal"),
        ("floor", "ホール＆キッチン現場", "/ui/portal/floor"),
        ("manager", "店長マネジメント", "/ui/portal/manager"),
    ]
    subtab_html = "".join(
        f'<a class="subtab{" active" if key == active_subtab else ""}" href="{href}">{escape(label)}</a>'
        for key, label, href in subtabs
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)} | まちなか飲食店サポート</title>
  <style>
    :root {{ --bg:#f8fafc; --surface:#fff; --navy:#0f172a; --slate:#334155; --muted:#64748b; --border:#e2e8f0; --accent:#ea580c; --accent-soft:#fff7ed; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--navy); line-height:1.5; font-family:"Noto Sans CJK JP","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif; }}
    .topbar {{ background:var(--navy); color:#fff; padding:0 24px; height:54px; display:flex; align-items:center; justify-content:space-between; gap:16px; }}
    .brand {{ display:flex; align-items:center; gap:10px; font-weight:700; font-size:15px; white-space:nowrap; }}
    .brand-badge {{ background:var(--accent); color:#fff; padding:2px 8px; border-radius:6px; font-size:11px; }}
    .nav-links {{ display:flex; gap:4px; overflow-x:auto; }}
    .nav-pill {{ color:#cbd5e1; text-decoration:none; font-size:12px; font-weight:600; padding:6px 10px; border-radius:6px; white-space:nowrap; }}
    .nav-pill.active {{ background:var(--accent); color:#fff; }}
    .subbar {{ background:var(--surface); border-bottom:1px solid var(--border); padding:12px 24px; display:flex; align-items:center; justify-content:space-between; gap:16px; }}
    .subbar h1 {{ margin:0; font-size:18px; }}
    .subbar .subtitle {{ margin:2px 0 0; font-size:12px; color:var(--muted); }}
    .subtabs {{ display:flex; gap:8px; }}
    .subtab {{ text-decoration:none; color:var(--slate); font-size:13px; font-weight:600; padding:7px 14px; border-radius:8px; border:1px solid var(--border); background:#fff; }}
    .subtab.active {{ background:var(--accent-soft); color:var(--accent); border-color:#fdba74; }}
    .container {{ max-width:1220px; margin:0 auto; padding:20px 24px 28px; }}
    .kpi-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:18px; }}
    .launcher-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }}
    .grid-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
    .grid-3 {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px; }}
    .card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:16px 18px; box-shadow:0 1px 2px rgba(15,23,42,.04); }}
    .app-tile {{ display:block; text-decoration:none; color:inherit; border:1px solid var(--border); border-radius:12px; padding:14px; background:#fff; }}
    .app-tile:hover {{ border-color:var(--accent); }}
    .kpi-label {{ font-size:12px; color:var(--muted); font-weight:600; }}
    .kpi-value {{ font-size:24px; font-weight:800; margin-top:4px; }}
    .kpi-sub {{ font-size:11px; color:var(--muted); margin-top:2px; }}
    .badge {{ display:inline-block; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:700; }}
    .badge-ok {{ background:#dcfce7; color:#166534; }}
    .badge-warn {{ background:#fef3c7; color:#92400e; }}
    .badge-info {{ background:#dbeafe; color:#1e40af; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th {{ text-align:left; padding:9px 10px; background:#f8fafc; color:var(--muted); font-size:12px; border-bottom:1px solid var(--border); }}
    td {{ padding:9px 10px; border-bottom:1px solid var(--border); }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <span>🍽️ まちなか飲食店サポート</span>
      <span class="brand-badge">店長・スタッフ共通ポータル</span>
    </div>
    <nav class="nav-links">{nav_html}</nav>
  </header>
  <section class="subbar">
    <div>
      <h1>{escape(title)}</h1>
      <p class="subtitle">{escape(subtitle)}</p>
    </div>
    <div class="subtabs">{subtab_html}</div>
  </section>
  <main class="container">{body_html}</main>
</body>
</html>
"""


def create_portal_app(
    *,
    product: Any = None,
    menu: Any = None,
    guest: Any = None,
    order: Any = None,
    dine_in: Any = None,
    takeout: Any = None,
    accounting: Any = None,
    sales: Any = None,
) -> FastAPI:
    """Create FastAPI app for the shared store manager & staff portal."""
    app = FastAPI(title="MachinakaRestaurantSupport Staff Portal", version="0.1.0")
    clients = {
        "product-management": product,
        "menu-management": menu,
        "guest-management": guest,
        "order-management": order,
        "accounting-management": accounting,
        "sales-management": sales,
        "dine-in-ordering": dine_in,
        "takeout-ordering": takeout,
    }

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "staff-portal"}

    @app.get("/ui/portal", response_class=HTMLResponse)
    def portal_dashboard() -> str:
        today = datetime.now(UTC).date().isoformat()
        month = today[:7]
        tables = _safe_json(guest, "/tables", [])
        orders = _safe_json(order, "/orders", [])
        products = _safe_json(product, "/products", [])
        monthly = _safe_json(sales, f"/sales/summary/monthly?month={month}", {})
        if not monthly.get("total_amount"):
            # Fallback to current UTC year if date spans day boundary
            monthly = _safe_json(sales, f"/sales/summary/yearly?year={today[:4]}", {})

        occ_count = sum(1 for t in tables if t.get("status") == "occupied")
        active_orders = sum(1 for o in orders if o.get("status") != "served")
        total_sales = int(monthly.get("total_amount", 0))

        tiles = []
        for svc_id, name, desc, href, icon in SUBSYSTEM_CARDS:
            c = clients.get(svc_id)
            h = _safe_json(c, "/health", {})
            ok = h.get("status") == "ok" or c is not None
            badge = (
                '<span class="badge badge-ok">稼働中</span>'
                if ok
                else '<span class="badge badge-warn">未接続</span>'
            )
            tiles.append(
                f'<a class="app-tile" href="{href}">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">'
                f'<span style="font-size:20px">{icon}</span>{badge}</div>'
                f'<div style="font-weight:700;font-size:14px;margin-bottom:4px">{escape(name)}</div>'
                f'<div style="font-size:12px;color:#64748b">{escape(desc)}</div>'
                f'<div style="font-size:11px;color:#ea580c;margin-top:8px;font-weight:700">{escape(svc_id)} →</div>'
                f"</a>"
            )

        body = f"""
        <div class="kpi-grid">
          <div class="card">
            <div class="kpi-label">累計・月間売上</div>
            <div class="kpi-value" style="color:#ea580c">¥{total_sales:,}</div>
            <div class="kpi-sub">決済件数: {int(monthly.get("order_count", 0))} 件</div>
          </div>
          <div class="card">
            <div class="kpi-label">稼働座席（着席中 / 全席）</div>
            <div class="kpi-value">{occ_count} / {len(tables)} 卓</div>
            <div class="kpi-sub">清掃待: {sum(1 for t in tables if t.get("status") == "cleaning")} 卓</div>
          </div>
          <div class="card">
            <div class="kpi-label">進行中注文（かんばん）</div>
            <div class="kpi-value">{active_orders} 件</div>
            <div class="kpi-sub">総受注数: {len(orders)} 件</div>
          </div>
          <div class="card">
            <div class="kpi-label">登録商品マスタ</div>
            <div class="kpi-value">{len(products)} 品</div>
            <div class="kpi-sub">8 サブシステム連携</div>
          </div>
        </div>
        <div class="card">
          <h2 style="margin:0 0 14px;font-size:16px">店舗業務ツール・クイックランチャー（全8サブシステム）</h2>
          <div class="launcher-grid">{"".join(tiles)}</div>
        </div>
        """
        return _render_shell(
            title="店長・スタッフ共通ポータル › 統合ダッシュボード",
            subtitle="店舗運営に必要な全8ツールの稼働状態・当日KPI・業務画面への導線を一元化します",
            active_subtab="dashboard",
            body_html=body,
        )

    @app.get("/ui/portal/floor", response_class=HTMLResponse)
    def portal_floor_operations() -> str:
        tables = _safe_json(guest, "/tables", [])
        orders = _safe_json(order, "/orders", [])

        seat_rows = "".join(
            f"<tr><td><strong>{escape(str(t.get('table_number', '-')))}</strong></td>"
            f"<td>{int(t.get('capacity', 0))}名</td>"
            f"<td><span class='badge badge-info'>{escape(str(t.get('status', '-')))}</span></td></tr>"
            for t in tables
        ) or '<tr><td colspan="3" style="color:#64748b">座席未登録</td></tr>'

        kanban_rows = "".join(
            f"<tr><td><code>{escape(str(o.get('order_id', '-'))[:12])}</code></td>"
            f"<td>{escape(str(o.get('source', '-')))}</td>"
            f"<td><span class='badge badge-warn'>{escape(str(o.get('status', '-')))}</span></td>"
            f"<td>¥{int(o.get('total_amount', 0)):,}</td></tr>"
            for o in orders
        ) or '<tr><td colspan="4" style="color:#64748b">注文なし</td></tr>'

        unpaid_rows = "".join(
            f"<tr><td><code>{escape(str(o.get('order_id', '-'))[:12])}</code></td>"
            f"<td>{escape(str(o.get('table_id') or o.get('customer_id') or '-'))}</td>"
            f"<td><strong>¥{int(o.get('total_amount', 0)):,}</strong></td>"
            f"<td>{'済' if o.get('paid') else '未会計'}</td></tr>"
            for o in orders
        ) or '<tr><td colspan="4" style="color:#64748b">会計待ちなし</td></tr>'

        body = f"""
        <div class="grid-3">
          <div class="card">
            <h2 style="margin:0 0 10px;font-size:15px">🪑 フロア座席状況</h2>
            <table><thead><tr><th>席</th><th>定員</th><th>状態</th></tr></thead><tbody>{seat_rows}</tbody></table>
          </div>
          <div class="card">
            <h2 style="margin:0 0 10px;font-size:15px">🍳 キッチン調理かんばん</h2>
            <table><thead><tr><th>注文</th><th>経路</th><th>状態</th><th>金額</th></tr></thead><tbody>{kanban_rows}</tbody></table>
          </div>
          <div class="card">
            <h2 style="margin:0 0 10px;font-size:15px">💳 会計ステータス</h2>
            <table><thead><tr><th>注文</th><th>対象</th><th>金額</th><th>精算</th></tr></thead><tbody>{unpaid_rows}</tbody></table>
          </div>
        </div>
        """
        return _render_shell(
            title="店長・スタッフ共通ポータル › ホール＆キッチン現場画面",
            subtitle="座席・調理進行・レジ会計の3領域を1画面で横断監視し、ホールとキッチンの連携を円滑にします",
            active_subtab="floor",
            body_html=body,
        )

    @app.get("/ui/portal/manager", response_class=HTMLResponse)
    def portal_manager_console() -> str:
        products = _safe_json(product, "/products", [])
        dine_menus = _safe_json(menu, "/menus/dine_in", [])
        take_menus = _safe_json(menu, "/menus/takeout", [])
        today = datetime.now(UTC).date().isoformat()
        yearly = _safe_json(sales, f"/sales/summary/yearly?year={today[:4]}", {})

        prod_rows = "".join(
            f"<tr><td><strong>{escape(str(p.get('name', '-')))}</strong></td>"
            f"<td>{escape(str(p.get('category', '-')))}</td>"
            f"<td>¥{int(p.get('price', 0)):,}</td>"
            f"<td>{'可' if p.get('takeout_available') else '不可'}</td></tr>"
            for p in products
        ) or '<tr><td colspan="4" style="color:#64748b">商品なし</td></tr>'

        menu_rows = "".join(
            f"<tr><td><strong>{escape(str(m.get('title', '-')))}</strong></td>"
            f"<td>{escape(str(m.get('channel', '-')))}</td>"
            f"<td><span class='badge badge-ok'>公開中</span></td></tr>"
            for m in [*dine_menus, *take_menus]
        ) or '<tr><td colspan="3" style="color:#64748b">公開メニューなし</td></tr>'

        by_ch = yearly.get("by_channel", {})
        body = f"""
        <div class="grid-2">
          <div class="card">
            <h2 style="margin:0 0 10px;font-size:16px">📦 商品マスタ登録状況</h2>
            <table><thead><tr><th>商品名</th><th>分類</th><th>価格</th><th>持帰</th></tr></thead><tbody>{prod_rows}</tbody></table>
          </div>
          <div class="card">
            <h2 style="margin:0 0 10px;font-size:16px">📖 公開中チャネル別メニュー</h2>
            <table><thead><tr><th>タイトル</th><th>チャネル</th><th>状態</th></tr></thead><tbody>{menu_rows}</tbody></table>
            <div style="margin-top:16px;padding:14px;background:#fff7ed;border-radius:10px;border:1px solid #fdba74">
              <div style="font-size:12px;color:#9a3412;font-weight:700">年間累計売上サマリー（{escape(today[:4])}年）</div>
              <div style="font-size:26px;font-weight:800;color:#ea580c;margin:4px 0">¥{int(yearly.get('total_amount', 0)):,}</div>
              <div style="font-size:12px;color:#475569">
                店内: ¥{int(by_ch.get('dine_in', 0)):,} ／ 持ち帰り: ¥{int(by_ch.get('takeout', 0)):,}
                （計 {int(yearly.get('order_count', 0))} 件）
              </div>
            </div>
          </div>
        </div>
        """
        return _render_shell(
            title="店長・スタッフ共通ポータル › 店長マネジメントコンソール",
            subtitle="商品マスタ・メニュー公開計画・チャネル別売上実績を統合管理する店長向けビューです",
            active_subtab="manager",
            body_html=body,
        )

    # Proxy routes so clicking any portal tab works seamlessly when browsing the portal app directly
    proxy_prefixes = [
        ("product-management", "/ui/products"),
        ("menu-management", "/ui/menus"),
        ("guest-management", "/ui/tables"),
        ("guest-management", "/ui/checkin"),
        ("guest-management", "/ui/guests"),
        ("order-management", "/ui/orders"),
        ("accounting-management", "/ui/accounting"),
        ("sales-management", "/ui/sales"),
        ("dine-in-ordering", "/ui/dine-in"),
        ("takeout-ordering", "/ui/takeout"),
    ]
    for svc_key, prefix in proxy_prefixes:
        def _make_proxy(service_name: str, base_prefix: str):
            def _proxy(subpath: str = "") -> HTMLResponse:
                target_client = clients.get(service_name)
                if target_client is None:
                    raise HTTPException(status_code=503, detail=f"{service_name} not connected")
                path = f"{base_prefix}/{subpath}".rstrip("/") if subpath else base_prefix
                resp = target_client.get(path)
                return HTMLResponse(content=resp.text, status_code=resp.status_code)

            return _proxy

        handler = _make_proxy(svc_key, prefix)
        app.add_api_route(prefix, handler, methods=["GET"], response_class=HTMLResponse)
        app.add_api_route(f"{prefix}/{{subpath:path}}", handler, methods=["GET"], response_class=HTMLResponse)

    return app
