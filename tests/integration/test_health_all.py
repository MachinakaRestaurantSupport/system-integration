"""Health check verification across all 8 subsystems."""

from conftest import RestaurantSystem


def test_all_subsystems_health(restaurant_system: RestaurantSystem) -> None:
    expected = [
        (restaurant_system.product, "product-management"),
        (restaurant_system.menu, "menu-management"),
        (restaurant_system.guest, "guest-management"),
        (restaurant_system.order, "order-management"),
        (restaurant_system.dine_in, "dine-in-ordering"),
        (restaurant_system.takeout, "takeout-ordering"),
        (restaurant_system.accounting, "accounting-management"),
        (restaurant_system.sales, "sales-management"),
    ]
    for client, service_name in expected:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok", "service": service_name}
