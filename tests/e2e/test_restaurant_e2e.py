"""End-to-end system tests covering full restaurant workflows."""

from pathlib import Path

from conftest import RestaurantSystem

from system_integration.doc_artifacts import PROJECT_SPECS, capture_and_generate_docs


def test_e2e_dine_in_full_lifecycle(restaurant_system: RestaurantSystem) -> None:
    """店内飲食E2E: 商品登録〜メニュー公開〜着席〜注文〜かんばん〜会計〜ポイント〜席再利用〜売上."""
    # 1. 商品登録・メニュー公開
    pasta = restaurant_system.product.post(
        "/products",
        json={
            "name": "ボロネーゼ",
            "category": "パスタ",
            "price": 1200,
            "allergens": ["小麦", "牛肉"],
            "calories": 780,
            "prep_time_minutes": 12,
            "takeout_available": True,
        },
    ).json()
    coffee = restaurant_system.product.post(
        "/products",
        json={
            "name": "ブレンドコーヒー",
            "category": "ドリンク",
            "price": 450,
            "takeout_available": True,
        },
    ).json()
    restaurant_system.menu.post(
        "/menus",
        json={
            "channel": "dine_in",
            "title": "ランチメニュー",
            "categories": [
                {"name": "食事", "product_ids": [pasta["id"]]},
                {"name": "飲料", "product_ids": [coffee["id"]]},
            ],
        },
    )

    # 2. 座席・会員準備と来客受付
    table = restaurant_system.guest.post(
        "/tables", json={"table_number": "A-1", "capacity": 4}
    ).json()
    guest = restaurant_system.guest.post(
        "/guests", json={"name": "佐藤花子", "email": "hanako@example.com"}
    ).json()
    occupied = restaurant_system.guest.post(
        f"/tables/{table['id']}/occupy", json={"party_size": 2}
    ).json()

    # 3. 席QRでメニュー参照・注文（同一席での店内分 + 店内発持ち帰り）
    assert len(restaurant_system.dine_in.get("/dine-in/menus").json()) == 1
    order_dine = restaurant_system.dine_in.post(
        "/dine-in/orders",
        json={
            "table_id": table["id"],
            "qr_token": occupied["qr_token"],
            "is_takeout_from_table": False,
            "items": [{"product_id": pasta["id"], "quantity": 1}],
        },
    ).json()
    order_souvenir = restaurant_system.dine_in.post(
        "/dine-in/orders",
        json={
            "table_id": table["id"],
            "qr_token": occupied["qr_token"],
            "is_takeout_from_table": True,
            "items": [{"product_id": coffee["id"], "quantity": 2}],
        },
    ).json()

    # 4. かんばん進行
    for oid in (order_dine["order_id"], order_souvenir["order_id"]):
        for st in ("preparing", "ready", "served"):
            res = restaurant_system.order.patch(f"/orders/{oid}/status", json={"status": st})
            assert res.status_code == 200

    # 5. 席A-1の請求合計確認 -> 分割会計（1回目: occupied維持、2回目: cleaning遷移）
    bill = restaurant_system.order.get(f"/tables/{table['id']}/bill").json()
    assert bill["total_amount"] == 2100

    p1 = restaurant_system.accounting.post(
        "/payments",
        json={"order_id": order_dine["order_id"], "method": "card", "received_amount": 1200},
    )
    assert p1.status_code == 201
    assert restaurant_system.guest.get(f"/tables/{table['id']}").json()["status"] == "occupied"

    p2 = restaurant_system.accounting.post(
        "/payments",
        json={"order_id": order_souvenir["order_id"], "method": "qr", "received_amount": 900},
    )
    assert p2.status_code == 201
    assert restaurant_system.guest.get(f"/tables/{table['id']}").json()["status"] == "cleaning"

    # 6. ポイント付与・席清掃完了で再利用可能へ
    pts = restaurant_system.guest.post(f"/guests/{guest['id']}/points", json={"delta": 21}).json()
    assert pts["points"] == 21

    released = restaurant_system.guest.post(f"/tables/{table['id']}/release").json()
    assert released["status"] == "available"

    # 7. 月次・年次売上確認
    paid_month = p1.json()["paid_at"][:7]
    paid_year = p1.json()["paid_at"][:4]
    monthly = restaurant_system.sales.get(f"/sales/summary/monthly?month={paid_month}").json()
    yearly = restaurant_system.sales.get(f"/sales/summary/yearly?year={paid_year}").json()
    assert monthly["total_amount"] == 2100
    assert yearly["order_count"] == 2


def test_e2e_takeout_full_lifecycle(restaurant_system: RestaurantSystem) -> None:
    """店外持ち帰りE2E: SNSログイン〜予約注文〜かんばん完了〜受取通知〜会計〜売上."""
    bento = restaurant_system.product.post(
        "/products",
        json={
            "name": "幕の内弁当",
            "category": "弁当",
            "price": 1100,
            "takeout_available": True,
        },
    ).json()
    restaurant_system.menu.post(
        "/menus",
        json={
            "channel": "takeout",
            "title": "お持ち帰り専用",
            "categories": [{"name": "弁当", "product_ids": [str(bento["id"])]}],
        },
    )

    login = restaurant_system.takeout.post(
        "/auth/login",
        json={"provider": "google", "oauth_token": "goog-123", "display_name": "鈴木一郎"},
    ).json()

    assert len(restaurant_system.takeout.get("/takeout/menus").json()) == 1

    order = restaurant_system.takeout.post(
        "/takeout/orders",
        json={
            "customer_id": login["customer_id"],
            "pickup_at": "2026-11-16T19:00:00+09:00",
            "items": [
                {
                    "product_id": str(bento["id"]),
                    "product_name": bento["name"],
                    "unit_price": bento["price"],
                    "quantity": 2,
                }
            ],
        },
    ).json()
    oid = order["order_id"]

    # 調理 -> 受取可能 -> 通知
    assert (
        restaurant_system.order.patch(
            f"/orders/{oid}/status", json={"status": "preparing"}
        ).status_code
        == 200
    )
    assert (
        restaurant_system.order.patch(f"/orders/{oid}/status", json={"status": "ready"}).status_code
        == 200
    )
    notify = restaurant_system.takeout.post(f"/takeout/orders/{oid}/notify-ready")
    assert notify.status_code == 200
    assert notify.json()["notified"] is True

    # 店頭受取時に決済
    payment = restaurant_system.accounting.post(
        "/payments",
        json={"order_id": oid, "method": "cash", "received_amount": 3000},
    )
    assert payment.status_code == 201
    assert payment.json()["change_amount"] == 800

    paid_date = payment.json()["paid_at"][:10]
    daily = restaurant_system.sales.get(f"/sales/summary/daily?date={paid_date}").json()
    assert daily["total_amount"] == 2200
    assert daily["by_channel"] == {"dine_in": 0, "takeout": 2200}


def test_e2e_zzz_capture_portal_and_subsystem_screens(
    restaurant_system: RestaurantSystem,
) -> None:
    """総合試験最終ステップ: 実データ投入状態でポータル・全画面を自動キャプチャ・遷移図更新."""
    # 1. 商品登録 (product-management)
    pasta = restaurant_system.product.post(
        "/products",
        json={
            "name": "ボロネーゼ",
            "category": "パスタ",
            "price": 1200,
            "allergens": ["小麦", "牛肉"],
            "calories": 780,
            "prep_time_minutes": 12,
            "options": ["大盛り", "粉チーズ増量"],
            "takeout_available": True,
        },
    ).json()
    coffee = restaurant_system.product.post(
        "/products",
        json={
            "name": "ブレンドコーヒー",
            "category": "ドリンク",
            "price": 450,
            "calories": 15,
            "prep_time_minutes": 4,
            "options": ["ホット", "アイス"],
            "takeout_available": True,
        },
    ).json()
    steak = restaurant_system.product.post(
        "/products",
        json={
            "name": "特製鉄板ハンバーグ",
            "category": "メイン",
            "price": 1480,
            "allergens": ["牛肉", "卵", "乳"],
            "calories": 860,
            "prep_time_minutes": 15,
            "options": ["デミグラス", "おろしポン酢"],
            "takeout_available": False,
        },
    ).json()
    bento = restaurant_system.product.post(
        "/products",
        json={
            "name": "幕の内弁当",
            "category": "弁当",
            "price": 1100,
            "allergens": ["小麦", "卵", "大豆"],
            "calories": 720,
            "prep_time_minutes": 10,
            "options": ["ごはん大盛"],
            "takeout_available": True,
        },
    ).json()

    # 2. メニュー構成・公開 (menu-management)
    restaurant_system.menu.post(
        "/menus",
        json={
            "channel": "dine_in",
            "title": "ランチ・グランドメニュー",
            "categories": [
                {"name": "食事", "product_ids": [str(pasta["id"]), str(steak["id"])]},
                {"name": "ドリンク", "product_ids": [str(coffee["id"])]},
            ],
        },
    )
    restaurant_system.menu.post(
        "/menus",
        json={
            "channel": "takeout",
            "title": "お持ち帰り専用メニュー",
            "categories": [
                {"name": "お弁当", "product_ids": [str(bento["id"])]},
                {"name": "ドリンク", "product_ids": [str(coffee["id"])]},
            ],
        },
    )

    # 3. 座席・会員準備と来客受付 (guest-management)
    t_a1 = restaurant_system.guest.post(
        "/tables", json={"table_number": "A-1", "capacity": 4}
    ).json()
    t_a2 = restaurant_system.guest.post(
        "/tables", json={"table_number": "A-2", "capacity": 2}
    ).json()
    restaurant_system.guest.post("/tables", json={"table_number": "B-1", "capacity": 4})
    occ_a1 = restaurant_system.guest.post(
        f"/tables/{t_a1['id']}/occupy", json={"party_size": 2}
    ).json()
    occ_a2 = restaurant_system.guest.post(
        f"/tables/{t_a2['id']}/occupy", json={"party_size": 2}
    ).json()
    g1 = restaurant_system.guest.post(
        "/guests", json={"name": "佐藤花子", "email": "hanako@example.com"}
    ).json()
    g2 = restaurant_system.guest.post(
        "/guests", json={"name": "山田太郎", "email": "taro@example.com"}
    ).json()
    restaurant_system.guest.post(f"/guests/{g1['id']}/points", json={"delta": 32})
    restaurant_system.guest.post(f"/guests/{g2['id']}/points", json={"delta": 15})

    # 4. 店内注文 + 店外持ち帰り注文 (dine-in / takeout)
    ord_served = restaurant_system.dine_in.post(
        "/dine-in/orders",
        json={
            "table_id": t_a1["id"],
            "qr_token": occ_a1["qr_token"],
            "is_takeout_from_table": False,
            "items": [
                {
                    "product_id": str(pasta["id"]),
                    "product_name": pasta["name"],
                    "unit_price": pasta["price"],
                    "quantity": 1,
                },
                {
                    "product_id": str(coffee["id"]),
                    "product_name": coffee["name"],
                    "unit_price": coffee["price"],
                    "quantity": 1,
                },
            ],
        },
    ).json()
    ord_preparing = restaurant_system.dine_in.post(
        "/dine-in/orders",
        json={
            "table_id": t_a2["id"],
            "qr_token": occ_a2["qr_token"],
            "is_takeout_from_table": False,
            "items": [
                {
                    "product_id": str(steak["id"]),
                    "product_name": steak["name"],
                    "unit_price": steak["price"],
                    "quantity": 1,
                }
            ],
        },
    ).json()
    restaurant_system.dine_in.post(
        "/dine-in/orders",
        json={
            "table_id": t_a2["id"],
            "qr_token": occ_a2["qr_token"],
            "is_takeout_from_table": True,
            "items": [
                {
                    "product_id": str(coffee["id"]),
                    "product_name": coffee["name"],
                    "unit_price": coffee["price"],
                    "quantity": 2,
                }
            ],
        },
    )

    login = restaurant_system.takeout.post(
        "/auth/login",
        json={"provider": "google", "oauth_token": "goog-demo", "display_name": "鈴木一郎"},
    ).json()
    restaurant_system.takeout.post(
        "/auth/login",
        json={"provider": "line", "oauth_token": "line-demo", "display_name": "高橋美咲"},
    )
    ord_takeout = restaurant_system.takeout.post(
        "/takeout/orders",
        json={
            "customer_id": login["customer_id"],
            "pickup_at": "2026-11-18T19:00:00+09:00",
            "items": [
                {
                    "product_id": str(bento["id"]),
                    "product_name": bento["name"],
                    "unit_price": bento["price"],
                    "quantity": 2,
                }
            ],
        },
    ).json()

    # 5. かんばん進行: received / preparing / ready / served 全列に注文が存在する状態へ
    for st in ("preparing", "ready", "served"):
        restaurant_system.order.patch(
            f"/orders/{ord_served['order_id']}/status", json={"status": st}
        )
    restaurant_system.order.patch(
        f"/orders/{ord_preparing['order_id']}/status", json={"status": "preparing"}
    )
    for st in ("preparing", "ready"):
        restaurant_system.order.patch(
            f"/orders/{ord_takeout['order_id']}/status", json={"status": st}
        )
    restaurant_system.takeout.post(f"/takeout/orders/{ord_takeout['order_id']}/notify-ready")

    # 6. 会計決済 (accounting-management) -> A-1 が cleaning になり、売上も計上される
    p1 = restaurant_system.accounting.post(
        "/payments",
        json={"order_id": ord_served["order_id"], "method": "card", "received_amount": 1650},
    )
    assert p1.status_code == 201
    p2 = restaurant_system.accounting.post(
        "/payments",
        json={"order_id": ord_takeout["order_id"], "method": "cash", "received_amount": 3000},
    )
    assert p2.status_code == 201

    # 7. ポータルおよび全8サブシステム画面をキャプチャし、draw.io + SVG 遷移図を自動更新
    docs_images_dir = Path(__file__).resolve().parents[2] / "docs" / "images"
    generated = capture_and_generate_docs(restaurant_system, docs_images_dir)

    assert len(generated) == len(PROJECT_SPECS)
    for spec in PROJECT_SPECS:
        paths = generated[spec.key]
        assert len(paths) == 5  # 3 PNGs + transition.drawio + transition.svg
        for p in paths:
            assert p.exists() and p.stat().st_size > 0
        assert "<mxfile" in paths[3].read_text(encoding="utf-8")
        svg_text = paths[4].read_text(encoding="utf-8")
        assert "<svg" in svg_text and "data:image/png;base64," in svg_text
