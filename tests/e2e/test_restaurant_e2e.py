"""End-to-end system tests covering full restaurant workflows."""

from conftest import RestaurantSystem


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
                {"name": "食事", "product_ids": [str(pasta["id"])]},
                {"name": "飲料", "product_ids": [str(coffee["id"])]},
            ],
        },
    )

    # 2. 座席・会員準備と来客受付
    table = restaurant_system.guest.post(
        "/tables", json={"table_number": "A-1", "capacity": 4}
    ).json()
    table_b = restaurant_system.guest.post(
        "/tables", json={"table_number": "A-2", "capacity": 2}
    ).json()
    guest = restaurant_system.guest.post(
        "/guests", json={"name": "佐藤花子", "email": "hanako@example.com"}
    ).json()
    occupied = restaurant_system.guest.post(
        f"/tables/{table['id']}/occupy", json={"party_size": 2}
    ).json()
    occupied_b = restaurant_system.guest.post(
        f"/tables/{table_b['id']}/occupy", json={"party_size": 1}
    ).json()

    # 3. 席QRでメニュー参照・注文（店内分 + 別席での店内発持ち帰り）
    assert len(restaurant_system.dine_in.get("/dine-in/menus").json()) == 1
    order_dine = restaurant_system.dine_in.post(
        "/dine-in/orders",
        json={
            "table_id": table["id"],
            "qr_token": occupied["qr_token"],
            "is_takeout_from_table": False,
            "items": [
                {
                    "product_id": str(pasta["id"]),
                    "product_name": pasta["name"],
                    "unit_price": pasta["price"],
                    "quantity": 1,
                }
            ],
        },
    ).json()
    order_souvenir = restaurant_system.dine_in.post(
        "/dine-in/orders",
        json={
            "table_id": table_b["id"],
            "qr_token": occupied_b["qr_token"],
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
    ).json()

    # 4. かんばん進行
    for oid in (order_dine["order_id"], order_souvenir["order_id"]):
        for st in ("preparing", "ready", "served"):
            res = restaurant_system.order.patch(f"/orders/{oid}/status", json={"status": st})
            assert res.status_code == 200

    # 5. 席A-1の請求合計確認 -> 会計完了
    bill = restaurant_system.order.get(f"/tables/{table['id']}/bill").json()
    assert bill["total_amount"] == 1200

    p1 = restaurant_system.accounting.post(
        "/payments",
        json={"order_id": order_dine["order_id"], "method": "card", "received_amount": 1200},
    )
    assert p1.status_code == 201
    p2 = restaurant_system.accounting.post(
        "/payments",
        json={"order_id": order_souvenir["order_id"], "method": "qr", "received_amount": 900},
    )
    assert p2.status_code == 201

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
