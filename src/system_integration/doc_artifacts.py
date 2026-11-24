"""Automatic UI screenshot capture and draw.io -> SVG transition diagram generator."""

from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

CHROME_CANDIDATES = [
    Path(
        "/home/sweet/.cache/ms-playwright/chromium_headless_shell-1208/"
        "chrome-headless-shell-linux64/chrome-headless-shell"
    ),
    Path(
        "/home/sweet/.cache/puppeteer/chrome-headless-shell/"
        "linux-157.0.8103.50/chrome-headless-shell-linux64/chrome-headless-shell"
    ),
]


@dataclass(frozen=True)
class ScreenSpec:
    """Definition of a single UI endpoint to capture."""

    filename: str
    client_attr: str
    path: str
    title: str


@dataclass(frozen=True)
class TransitionEdge:
    """Directed transition between two screens in a project."""

    source_index: int
    target_index: int
    label: str
    route_lane: str = "straight"  # straight | top | bottom


@dataclass(frozen=True)
class ProjectDocSpec:
    """Capture and transition diagram specification for one project."""

    key: str
    title: str
    screens: tuple[ScreenSpec, ScreenSpec, ScreenSpec]
    edges: tuple[TransitionEdge, ...]


PROJECT_SPECS: tuple[ProjectDocSpec, ...] = (
    ProjectDocSpec(
        key="portal",
        title="店長・スタッフ共通ポータル 画面遷移図",
        screens=(
            ScreenSpec("01-portal-dashboard.png", "portal", "/ui/portal", "1. 統合ダッシュボード"),
            ScreenSpec(
                "02-portal-floor-operations.png",
                "portal",
                "/ui/portal/floor",
                "2. ホール＆キッチン現場",
            ),
            ScreenSpec(
                "03-portal-manager-console.png",
                "portal",
                "/ui/portal/manager",
                "3. 店長マネジメント",
            ),
        ),
        edges=(
            TransitionEdge(0, 1, "現場画面タブ", "straight"),
            TransitionEdge(1, 2, "店長画面タブ", "straight"),
            TransitionEdge(0, 2, "マネジメント確認", "top"),
            TransitionEdge(2, 0, "統合ビューへ戻る", "bottom"),
        ),
    ),
    ProjectDocSpec(
        key="product_management",
        title="商品管理 (product-management) 画面遷移図",
        screens=(
            ScreenSpec("01-product-list.png", "product", "/ui/products", "1. 商品マスタ一覧"),
            ScreenSpec(
                "02-product-register.png", "product", "/ui/products/new", "2. 新規商品登録"
            ),
            ScreenSpec(
                "03-product-detail.png", "product", "/ui/products/1", "3. 商品詳細・編集"
            ),
        ),
        edges=(
            TransitionEdge(0, 1, "＋新規商品を登録", "straight"),
            TransitionEdge(1, 0, "登録完了 (POST)", "bottom"),
            TransitionEdge(0, 2, "「編集」クリック", "top"),
            TransitionEdge(2, 0, "保存後一覧へ (PUT)", "bottom"),
        ),
    ),
    ProjectDocSpec(
        key="menu_management",
        title="メニュー管理 (menu-management) 画面遷移図",
        screens=(
            ScreenSpec("01-menu-list.png", "menu", "/ui/menus", "1. メニュー一覧・公開"),
            ScreenSpec(
                "02-menu-editor.png", "menu", "/ui/menus/editor", "2. ノーコード作成"
            ),
            ScreenSpec(
                "03-menu-preview.png", "menu", "/ui/menus/preview", "3. 端末別プレビュー"
            ),
        ),
        edges=(
            TransitionEdge(0, 1, "＋ノーコード作成", "straight"),
            TransitionEdge(1, 0, "公開作成 (POST)", "bottom"),
            TransitionEdge(0, 2, "プレビュー表示", "top"),
            TransitionEdge(2, 0, "一覧へ戻る", "bottom"),
        ),
    ),
    ProjectDocSpec(
        key="guest_management",
        title="顧客・座席管理 (guest-management) 画面遷移図",
        screens=(
            ScreenSpec("01-table-map.png", "guest", "/ui/tables", "1. 座席マップ"),
            ScreenSpec("02-table-checkin-qr.png", "guest", "/ui/checkin", "2. 来客受付・QR発行"),
            ScreenSpec("03-guest-loyalty.png", "guest", "/ui/guests", "3. 会員ポイント・清掃"),
        ),
        edges=(
            TransitionEdge(0, 1, "着席受付へ", "straight"),
            TransitionEdge(1, 0, "着席完了 (occupy)", "bottom"),
            TransitionEdge(0, 2, "清掃完了・会員管理", "top"),
            TransitionEdge(2, 0, "空席復帰 (release)", "bottom"),
        ),
    ),
    ProjectDocSpec(
        key="dine_in_ordering",
        title="店内注文 (dine-in-ordering) 画面遷移図",
        screens=(
            ScreenSpec(
                "01-qr-session.png", "dine_in", "/ui/dine-in/session", "1. 席QRセッション認証"
            ),
            ScreenSpec(
                "02-order-menu.png", "dine_in", "/ui/dine-in/menu", "2. 店内・席持帰注文"
            ),
            ScreenSpec(
                "03-order-status.png", "dine_in", "/ui/dine-in/status", "3. 注文・調理状況"
            ),
        ),
        edges=(
            TransitionEdge(0, 1, "QR認証成功 (/sessions)", "straight"),
            TransitionEdge(1, 2, "注文送信後の確認", "straight"),
            TransitionEdge(2, 1, "追加注文へ戻る", "bottom"),
        ),
    ),
    ProjectDocSpec(
        key="takeout_ordering",
        title="持ち帰り注文 (takeout-ordering) 画面遷移図",
        screens=(
            ScreenSpec(
                "01-sns-login.png", "takeout", "/ui/takeout/login", "1. SNS認証ログイン"
            ),
            ScreenSpec(
                "02-takeout-reserve.png", "takeout", "/ui/takeout/reserve", "2. メニュー・受取予約"
            ),
            ScreenSpec(
                "03-pickup-notification.png",
                "takeout",
                "/ui/takeout/status",
                "3. 注文状況・受取通知",
            ),
        ),
        edges=(
            TransitionEdge(0, 1, "SNSログイン (/auth)", "straight"),
            TransitionEdge(1, 2, "予約確定・状況確認", "straight"),
            TransitionEdge(2, 0, "アカウント切替", "top"),
        ),
    ),
    ProjectDocSpec(
        key="order_management",
        title="注文管理 (order-management) 画面遷移図",
        screens=(
            ScreenSpec(
                "01-order-kanban.png", "order", "/ui/orders/kanban", "1. 統合注文かんばん"
            ),
            ScreenSpec(
                "02-order-transition.png", "order", "/ui/orders/detail", "2. 注文詳細・進行"
            ),
            ScreenSpec(
                "03-table-bill.png", "order", "/ui/orders/bills", "3. 席別会計サマリー"
            ),
        ),
        edges=(
            TransitionEdge(0, 1, "注文カード選択", "straight"),
            TransitionEdge(1, 0, "かんばんへ戻る", "bottom"),
            TransitionEdge(0, 2, "会計金額タブ", "top"),
            TransitionEdge(2, 0, "かんばんボードへ", "bottom"),
        ),
    ),
    ProjectDocSpec(
        key="accounting_management",
        title="会計管理 (accounting-management) 画面遷移図",
        screens=(
            ScreenSpec(
                "01-checkout-bill.png", "accounting", "/ui/accounting/checkout", "1. 会計対象確認"
            ),
            ScreenSpec(
                "02-payment-method.png", "accounting", "/ui/accounting/payment", "2. レジ決済処理"
            ),
            ScreenSpec(
                "03-payment-receipt.png",
                "accounting",
                "/ui/accounting/receipt",
                "3. 領収書・決済履歴",
            ),
        ),
        edges=(
            TransitionEdge(0, 1, "「レジ決済へ」", "straight"),
            TransitionEdge(1, 2, "決済確定 (POST)", "straight"),
            TransitionEdge(0, 2, "会計済み領収書表示", "top"),
        ),
    ),
    ProjectDocSpec(
        key="sales_management",
        title="売上管理 (sales-management) 画面遷移図",
        screens=(
            ScreenSpec("01-daily-sales.png", "sales", "/ui/sales/daily", "1. 日次売上"),
            ScreenSpec("02-monthly-sales.png", "sales", "/ui/sales/monthly", "2. 月次・年次集計"),
            ScreenSpec("03-sales-records.png", "sales", "/ui/sales/records", "3. 売上計上明細"),
        ),
        edges=(
            TransitionEdge(0, 1, "月次・年次タブ", "straight"),
            TransitionEdge(1, 2, "明細一覧タブ", "straight"),
            TransitionEdge(0, 2, "計上レコード直参照", "top"),
        ),
    ),
)


def _find_chrome_binary() -> Path:
    for candidate in CHROME_CANDIDATES:
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate
    raise FileNotFoundError("Headless Chromium binary was not found in expected cache paths.")


def _import_pil_image() -> Any | None:
    try:
        from PIL import Image

        return Image
    except ImportError:
        uv_archive = Path("/home/sweet/.cache/uv/archive-v0")
        if uv_archive.exists():
            for pkg_dir in uv_archive.glob("*/lib/python3.12/site-packages"):
                if (pkg_dir / "PIL").exists():
                    sys.path.append(str(pkg_dir))
                    try:
                        from PIL import Image

                        return Image
                    except ImportError:
                        continue
            for direct_pil in uv_archive.glob("*/PIL"):
                parent = direct_pil.parent
                sys.path.append(str(parent))
                try:
                    from PIL import Image

                    return Image
                except ImportError:
                    continue
    return None


def _normalize_html_for_hash(html: str) -> str:
    """Strip volatile random IDs/timestamps so unchanged UI renders keep identical hashes."""
    normalized = re.sub(r"ord_[0-9a-f]{8,12}", "ord_STATIC", html)
    normalized = re.sub(r"pay_[0-9a-f]{8,12}", "pay_STATIC", normalized)
    normalized = re.sub(r"prod-[0-9a-f]{8}", "prod-STATIC", normalized)
    normalized = re.sub(r"cust-(?:google|facebook|line)-[0-9a-f]{8}", "cust-STATIC", normalized)
    normalized = re.sub(r"tok-[0-9a-f]{16}", "tok-STATIC", normalized)
    normalized = re.sub(r"RCP-\d{8}-[0-9A-F]{6}", "RCP-STATIC", normalized)
    normalized = re.sub(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "UUID-STATIC",
        normalized,
    )
    normalized = re.sub(r"[0-9a-f]{8}-[0-9a-f]{3,4}", "UUID-PREFIX", normalized)
    normalized = re.sub(r"(ID:|席:) [0-9a-f]{8}", r"\1 UUID8", normalized)
    normalized = re.sub(r'value="[A-Za-z0-9_-]{18,}"', 'value="TOKEN"', normalized)
    normalized = re.sub(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
        "TIMESTAMP-STATIC",
        normalized,
    )
    normalized = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "DATE-STATIC", normalized)
    normalized = re.sub(r"\b\d{4}-\d{2}\b", "MONTH-STATIC", normalized)
    normalized = re.sub(
        r"<code>[A-Za-z0-9_-]{10,}\.\.\.</code>", "<code>TOKEN...</code>", normalized
    )
    normalized = re.sub(r"<code>[A-Za-z0-9_-]{16,}</code>", "<code>TOKEN</code>", normalized)
    return normalized


def _hash_html(html: str) -> str:
    return hashlib.sha256(_normalize_html_for_hash(html).encode("utf-8")).hexdigest()


def _render_html_to_png(chrome_bin: Path, html: str, output_png: Path) -> None:
    output_png.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mrs_cap_") as tmpdir:
        tmp_path = Path(tmpdir)
        html_file = tmp_path / "page.html"
        profile_dir = tmp_path / "profile"
        html_file.write_text(html, encoding="utf-8")
        env = os.environ.copy()
        env["HOME"] = str(tmp_path)
        env["XDG_CONFIG_HOME"] = str(tmp_path)
        env["XDG_CACHE_HOME"] = str(tmp_path)
        cmd = [
            str(chrome_bin),
            "--no-sandbox",
            "--disable-gpu",
            f"--user-data-dir={profile_dir}",
            "--window-size=1280,800",
            "--hide-scrollbars",
            f"--screenshot={output_png}",
            html_file.as_uri(),
        ]
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
        if result.returncode != 0 or not output_png.exists() or output_png.stat().st_size == 0:
            raise RuntimeError(
                f"Chromium screenshot failed for {output_png.name}: {result.stderr}"
            )


def _thumbnail_base64(png_path: Path, width: int = 320, height: int = 200) -> str:
    pil_image = _import_pil_image()
    if pil_image is not None:
        with pil_image.open(png_path) as img:
            resized = img.resize((width, height), pil_image.Resampling.LANCZOS)
            buf = io.BytesIO()
            resized.save(buf, format="PNG", optimize=True)
            return base64.b64encode(buf.getvalue()).decode("ascii")
    return base64.b64encode(png_path.read_bytes()).decode("ascii")


def build_drawio_xml(spec: ProjectDocSpec, thumbnails_b64: list[str]) -> str:
    """Create a draw.io (.drawio) XML diagram containing scaled screen captures."""
    mxfile = ET.Element("mxfile", host="app.diagrams.net", type="device")
    diagram = ET.SubElement(mxfile, "diagram", id=f"diagram-{spec.key}", name="画面遷移図")
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        dx="1340",
        dy="470",
        grid="1",
        gridSize="10",
        guides="1",
        tooltips="1",
        connect="1",
        arrows="1",
        fold="1",
        page="1",
        pageScale="1",
        pageWidth="1340",
        pageHeight="470",
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    positions = [(45, 135), (510, 135), (975, 135)]
    node_w, node_h = 320, 200

    for idx, (screen, b64) in enumerate(zip(spec.screens, thumbnails_b64, strict=True)):
        x, y = positions[idx]
        node_id = f"screen-{idx + 1}"
        # draw.io uses comma without ';base64' inside style strings
        style = (
            "shape=image;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;"
            "verticalAlign=top;aspect=fixed;imageAspect=0;rounded=1;strokeColor=#cbd5e1;"
            f"image=data:image/png,{b64}"
        )
        cell = ET.SubElement(
            root,
            "mxCell",
            id=node_id,
            value=f"{screen.title} ({screen.path})",
            style=style,
            vertex="1",
            parent="1",
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            x=str(x),
            y=str(y),
            width=str(node_w),
            height=str(node_h),
            **{"as": "geometry"},
        )

    for e_idx, edge in enumerate(spec.edges, start=1):
        edge_id = f"edge-{e_idx}"
        edge_style = (
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;"
            "jettySize=auto;html=1;strokeColor=#ea580c;strokeWidth=2;fontColor=#0f172a;"
            f"routeLane={edge.route_lane};"
        )
        cell = ET.SubElement(
            root,
            "mxCell",
            id=edge_id,
            value=edge.label,
            style=edge_style,
            edge="1",
            parent="1",
            source=f"screen-{edge.source_index + 1}",
            target=f"screen-{edge.target_index + 1}",
        )
        ET.SubElement(cell, "mxGeometry", relative="1", **{"as": "geometry"})

    ET.indent(mxfile, space="  ")
    return ET.tostring(mxfile, encoding="unicode")


def convert_drawio_to_svg(drawio_xml: str, diagram_title: str) -> str:
    """Parse draw.io XML and render a clean SVG diagram embedding the thumbnail captures."""
    root = ET.fromstring(drawio_xml)
    model = root.find(".//mxGraphModel")
    if model is None:
        raise ValueError("Invalid draw.io XML: missing mxGraphModel")
    width = int(model.attrib.get("pageWidth", "1340"))
    height = int(model.attrib.get("pageHeight", "470"))

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    for cell in model.findall(".//mxCell"):
        if cell.attrib.get("vertex") == "1":
            geom = cell.find("mxGeometry")
            if geom is None:
                continue
            style = cell.attrib.get("style", "")
            img_data = ""
            m = re.search(r"image=data:image/png,([^;]+)", style)
            if m:
                img_data = m.group(1)
            nodes[cell.attrib["id"]] = {
                "id": cell.attrib["id"],
                "label": cell.attrib.get("value", ""),
                "x": float(geom.attrib.get("x", "0")),
                "y": float(geom.attrib.get("y", "0")),
                "w": float(geom.attrib.get("width", "320")),
                "h": float(geom.attrib.get("height", "200")),
                "b64": img_data,
            }
        elif cell.attrib.get("edge") == "1":
            style = cell.attrib.get("style", "")
            lane_m = re.search(r"routeLane=(\w+)", style)
            edges.append(
                {
                    "id": cell.attrib["id"],
                    "label": cell.attrib.get("value", ""),
                    "source": cell.attrib.get("source", ""),
                    "target": cell.attrib.get("target", ""),
                    "lane": lane_m.group(1) if lane_m else "straight",
                }
            )

    svg_parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "  <defs>",
        '    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#ea580c"/>',
        "    </marker>",
        '    <filter id="card-shadow" x="-5%" y="-5%" width="110%" height="115%">',
        '      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0f172a" '
        'flood-opacity="0.10"/>',
        "    </filter>",
        "  </defs>",
        f'  <rect width="{width}" height="{height}" rx="16" fill="#f8fafc" stroke="#e2e8f0"/>',
        '  <text x="45" y="34" font-family="Noto Sans CJK JP, sans-serif" '
        f'font-size="18" font-weight="700" fill="#0f172a">{escape(diagram_title)}</text>',
        '  <text x="45" y="54" font-family="Noto Sans CJK JP, sans-serif" '
        'font-size="12" fill="#64748b">縮小画面キャプチャによる画面遷移図 '
        "(draw.io ソースから自動生成)</text>",
    ]

    # Render edges
    top_offset = 0
    bottom_offset = 0
    for edge in edges:
        src = nodes.get(edge["source"])
        dst = nodes.get(edge["target"])
        if not src or not dst:
            continue
        lane = edge["lane"]
        if lane == "straight":
            y_mid = src["y"] + src["h"] / 2
            if src["x"] < dst["x"]:
                x1, x2 = src["x"] + src["w"] + 4, dst["x"] - 6
            else:
                x1, x2 = src["x"] - 4, dst["x"] + dst["w"] + 6
            path_d = f"M {x1:.0f} {y_mid:.0f} L {x2:.0f} {y_mid:.0f}"
            lx, ly = (x1 + x2) / 2, y_mid - 14
        elif lane == "top":
            lane_y = 86 - top_offset * 22
            top_offset += 1
            x1 = src["x"] + src["w"] * 0.55
            y1 = src["y"] - 22
            x2 = dst["x"] + dst["w"] * 0.45
            y2 = dst["y"] - 24
            path_d = (
                f"M {x1:.0f} {y1:.0f} L {x1:.0f} {lane_y:.0f} "
                f"L {x2:.0f} {lane_y:.0f} L {x2:.0f} {y2:.0f}"
            )
            lx, ly = (x1 + x2) / 2, lane_y - 4
        else:  # bottom
            lane_y = src["y"] + src["h"] + 58 + bottom_offset * 26
            bottom_offset += 1
            x1 = src["x"] + src["w"] * 0.45
            y1 = src["y"] + src["h"] + 30
            x2 = dst["x"] + dst["w"] * 0.55
            y2 = dst["y"] + dst["h"] + 32
            path_d = (
                f"M {x1:.0f} {y1:.0f} L {x1:.0f} {lane_y:.0f} "
                f"L {x2:.0f} {lane_y:.0f} L {x2:.0f} {y2:.0f}"
            )
            lx, ly = (x1 + x2) / 2, lane_y - 4

        svg_parts.append(
            f'  <path d="{path_d}" fill="none" stroke="#ea580c" stroke-width="2.2" '
            'marker-end="url(#arrow)"/>'
        )
        lbl = edge["label"]
        box_w = sum(11 if ord(ch) > 127 else 7 for ch in lbl) + 20
        svg_parts.append(
            f'  <rect x="{lx - box_w / 2:.0f}" y="{ly - 13:.0f}" width="{box_w}" '
            f'height="20" rx="10" fill="#fff7ed" stroke="#fdba74"/>'
        )
        svg_parts.append(
            f'  <text x="{lx:.0f}" y="{ly + 1:.0f}" text-anchor="middle" '
            f'font-family="Noto Sans CJK JP, sans-serif" font-size="11" font-weight="700" '
            f'fill="#9a3412">{escape(lbl)}</text>'
        )

    # Render thumbnail screen cards
    for node in nodes.values():
        x, y, w, h = node["x"], node["y"], node["w"], node["h"]
        svg_parts.append(
            f'  <g filter="url(#card-shadow)">'
            f'<rect x="{x:.0f}" y="{y - 20:.0f}" width="{w:.0f}" height="{h + 48:.0f}" '
            f'rx="10" fill="#ffffff" stroke="#cbd5e1"/>'
            f'<rect x="{x:.0f}" y="{y - 20:.0f}" width="{w:.0f}" height="20" '
            f'rx="10" fill="#0f172a"/>'
            f'<circle cx="{x + 12:.0f}" cy="{y - 10:.0f}" r="3" fill="#ef4444"/>'
            f'<circle cx="{x + 22:.0f}" cy="{y - 10:.0f}" r="3" fill="#f59e0b"/>'
            f'<circle cx="{x + 32:.0f}" cy="{y - 10:.0f}" r="3" fill="#22c55e"/>'
            f'<image x="{x + 1:.0f}" y="{y:.0f}" width="{w - 2:.0f}" height="{h:.0f}" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'xlink:href="data:image/png;base64,{node["b64"]}"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + h + 18:.0f}" text-anchor="middle" '
            f'font-family="Noto Sans CJK JP, sans-serif" font-size="12" font-weight="700" '
            f'fill="#0f172a">{escape(node["label"])}</text>'
            f"</g>"
        )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def capture_and_generate_docs(
    system: Any,
    docs_images_dir: Path,
    *,
    force: bool = False,
) -> dict[str, list[Path]]:
    """Capture screenshots of portal & 8 subsystems and generate .drawio/.svg diagrams.

    Only re-renders images and diagrams when UI HTML changes or target files are missing,
    unless ``force=True`` or ``FORCE_DOC_CAPTURE=1`` is set.
    """
    force_mode = force or os.getenv("FORCE_DOC_CAPTURE") == "1"
    chrome_bin = _find_chrome_binary()
    docs_images_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = docs_images_dir / ".capture-hashes.json"
    old_hashes: dict[str, str] = {}
    if manifest_path.exists():
        old_hashes = json.loads(manifest_path.read_text(encoding="utf-8"))
    new_hashes: dict[str, str] = dict(old_hashes)

    pending_renders: list[tuple[str, str, Path]] = []
    project_changed: dict[str, bool] = {}

    # 1. Fetch HTML from live TestClients and determine what changed
    for spec in PROJECT_SPECS:
        proj_dir = docs_images_dir / spec.key
        proj_dir.mkdir(parents=True, exist_ok=True)
        changed = force_mode
        for scr in spec.screens:
            client = getattr(system, scr.client_attr)
            target_path = scr.path
            if scr.path == "/ui/products/1":
                prod_list = client.get("/products")
                if prod_list.status_code == 200 and prod_list.json():
                    target_path = f"/ui/products/{prod_list.json()[0]['id']}"
            resp = client.get(target_path)
            if resp.status_code != 200:
                raise AssertionError(
                    f"UI screen {scr.client_attr}:{target_path} returned {resp.status_code}"
                )
            html_text = resp.text
            digest = _hash_html(html_text)
            rel_key = f"{spec.key}/{scr.filename}"
            out_png = proj_dir / scr.filename
            if force_mode or not out_png.exists() or old_hashes.get(rel_key) != digest:
                pending_renders.append((rel_key, html_text, out_png))
                new_hashes[rel_key] = digest
                changed = True
        drawio_path = proj_dir / "transition.drawio"
        svg_path = proj_dir / "transition.svg"
        if not drawio_path.exists() or not svg_path.exists():
            changed = True
        project_changed[spec.key] = changed

    # 2. Render changed screenshots in parallel
    if pending_renders:
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [
                pool.submit(_render_html_to_png, chrome_bin, html_text, out_png)
                for _, html_text, out_png in pending_renders
            ]
            for fut in futures:
                fut.result()

    # 3. Generate draw.io + SVG transition diagrams for updated projects
    generated: dict[str, list[Path]] = {}
    for spec in PROJECT_SPECS:
        proj_dir = docs_images_dir / spec.key
        png_paths = [proj_dir / s.filename for s in spec.screens]
        drawio_path = proj_dir / "transition.drawio"
        svg_path = proj_dir / "transition.svg"
        if project_changed[spec.key]:
            thumbs = [_thumbnail_base64(p) for p in png_paths]
            drawio_xml = build_drawio_xml(spec, thumbs)
            drawio_path.write_text(drawio_xml, encoding="utf-8")
            svg_xml = convert_drawio_to_svg(drawio_xml, spec.title)
            svg_path.write_text(svg_xml, encoding="utf-8")
        generated[spec.key] = [*png_paths, drawio_path, svg_path]

    manifest_path.write_text(
        json.dumps(new_hashes, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return generated
