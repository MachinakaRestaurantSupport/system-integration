"""Integration tests covering integration points I-1 through I-6."""

from conftest import RestaurantSystem


def test_i5_product_to_menu_and_ordering_channels(restaurant_system: RestaurantSystem) -> None:
    """I-5: 商品登録 -> メニュー作成/公開 -> 店内・持ち帰りメニュー参照の連携確認."""
    dine_only = restaurant_system.product.post(
        "/products",
        json={
            "name": "特製ラーメン",
            "category": "麺類",
            "price": 980,
            "allergens": ["小麦"],
            "calories": 650,
            "prep_time_minutes": 10,
            "takeout_available": False,
        },
    )
    assert dine_only.status_code == 201
    dine_only_id = str(dine_only.json()["id"])

    takeout_ok = restaurant_system.product.post(
        "/products",
        json={
            "name": "唐揚げ弁当",
            "category": "弁当",
            "price": 850,
            "allergens": ["鶏肉"],
            "calories": 720,
            "prep_time_minutes": 12,
            "takeout_available": True,
        },
    )
    assert takeout_ok.status_code == 201
    takeout_ok_id = str(takeout_ok.json()["id"])

    # 持ち帰り不可商品を takeout メニューに含めると 422 になる
    bad_menu = restaurant_system.menu.post(
        "/menus",
        json={
            "channel": "takeout",
            "title": "NG持ち帰りメニュー",
            "categories": [{"name": "メイン", "product_ids": [dine_only_id]}],
        },
    )
    assert bad_menu.status_code == 422

    # 店内・持ち帰りそれぞれ公開メニューを作成
    dine_menu = restaurant_system.menu.post(
        "/menus",
        json={
            "channel": "dine_in",
            "title": "グランドメニュー",
            "categories": [{"name": "麺類", "product_ids": [dine_only_id]}],
        },
    )
    assert dine_menu.status_code == 201, dine_menu.text

    takeout_menu = restaurant_system.menu.post(
        "/menus",
        json={
            "channel": "takeout",
            "title": "テイクアウトメニュー",
            "categories": [{"name": "弁当", "product_ids": [takeout_ok_id]}],
        },
    )
    assert takeout_menu.status_code == 201

    assert len(restaurant_system.dine_in.get("/dine-in/menus").json()) == 1
    assert len(restaurant_system.takeout.get("/takeout/menus").json()) == 1


def test_i1_i2_i3_i4_i6_order_to_accounting_guest_sales(
    restaurant_system: RestaurantSystem,
) -> None:
    """I-1, I-2, I-3, I-4, I-6: 店内/持ち帰り注文 -> 決済 -> 席清掃 -> 売上計上の連携確認."""
    # 座席登録と来客受付 (I-6)
    table = restaurant_system.guest.post(
        "/tables", json={"table_number": "T-01", "capacity": 4}
    ).json()
    occupied = restaurant_system.guest.post(
        f"/tables/{table['id']}/occupy", json={"party_size": 2}
    ).json()
    assert occupied["status"] == "occupied"

    # I-1: 店内注文 -> 注文管理
    session_res = restaurant_system.dine_in.post(
        "/sessions",
        json={"table_id": table["id"], "qr_token": occupied["qr_token"]},
    )
    assert session_res.status_code == 200
    assert session_res.json()["valid"] is True

    dine_order_res = restaurant_system.dine_in.post(
        "/dine-in/orders",
        json={
            "table_id": table["id"],
            "qr_token": occupied["qr_token"],
            "is_takeout_from_table": False,
            "items": [
                {
                    "product_id": "p1",
                    "product_name": "特製ラーメン",
                    "unit_price": 980,
                    "quantity": 2,
                }
            ],
        },
    )
    assert dine_order_res.status_code == 201
    dine_order = dine_order_res.json()
    assert dine_order["total_amount"] == 1960

    # I-2: 持ち帰り注文 -> 注文管理
    login_res = restaurant_system.takeout.post(
        "/auth/login",
        json={"provider": "line", "oauth_token": "line-tok-1", "display_name": "山田"},
    )
    assert login_res.status_code == 200
    customer_id = login_res.json()["customer_id"]

    takeout_order_res = restaurant_system.takeout.post(
        "/takeout/orders",
        json={
            "customer_id": customer_id,
            "pickup_at": "2026-11-16T18:30:00+09:00",
            "items": [
                {
                    "product_id": "p2",
                    "product_name": "唐揚げ弁当",
                    "unit_price": 850,
                    "quantity": 1,
                }
            ],
        },
    )
    assert takeout_order_res.status_code == 201
    takeout_order = takeout_order_res.json()
    assert takeout_order["total_amount"] == 850

    # I-3 + I-6 + I-4: 店内注文の会計処理 -> 支払済み更新 + 席清掃要求 + 売上計上
    payment_res = restaurant_system.accounting.post(
        "/payments",
        json={"order_id": dine_order["order_id"], "method": "cash", "received_amount": 2000},
    )
    assert payment_res.status_code == 201, payment_res.text
    assert payment_res.json()["change_amount"] == 40

    # 注文管理側で paid=True になっていること
    assert restaurant_system.order.get(f"/orders/{dine_order['order_id']}").json()["paid"] is True
    # 顧客管理側で席が cleaning に遷移していること
    assert restaurant_system.guest.get(f"/tables/{table['id']}").json()["status"] == "cleaning"

    # 持ち帰り注文もカード決済
    payment_takeout = restaurant_system.accounting.post(
        "/payments",
        json={"order_id": takeout_order["order_id"], "method": "card", "received_amount": 850},
    )
    assert payment_takeout.status_code == 201, payment_takeout.text

    # 売上管理に2件とも計上されていること (I-4)
    paid_date = payment_res.json()["paid_at"][:10]
    daily = restaurant_system.sales.get(f"/sales/summary/daily?date={paid_date}")
    assert daily.status_code == 200
    summary = daily.json()
    assert summary["order_count"] == 2
    assert summary["total_amount"] == 2810
    assert summary["by_channel"] == {"dine_in": 1960, "takeout": 850}
