"""Integration test harness connecting all 8 subsystem FastAPI apps in-process."""

from dataclasses import dataclass

import httpx
import pytest
from accounting_management.clients import (
    GuestClient as AccountingGuestClient,
)
from accounting_management.clients import (
    OrderClient as AccountingOrderClient,
)
from accounting_management.clients import (
    SalesClient as AccountingSalesClient,
)
from accounting_management.main import create_app as create_accounting_app
from dine_in_ordering.clients import (
    GuestClient as DineInGuestClient,
)
from dine_in_ordering.clients import (
    MenuClient as DineInMenuClient,
)
from dine_in_ordering.clients import (
    OrderClient as DineInOrderClient,
)
from dine_in_ordering.clients import (
    ProductClient as DineInProductClient,
)
from dine_in_ordering.main import create_app as create_dine_in_app
from fastapi import FastAPI
from fastapi.testclient import TestClient
from guest_management.main import create_app as create_guest_app
from menu_management.client import ProductClient as MenuProductClient
from menu_management.main import create_app as create_menu_app
from order_management.main import create_app as create_order_app
from product_management.main import create_app as create_product_app
from sales_management.main import create_app as create_sales_app
from takeout_ordering.clients import (
    MenuClient as TakeoutMenuClient,
)
from takeout_ordering.clients import (
    OrderClient as TakeoutOrderClient,
)
from takeout_ordering.clients import (
    ProductClient as TakeoutProductClient,
)
from takeout_ordering.main import create_app as create_takeout_app

from system_integration.portal import create_portal_app


class FastAPIBridgeTransport(httpx.BaseTransport):
    """Synchronous httpx transport that forwards requests to a FastAPI TestClient."""

    def __init__(self, app: FastAPI) -> None:
        self._client = TestClient(app)

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        resp = self._client.request(
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            content=request.content,
        )
        return httpx.Response(
            status_code=resp.status_code,
            headers=resp.headers,
            content=resp.content,
        )


@dataclass
class RestaurantSystem:
    """Bundle of TestClients for all 8 interconnected subsystems and the staff portal."""

    product: TestClient
    menu: TestClient
    guest: TestClient
    order: TestClient
    dine_in: TestClient
    takeout: TestClient
    accounting: TestClient
    sales: TestClient
    portal: TestClient


@pytest.fixture()
def restaurant_system() -> RestaurantSystem:
    """Spin up fresh in-memory instances of all 8 subsystems wired together."""
    product_app = create_product_app()
    guest_app = create_guest_app()
    order_app = create_order_app()
    sales_app = create_sales_app()

    menu_app = create_menu_app(
        product_client=MenuProductClient(
            base_url="http://product-management",
            transport=FastAPIBridgeTransport(product_app),
        )
    )
    dine_in_app = create_dine_in_app(
        guest_client=DineInGuestClient(
            base_url="http://guest-management",
            transport=FastAPIBridgeTransport(guest_app),
        ),
        menu_client=DineInMenuClient(
            base_url="http://menu-management",
            transport=FastAPIBridgeTransport(menu_app),
        ),
        order_client=DineInOrderClient(
            base_url="http://order-management",
            transport=FastAPIBridgeTransport(order_app),
        ),
        product_client=DineInProductClient(
            base_url="http://product-management",
            transport=FastAPIBridgeTransport(product_app),
        ),
    )
    takeout_app = create_takeout_app(
        menu_client=TakeoutMenuClient(
            base_url="http://menu-management",
            transport=FastAPIBridgeTransport(menu_app),
        ),
        order_client=TakeoutOrderClient(
            base_url="http://order-management",
            transport=FastAPIBridgeTransport(order_app),
        ),
        product_client=TakeoutProductClient(
            base_url="http://product-management",
            transport=FastAPIBridgeTransport(product_app),
        ),
    )
    accounting_app = create_accounting_app(
        order_client=AccountingOrderClient(
            base_url="http://order-management",
            transport=FastAPIBridgeTransport(order_app),
        ),
        guest_client=AccountingGuestClient(
            base_url="http://guest-management",
            transport=FastAPIBridgeTransport(guest_app),
        ),
        sales_client=AccountingSalesClient(
            base_url="http://sales-management",
            transport=FastAPIBridgeTransport(sales_app),
        ),
    )

    product_client = TestClient(product_app)
    menu_client = TestClient(menu_app)
    guest_client = TestClient(guest_app)
    order_client = TestClient(order_app)
    dine_in_client = TestClient(dine_in_app)
    takeout_client = TestClient(takeout_app)
    accounting_client = TestClient(accounting_app)
    sales_client = TestClient(sales_app)
    portal_app = create_portal_app(
        product=product_client,
        menu=menu_client,
        guest=guest_client,
        order=order_client,
        dine_in=dine_in_client,
        takeout=takeout_client,
        accounting=accounting_client,
        sales=sales_client,
    )

    return RestaurantSystem(
        product=product_client,
        menu=menu_client,
        guest=guest_client,
        order=order_client,
        dine_in=dine_in_client,
        takeout=takeout_client,
        accounting=accounting_client,
        sales=sales_client,
        portal=TestClient(portal_app),
    )
