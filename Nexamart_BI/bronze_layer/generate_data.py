"""
BusinessIntelligence.ai
NexaMart Synthetic Data Generator

Generates:
    1. sales.csv
    2. marketing.csv
    3. inventory.csv
    4. products.csv
    5. regions.csv
    6. customers.csv

Business scenarios:
    1. P001 inventory availability shock
    2. Paid Social marketing efficiency decline
    3. North region revenue decline
    4. P999 sparse-history new product
    5. Conflicting / ambiguous evidence

Date range:
    2026-01-01 -> 2026-08-15
"""

import os
import random

import numpy as np
import pandas as pd


# ============================================================
# 1. CONFIGURATION
# ============================================================

SEED = 42

random.seed(SEED)
np.random.seed(SEED)

START_DATE = "2026-01-01"
END_DATE = "2026-08-15"

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "raw"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 2. BUSINESS EVENTS
# ============================================================

# Event 1 — P001 Inventory Shock
P001_SHOCK_START = pd.Timestamp("2026-05-15")
P001_SHOCK_END = pd.Timestamp("2026-05-28")

# Event 2 — Paid Social Efficiency Decline
MARKETING_EVENT_START = pd.Timestamp("2026-06-10")
MARKETING_EVENT_END = pd.Timestamp("2026-06-24")

# Event 3 — North Revenue Decline
NORTH_EVENT_START = pd.Timestamp("2026-07-05")
NORTH_EVENT_END = pd.Timestamp("2026-07-19")

# Event 5 — Conflicting Evidence
CONFLICT_EVENT_START = pd.Timestamp("2026-07-25")
CONFLICT_EVENT_END = pd.Timestamp("2026-07-31")

# Event 4 — P999 Launch
P999_LAUNCH_DATE = pd.Timestamp("2026-08-01")


# ============================================================
# 3. MASTER CONFIGURATION
# ============================================================

REGIONS = {
    "R01": "North",
    "R02": "South",
    "R03": "East",
    "R04": "West",
    "R05": "Central",
}

CUSTOMER_SEGMENTS = [
    "Premium",
    "Regular",
    "Budget",
    "Enterprise",
]

SALES_CHANNELS = [
    "Online",
    "Mobile App",
    "Marketplace",
    "Store",
]

MARKETING_CHANNELS = [
    "Paid Search",
    "Paid Social",
    "Email",
    "Display",
    "Affiliate",
]

CATEGORIES = [
    "Electronics",
    "Home Appliances",
    "Fashion",
    "Beauty",
    "Sports",
    "Grocery",
]

REGION_WEIGHTS = {
    "North": 0.23,
    "South": 0.22,
    "East": 0.19,
    "West": 0.20,
    "Central": 0.16,
}

SEGMENT_WEIGHTS = {
    "Premium": 0.15,
    "Regular": 0.50,
    "Budget": 0.25,
    "Enterprise": 0.10,
}

CHANNEL_WEIGHTS = {
    "Online": 0.40,
    "Mobile App": 0.25,
    "Marketplace": 0.25,
    "Store": 0.10,
}

CATEGORY_PRICE_RANGES = {
    "Electronics": (8000, 75000),
    "Home Appliances": (2500, 45000),
    "Fashion": (500, 8000),
    "Beauty": (300, 6000),
    "Sports": (800, 12000),
    "Grocery": (100, 3000),
}


# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================

def is_between(date, start, end):
    """Return True if date is between start and end inclusive."""
    return start <= date <= end


def weekday_factor(date):
    """Slightly higher demand on weekends."""
    if date.weekday() >= 5:
        return 1.15

    return 1.0


def seasonal_factor(date):
    """Mild monthly seasonality."""
    month_factor = {
        1: 0.92,
        2: 0.95,
        3: 1.00,
        4: 1.02,
        5: 1.05,
        6: 1.08,
        7: 1.04,
        8: 1.10,
    }

    return month_factor.get(date.month, 1.0)


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


# ============================================================
# 5. GENERATE PRODUCTS
# ============================================================

def generate_products():

    rows = []

    product_ids = [
        f"P{i:03d}"
        for i in range(1, 51)
    ]

    product_name_prefix = {
        "Electronics": [
            "NexaPhone",
            "NexaTab",
            "NexaBuds",
            "NexaWatch",
            "NexaCam",
        ],
        "Home Appliances": [
            "NexaCool",
            "NexaWash",
            "NexaMix",
            "NexaHeat",
            "NexaClean",
        ],
        "Fashion": [
            "NexaWear",
            "NexaStyle",
            "NexaFit",
            "NexaDenim",
            "NexaClassic",
        ],
        "Beauty": [
            "NexaGlow",
            "NexaCare",
            "NexaSkin",
            "NexaPure",
            "NexaBeauty",
        ],
        "Sports": [
            "NexaRun",
            "NexaSport",
            "NexaFitPro",
            "NexaActive",
            "NexaGear",
        ],
        "Grocery": [
            "NexaFresh",
            "NexaDaily",
            "NexaChoice",
            "NexaOrganic",
            "NexaFood",
        ],
    }

    for idx, product_id in enumerate(product_ids):

        category = random.choice(CATEGORIES)

        low, high = CATEGORY_PRICE_RANGES[category]

        price = round(
            np.random.uniform(
                low,
                high
            ),
            2
        )

        prefixes = product_name_prefix[category]

        prefix = prefixes[
            idx % len(prefixes)
        ]

        product_name = (
            f"{prefix} {idx + 1}"
        )

        rows.append({
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "price": price,
        })

    # Event 4 — New product
    rows.append({
        "product_id": "P999",
        "product_name": "NexaAI Pro",
        "category": "Electronics",
        "price": 54999.00,
    })

    return pd.DataFrame(rows)


# ============================================================
# 6. GENERATE REGIONS
# ============================================================

def generate_regions():

    return pd.DataFrame([
        {
            "region_id": region_id,
            "region_name": region_name,
        }
        for region_id, region_name in REGIONS.items()
    ])


# ============================================================
# 7. GENERATE CUSTOMERS
# ============================================================

def generate_customers(
    n_customers=5000
):

    rows = []

    segments = list(
        SEGMENT_WEIGHTS.keys()
    )

    probabilities = list(
        SEGMENT_WEIGHTS.values()
    )

    for i in range(
        1,
        n_customers + 1
    ):

        segment = np.random.choice(
            segments,
            p=probabilities
        )

        rows.append({
            "customer_id": f"CUST{i:05d}",
            "customer_segment": segment,
        })

    return pd.DataFrame(rows)


# ============================================================
# 8. GENERATE INVENTORY
# ============================================================

def generate_inventory(
    products_df,
    dates
):

    rows = []

    # P999 is generated separately after launch.
    active_products = products_df[
        products_df["product_id"] != "P999"
    ].copy()

    for date in dates:

        for _, product in active_products.iterrows():

            product_id = product["product_id"]

            for region_name in REGIONS.values():

                # ------------------------------------------------
                # Base stock
                # ------------------------------------------------

                base_stock = np.random.randint(
                    300,
                    1200
                )

                category = product["category"]

                if category == "Electronics":
                    base_stock *= 0.75

                elif category == "Grocery":
                    base_stock *= 1.25

                base_stock *= seasonal_factor(
                    date
                )

                stock_available = max(
                    0,
                    int(
                        np.random.normal(
                            base_stock,
                            base_stock * 0.10
                        )
                    )
                )

                # ------------------------------------------------
                # Normal stockout behavior
                # ------------------------------------------------

                stockout_hours = (
                    np.random.beta(
                        1.5,
                        18
                    ) * 5
                )

                # =================================================
                # EVENT 1 — P001 INVENTORY SHOCK
                # =================================================

                if (
                    product_id == "P001"
                    and is_between(
                        date,
                        P001_SHOCK_START,
                        P001_SHOCK_END
                    )
                ):

                    stockout_hours = np.random.uniform(
                        12.5,
                        15.0
                    )

                    stock_available = int(
                        stock_available
                        * np.random.uniform(
                            0.30,
                            0.45
                        )
                    )

                # =================================================
                # EVENT 5 — CONFLICTING EVIDENCE
                #
                # P002 and P003 experience a MODERATE inventory
                # deterioration during July 25–31.
                #
                # This is deliberately much weaker than Event 1.
                # =================================================

                if (
                    product_id in [
                        "P002",
                        "P003"
                    ]
                    and is_between(
                        date,
                        CONFLICT_EVENT_START,
                        CONFLICT_EVENT_END
                    )
                ):

                    stockout_hours = np.random.uniform(
                        4.5,
                        7.0
                    )

                    stock_available = int(
                        stock_available
                        * np.random.uniform(
                            0.70,
                            0.85
                        )
                    )

                # ------------------------------------------------
                # Keep stockout hours valid
                # ------------------------------------------------

                stockout_hours = clamp(
                    stockout_hours,
                    0,
                    24
                )

                # ------------------------------------------------
                # Lead time
                # ------------------------------------------------

                lead_time = int(
                    np.random.choice(
                        [2, 3, 4, 5, 6, 7],
                        p=[
                            0.10,
                            0.20,
                            0.25,
                            0.20,
                            0.15,
                            0.10,
                        ]
                    )
                )

                rows.append({
                    "date": date.strftime(
                        "%Y-%m-%d"
                    ),
                    "product_id": product_id,
                    "region": region_name,
                    "stock_available": stock_available,
                    "stockout_hours": round(
                        stockout_hours,
                        2
                    ),
                    "lead_time": lead_time,
                })

        # ========================================================
        # EVENT 4 — P999 LAUNCH
        # ========================================================

        if date >= P999_LAUNCH_DATE:

            for region_name in REGIONS.values():

                stock_available = np.random.randint(
                    150,
                    450
                )

                stockout_hours = np.random.uniform(
                    0,
                    2
                )

                lead_time = np.random.choice(
                    [4, 5, 6]
                )

                rows.append({
                    "date": date.strftime(
                        "%Y-%m-%d"
                    ),
                    "product_id": "P999",
                    "region": region_name,
                    "stock_available": stock_available,
                    "stockout_hours": round(
                        stockout_hours,
                        2
                    ),
                    "lead_time": lead_time,
                })

    return pd.DataFrame(rows)


# ============================================================
# 9. GENERATE MARKETING
# ============================================================

def generate_marketing(dates):

    rows = []

    # 44 campaigns × 227 days = 9,988 rows.
    campaign_ids = [
        f"CAM{i:03d}"
        for i in range(1, 45)
    ]

    campaign_channel_map = {}

    for campaign_id in campaign_ids:

        campaign_channel_map[
            campaign_id
        ] = random.choice(
            MARKETING_CHANNELS
        )

    for date in dates:

        for campaign_id in campaign_ids:

            channel = campaign_channel_map[
                campaign_id
            ]

            # ------------------------------------------------
            # Base spend by channel
            # ------------------------------------------------

            base_spend = {
                "Paid Search": 55000,
                "Paid Social": 65000,
                "Email": 18000,
                "Display": 35000,
                "Affiliate": 25000,
            }[channel]

            spend = np.random.normal(
                base_spend,
                base_spend * 0.12
            )

            spend = max(
                5000,
                spend
            )

            # ------------------------------------------------
            # Impressions
            # ------------------------------------------------

            impressions_per_rupee = {
                "Paid Search": 3.5,
                "Paid Social": 4.5,
                "Email": 7.0,
                "Display": 5.0,
                "Affiliate": 4.0,
            }[channel]

            impressions = int(
                spend
                * impressions_per_rupee
                * np.random.uniform(
                    0.85,
                    1.15
                )
            )

            # ------------------------------------------------
            # CTR
            # ------------------------------------------------

            ctr = {
                "Paid Search": 0.055,
                "Paid Social": 0.042,
                "Email": 0.080,
                "Display": 0.025,
                "Affiliate": 0.035,
            }[channel]

            ctr *= np.random.uniform(
                0.90,
                1.10
            )

            clicks = int(
                impressions * ctr
            )

            # ------------------------------------------------
            # Conversion rate
            # ------------------------------------------------

            conversion_rate = {
                "Paid Search": 0.075,
                "Paid Social": 0.060,
                "Email": 0.100,
                "Display": 0.035,
                "Affiliate": 0.055,
            }[channel]

            # =================================================
            # EVENT 2 — PAID SOCIAL EFFICIENCY DECLINE
            # =================================================

            if (
                channel == "Paid Social"
                and is_between(
                    date,
                    MARKETING_EVENT_START,
                    MARKETING_EVENT_END
                )
            ):

                spend *= np.random.uniform(
                    1.25,
                    1.35
                )

                impressions = int(
                    impressions
                    * np.random.uniform(
                        1.20,
                        1.35
                    )
                )

                clicks = int(
                    impressions
                    * ctr
                    * np.random.uniform(
                        1.00,
                        1.10
                    )
                )

                conversion_rate *= np.random.uniform(
                    0.60,
                    0.68
                )

            # =================================================
            # EVENT 5 — CONFLICTING EVIDENCE
            #
            # Paid Search and Email experience a MODERATE
            # efficiency decline.
            #
            # This is deliberately weaker than Event 2.
            # =================================================

            if (
                channel in [
                    "Paid Search",
                    "Email"
                ]
                and is_between(
                    date,
                    CONFLICT_EVENT_START,
                    CONFLICT_EVENT_END
                )
            ):

                conversion_rate *= np.random.uniform(
                    0.88,
                    0.94
                )

                spend *= np.random.uniform(
                    1.05,
                    1.12
                )

                impressions = int(
                    impressions
                    * np.random.uniform(
                        1.03,
                        1.10
                    )
                )

                clicks = int(
                    impressions
                    * ctr
                    * np.random.uniform(
                        0.98,
                        1.05
                    )
                )

            # ------------------------------------------------
            # Normal random variation
            # ------------------------------------------------

            conversion_rate *= np.random.uniform(
                0.90,
                1.10
            )

            conversions = int(
                clicks * conversion_rate
            )

            rows.append({
                "date": date.strftime(
                    "%Y-%m-%d"
                ),
                "campaign_id": campaign_id,
                "channel": channel,
                "spend": round(
                    spend,
                    2
                ),
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
            })

    return pd.DataFrame(rows)


# ============================================================
# 10. CREATE MARKETING DAILY SIGNAL
# ============================================================

def create_marketing_daily_signal(
    marketing_df
):

    temp = marketing_df.copy()

    temp["conversion_rate"] = np.where(
        temp["clicks"] > 0,
        temp["conversions"]
        / temp["clicks"],
        0
    )

    daily = (
        temp
        .groupby("date")
        .agg(
            total_spend=("spend", "sum"),
            total_clicks=("clicks", "sum"),
            total_conversions=("conversions", "sum"),
        )
        .reset_index()
    )

    daily["conversion_rate"] = np.where(
        daily["total_clicks"] > 0,
        daily["total_conversions"]
        / daily["total_clicks"],
        0
    )

    return daily


# ============================================================
# 11. GENERATE SALES
# ============================================================

def generate_sales(
    products_df,
    customers_df,
    inventory_df,
    marketing_daily,
    dates
):

    rows = []

    # ------------------------------------------------
    # Product lookups
    # ------------------------------------------------

    product_prices = dict(
        zip(
            products_df["product_id"],
            products_df["price"]
        )
    )

    product_categories = dict(
        zip(
            products_df["product_id"],
            products_df["category"]
        )
    )

    # ------------------------------------------------
    # Inventory lookup
    # ------------------------------------------------

    inventory_temp = inventory_df.copy()

    inventory_temp["date"] = pd.to_datetime(
        inventory_temp["date"]
    )

    inventory_lookup = (
        inventory_temp
        .groupby(
            [
                "date",
                "product_id",
                "region"
            ]
        )
        .agg(
            stock_available=(
                "stock_available",
                "mean"
            ),
            stockout_hours=(
                "stockout_hours",
                "mean"
            ),
        )
        .reset_index()
    )

    inventory_lookup["availability"] = (
        1
        - inventory_lookup["stockout_hours"]
        / 24
    )

    inventory_dict = {
        (
            row["date"],
            row["product_id"],
            row["region"]
        ): row["availability"]
        for _, row
        in inventory_lookup.iterrows()
    }

    # ------------------------------------------------
    # Marketing lookup
    # ------------------------------------------------

    marketing_dict = dict(
        zip(
            pd.to_datetime(
                marketing_daily["date"]
            ),
            marketing_daily[
                "conversion_rate"
            ]
        )
    )

    # ------------------------------------------------
    # Customer lookup
    # ------------------------------------------------

    customer_ids = customers_df[
        "customer_id"
    ].tolist()

    customer_segment_lookup = dict(
        zip(
            customers_df["customer_id"],
            customers_df["customer_segment"]
        )
    )

    # ------------------------------------------------
    # Product popularity
    # ------------------------------------------------

    normal_products = [
        p
        for p in products_df[
            "product_id"
        ]
        if p != "P999"
    ]

    popularity = {}

    for product_id in normal_products:

        category = product_categories[
            product_id
        ]

        if category == "Electronics":

            weight = np.random.uniform(
                1.2,
                2.0
            )

        elif category == "Grocery":

            weight = np.random.uniform(
                1.0,
                1.7
            )

        else:

            weight = np.random.uniform(
                0.5,
                1.4
            )

        popularity[
            product_id
        ] = weight

    total_weight = sum(
        popularity.values()
    )

    for product_id in popularity:

        popularity[
            product_id
        ] /= total_weight

    products = list(
        popularity.keys()
    )

    product_probabilities = np.array([
        popularity[p]
        for p in products
    ])

    # ------------------------------------------------
    # Sales generation
    # ------------------------------------------------

    order_counter = 1

    for date in dates:

        date_ts = pd.Timestamp(
            date
        )

        # ------------------------------------------------
        # Base demand
        # ------------------------------------------------

        base_orders = 650

        base_orders *= weekday_factor(
            date_ts
        )

        base_orders *= seasonal_factor(
            date_ts
        )

        # ------------------------------------------------
        # Marketing influence
        # ------------------------------------------------

        daily_conversion = marketing_dict.get(
            date_ts,
            0.065
        )

        normal_conversion = 0.065

        marketing_factor = 1.0

        if normal_conversion > 0:

            marketing_factor = (
                1
                + (
                    daily_conversion
                    - normal_conversion
                ) * 1.5
            )

        marketing_factor = clamp(
            marketing_factor,
            0.75,
            1.15
        )

        expected_orders = (
            base_orders
            * marketing_factor
        )

        # ------------------------------------------------
        # Regional multipliers
        # ------------------------------------------------

        region_order_multiplier = {}

        for region_name in REGIONS.values():

            multiplier = 1.0

            # =============================================
            # EVENT 3 — NORTH REVENUE DECLINE
            # =============================================

            if (
                region_name == "North"
                and is_between(
                    date_ts,
                    NORTH_EVENT_START,
                    NORTH_EVENT_END
                )
            ):

                multiplier = np.random.uniform(
                    0.72,
                    0.80
                )

            region_order_multiplier[
                region_name
            ] = multiplier

        # ------------------------------------------------
        # Generate regional sales
        # ------------------------------------------------

        for region_name in REGIONS.values():

            regional_orders = (
                expected_orders
                * REGION_WEIGHTS[
                    region_name
                ]
                * region_order_multiplier[
                    region_name
                ]
            )

            regional_orders = np.random.poisson(
                max(
                    regional_orders,
                    1
                )
            )

            for _ in range(
                regional_orders
            ):

                # ------------------------------------------------
                # Product
                # ------------------------------------------------

                product_id = np.random.choice(
                    products,
                    p=product_probabilities
                )

                # ------------------------------------------------
                # Inventory availability
                # ------------------------------------------------

                inventory_key = (
                    date_ts,
                    product_id,
                    region_name
                )

                availability = inventory_dict.get(
                    inventory_key,
                    0.95
                )

                availability = clamp(
                    availability,
                    0.10,
                    1.0
                )

                # ------------------------------------------------
                # Inventory influences probability of sale.
                #
                # This is important:
                # We don't directly reduce revenue.
                # The inventory problem naturally reduces orders.
                # ------------------------------------------------

                if (
                    np.random.random()
                    > availability
                ):
                    continue

                # ------------------------------------------------
                # Customer segment
                # ------------------------------------------------

                segment = np.random.choice(
                    list(
                        SEGMENT_WEIGHTS.keys()
                    ),
                    p=list(
                        SEGMENT_WEIGHTS.values()
                    )
                )

                # ------------------------------------------------
                # Customer
                # ------------------------------------------------

                candidates = [
                    cid
                    for cid in customer_ids
                    if customer_segment_lookup[
                        cid
                    ] == segment
                ]

                if candidates:

                    customer_id = np.random.choice(
                        candidates
                    )

                else:

                    customer_id = np.random.choice(
                        customer_ids
                    )

                # ------------------------------------------------
                # Sales channel
                # ------------------------------------------------

                channel = np.random.choice(
                    list(
                        CHANNEL_WEIGHTS.keys()
                    ),
                    p=list(
                        CHANNEL_WEIGHTS.values()
                    )
                )

                # ------------------------------------------------
                # Quantity
                # ------------------------------------------------

                quantity = int(
                    np.random.choice(
                        [1, 2, 3, 4],
                        p=[
                            0.60,
                            0.25,
                            0.10,
                            0.05,
                        ]
                    )
                )

                # ------------------------------------------------
                # Revenue
                # ------------------------------------------------

                price = product_prices[
                    product_id
                ]

                price_factor = np.random.uniform(
                    0.90,
                    1.02
                )

                revenue = (
                    price
                    * quantity
                    * price_factor
                )

                rows.append({
                    "order_id": (
                        f"ORD{order_counter:07d}"
                    ),
                    "date": date_ts.strftime(
                        "%Y-%m-%d"
                    ),
                    "product_id": product_id,
                    "region": region_name,
                    "customer_segment": segment,
                    "channel": channel,
                    "quantity": quantity,
                    "revenue": round(
                        revenue,
                        2
                    ),
                })

                order_counter += 1

        # ========================================================
        # EVENT 4 — P999 NEW PRODUCT
        # ========================================================

        if date_ts >= P999_LAUNCH_DATE:

            new_product_orders = np.random.poisson(
                8
            )

            for _ in range(
                new_product_orders
            ):

                region_name = np.random.choice(
                    list(
                        REGIONS.values()
                    )
                )

                segment = np.random.choice(
                    list(
                        SEGMENT_WEIGHTS.keys()
                    ),
                    p=list(
                        SEGMENT_WEIGHTS.values()
                    )
                )

                channel = np.random.choice(
                    list(
                        CHANNEL_WEIGHTS.keys()
                    ),
                    p=list(
                        CHANNEL_WEIGHTS.values()
                    )
                )

                quantity = int(
                    np.random.choice(
                        [1, 2],
                        p=[
                            0.80,
                            0.20
                        ]
                    )
                )

                price = product_prices[
                    "P999"
                ]

                revenue = (
                    price
                    * quantity
                    * np.random.uniform(
                        0.95,
                        1.0
                    )
                )

                rows.append({
                    "order_id": (
                        f"ORD{order_counter:07d}"
                    ),
                    "date": date_ts.strftime(
                        "%Y-%m-%d"
                    ),
                    "product_id": "P999",
                    "region": region_name,
                    "customer_segment": segment,
                    "channel": channel,
                    "quantity": quantity,
                    "revenue": round(
                        revenue,
                        2
                    ),
                })

                order_counter += 1

    sales_df = pd.DataFrame(
        rows
    )

    # ------------------------------------------------
    # Keep target sales volume approximately 150k.
    # ------------------------------------------------

    if len(sales_df) > 155000:

        sales_df = (
            sales_df
            .sample(
                n=150000,
                random_state=SEED
            )
            .sort_values(
                [
                    "date",
                    "order_id"
                ]
            )
            .reset_index(
                drop=True
            )
        )

    return sales_df


# ============================================================
# 12. VALIDATION
# ============================================================

def validate_data(
    sales_df,
    marketing_df,
    inventory_df,
    products_df,
    regions_df,
    customers_df
):

    print("\n" + "=" * 70)
    print("DATA VALIDATION")
    print("=" * 70)

    datasets = {
        "Sales": sales_df,
        "Marketing": marketing_df,
        "Inventory": inventory_df,
        "Products": products_df,
        "Regions": regions_df,
        "Customers": customers_df,
    }

    # ------------------------------------------------
    # Row counts
    # ------------------------------------------------

    print("\nROW COUNTS")
    print("-" * 70)

    for name, df in datasets.items():

        print(
            f"{name:<15} "
            f"{len(df):>10,} rows"
        )

    # ------------------------------------------------
    # Null values
    # ------------------------------------------------

    print("\nNULL VALUE CHECK")
    print("-" * 70)

    for name, df in datasets.items():

        null_count = int(
            df.isnull().sum().sum()
        )

        status = (
            "PASS"
            if null_count == 0
            else "FAIL"
        )

        print(
            f"{name:<15} "
            f"Nulls: {null_count:<8} "
            f"{status}"
        )

    # ------------------------------------------------
    # Sales checks
    # ------------------------------------------------

    print("\nSALES VALIDATION")
    print("-" * 70)

    duplicate_orders = (
        sales_df["order_id"]
        .duplicated()
        .sum()
    )

    negative_revenue = (
        sales_df["revenue"] < 0
    ).sum()

    invalid_quantity = (
        sales_df["quantity"] <= 0
    ).sum()

    print(
        f"Duplicate order IDs: "
        f"{duplicate_orders}"
    )

    print(
        f"Negative revenue: "
        f"{negative_revenue}"
    )

    print(
        f"Invalid quantities: "
        f"{invalid_quantity}"
    )

    # ------------------------------------------------
    # Marketing checks
    # ------------------------------------------------

    print("\nMARKETING VALIDATION")
    print("-" * 70)

    invalid_clicks = (
        marketing_df["clicks"]
        > marketing_df["impressions"]
    ).sum()

    invalid_conversions = (
        marketing_df["conversions"]
        > marketing_df["clicks"]
    ).sum()

    print(
        f"Clicks > impressions: "
        f"{invalid_clicks}"
    )

    print(
        f"Conversions > clicks: "
        f"{invalid_conversions}"
    )

    # ------------------------------------------------
    # Inventory checks
    # ------------------------------------------------

    print("\nINVENTORY VALIDATION")
    print("-" * 70)

    invalid_stockout = (
        (inventory_df["stockout_hours"] < 0)
        |
        (inventory_df["stockout_hours"] > 24)
    ).sum()

    negative_stock = (
        inventory_df["stock_available"] < 0
    ).sum()

    print(
        f"Invalid stockout hours: "
        f"{invalid_stockout}"
    )

    print(
        f"Negative stock: "
        f"{negative_stock}"
    )

    # =================================================
    # EVENT 1 — P001
    # =================================================

    print("\n" + "=" * 70)
    print("EVENT 1 — P001 INVENTORY SHOCK")
    print("=" * 70)

    inventory_temp = inventory_df.copy()

    inventory_temp["date"] = pd.to_datetime(
        inventory_temp["date"]
    )

    inventory_temp["availability"] = (
        1
        - inventory_temp["stockout_hours"]
        / 24
    ) * 100

    normal_p001 = inventory_temp[
        (
            inventory_temp["product_id"]
            == "P001"
        )
        &
        (
            inventory_temp["date"]
            < P001_SHOCK_START
        )
    ]

    event_p001 = inventory_temp[
        (
            inventory_temp["product_id"]
            == "P001"
        )
        &
        (
            inventory_temp["date"]
            .between(
                P001_SHOCK_START,
                P001_SHOCK_END
            )
        )
    ]

    print(
        f"Normal availability: "
        f"{normal_p001['availability'].mean():.2f}%"
    )

    print(
        f"Event availability: "
        f"{event_p001['availability'].mean():.2f}%"
    )

    # =================================================
    # EVENT 2 — PAID SOCIAL
    # =================================================

    print("\n" + "=" * 70)
    print("EVENT 2 — PAID SOCIAL MARKETING")
    print("=" * 70)

    marketing_temp = marketing_df.copy()

    marketing_temp["date"] = pd.to_datetime(
        marketing_temp["date"]
    )

    marketing_temp["conversion_rate"] = np.where(
        marketing_temp["clicks"] > 0,
        marketing_temp["conversions"]
        / marketing_temp["clicks"]
        * 100,
        0
    )

    normal_paid_social = marketing_temp[
        (
            marketing_temp["channel"]
            == "Paid Social"
        )
        &
        (
            marketing_temp["date"]
            < MARKETING_EVENT_START
        )
    ]

    event_paid_social = marketing_temp[
        (
            marketing_temp["channel"]
            == "Paid Social"
        )
        &
        (
            marketing_temp["date"]
            .between(
                MARKETING_EVENT_START,
                MARKETING_EVENT_END
            )
        )
    ]

    print(
        f"Normal spend: "
        f"{normal_paid_social['spend'].mean():,.2f}"
    )

    print(
        f"Event spend: "
        f"{event_paid_social['spend'].mean():,.2f}"
    )

    print(
        f"Normal conversion rate: "
        f"{normal_paid_social['conversion_rate'].mean():.2f}%"
    )

    print(
        f"Event conversion rate: "
        f"{event_paid_social['conversion_rate'].mean():.2f}%"
    )

    # =================================================
    # EVENT 3 — NORTH
    # =================================================

    print("\n" + "=" * 70)
    print("EVENT 3 — NORTH REGION")
    print("=" * 70)

    sales_temp = sales_df.copy()

    sales_temp["date"] = pd.to_datetime(
        sales_temp["date"]
    )

    north_normal = sales_temp[
        (
            sales_temp["region"]
            == "North"
        )
        &
        (
            sales_temp["date"]
            < NORTH_EVENT_START
        )
    ]

    north_event = sales_temp[
        (
            sales_temp["region"]
            == "North"
        )
        &
        (
            sales_temp["date"]
            .between(
                NORTH_EVENT_START,
                NORTH_EVENT_END
            )
        )
    ]

    normal_daily = (
        north_normal
        .groupby("date")
        ["revenue"]
        .sum()
        .mean()
    )

    event_daily = (
        north_event
        .groupby("date")
        ["revenue"]
        .sum()
        .mean()
    )

    change = (
        (
            event_daily
            - normal_daily
        )
        / normal_daily
    ) * 100

    print(
        f"Normal daily revenue: "
        f"{normal_daily:,.2f}"
    )

    print(
        f"Event daily revenue: "
        f"{event_daily:,.2f}"
    )

    print(
        f"Revenue change: "
        f"{change:.2f}%"
    )

    # =================================================
    # EVENT 4 — P999
    # =================================================

    print("\n" + "=" * 70)
    print("EVENT 4 — P999 NEW PRODUCT")
    print("=" * 70)

    p999_sales = sales_temp[
        sales_temp["product_id"]
        == "P999"
    ]

    if len(p999_sales) > 0:

        first_date = (
            p999_sales["date"].min()
        )

        last_date = (
            p999_sales["date"].max()
        )

        history = (
            last_date
            - first_date
        ).days + 1

        print(
            f"First date: "
            f"{first_date.date()}"
        )

        print(
            f"Last date: "
            f"{last_date.date()}"
        )

        print(
            f"History: "
            f"{history} days"
        )

    else:

        print(
            "P999 sales not found."
        )

    # =================================================
    # EVENT 5 — CONFLICTING EVIDENCE
    # =================================================

    print("\n" + "=" * 70)
    print("EVENT 5 — CONFLICTING EVIDENCE")
    print("=" * 70)

    # ------------------------------------------------
    # Marketing side
    # ------------------------------------------------

    conflict_marketing_normal = marketing_temp[
        (
            marketing_temp["channel"]
            .isin(
                [
                    "Paid Search",
                    "Email"
                ]
            )
        )
        &
        (
            marketing_temp["date"]
            < CONFLICT_EVENT_START
        )
    ]

    conflict_marketing_event = marketing_temp[
        (
            marketing_temp["channel"]
            .isin(
                [
                    "Paid Search",
                    "Email"
                ]
            )
        )
        &
        (
            marketing_temp["date"]
            .between(
                CONFLICT_EVENT_START,
                CONFLICT_EVENT_END
            )
        )
    ]

    normal_marketing_cr = (
        conflict_marketing_normal[
            "conversion_rate"
        ].mean()
    )

    event_marketing_cr = (
        conflict_marketing_event[
            "conversion_rate"
        ].mean()
    )

    # ------------------------------------------------
    # Inventory side
    # ------------------------------------------------

    conflict_inventory_normal = inventory_temp[
        (
            inventory_temp["product_id"]
            .isin(
                [
                    "P002",
                    "P003"
                ]
            )
        )
        &
        (
            inventory_temp["date"]
            < CONFLICT_EVENT_START
        )
    ]

    conflict_inventory_event = inventory_temp[
        (
            inventory_temp["product_id"]
            .isin(
                [
                    "P002",
                    "P003"
                ]
            )
        )
        &
        (
            inventory_temp["date"]
            .between(
                CONFLICT_EVENT_START,
                CONFLICT_EVENT_END
            )
        )
    ]

    normal_inventory_availability = (
        conflict_inventory_normal[
            "availability"
        ].mean()
    )

    event_inventory_availability = (
        conflict_inventory_event[
            "availability"
        ].mean()
    )

    print(
        "Marketing signal:"
    )

    print(
        f"  Normal conversion: "
        f"{normal_marketing_cr:.2f}%"
    )

    print(
        f"  Event conversion: "
        f"{event_marketing_cr:.2f}%"
    )

    print(
        "\nInventory signal:"
    )

    print(
        f"  Normal availability: "
        f"{normal_inventory_availability:.2f}%"
    )

    print(
        f"  Event availability: "
        f"{event_inventory_availability:.2f}%"
    )

    print(
        "\nExpected interpretation:"
    )

    print(
        "  Multiple moderate signals exist."
    )

    print(
        "  No single driver should automatically "
        "be treated as the primary cause."
    )

    print(
        "  Future intelligence engine should "
        "evaluate evidence and confidence."
    )


# ============================================================
# 13. SAVE DATASETS
# ============================================================

def save_datasets(
    sales_df,
    marketing_df,
    inventory_df,
    products_df,
    regions_df,
    customers_df
):

    paths = {
        "sales": os.path.join(
            OUTPUT_DIR,
            "sales.csv"
        ),
        "marketing": os.path.join(
            OUTPUT_DIR,
            "marketing.csv"
        ),
        "inventory": os.path.join(
            OUTPUT_DIR,
            "inventory.csv"
        ),
        "products": os.path.join(
            OUTPUT_DIR,
            "products.csv"
        ),
        "regions": os.path.join(
            OUTPUT_DIR,
            "regions.csv"
        ),
        "customers": os.path.join(
            OUTPUT_DIR,
            "customers.csv"
        ),
    }

    sales_df.to_csv(
        paths["sales"],
        index=False
    )

    marketing_df.to_csv(
        paths["marketing"],
        index=False
    )

    inventory_df.to_csv(
        paths["inventory"],
        index=False
    )

    products_df.to_csv(
        paths["products"],
        index=False
    )

    regions_df.to_csv(
        paths["regions"],
        index=False
    )

    customers_df.to_csv(
        paths["customers"],
        index=False
    )

    print("\n" + "=" * 70)
    print("FILES CREATED")
    print("=" * 70)

    for path in paths.values():

        print(path)


# ============================================================
# 14. MAIN
# ============================================================

def main():

    print("=" * 70)
    print("BusinessIntelligence.ai")
    print("NexaMart Synthetic Data Generator")
    print("=" * 70)

    # ------------------------------------------------
    # Dates
    # ------------------------------------------------

    dates = pd.date_range(
        START_DATE,
        END_DATE,
        freq="D"
    )

    print(
        f"\nGenerating data from "
        f"{START_DATE} to {END_DATE}"
    )

    # ------------------------------------------------
    # Dimensions
    # ------------------------------------------------

    print("\nGenerating products...")

    products_df = generate_products()

    print("Generating regions...")

    regions_df = generate_regions()

    print("Generating customers...")

    customers_df = generate_customers(
        n_customers=5000
    )

    # ------------------------------------------------
    # Inventory
    # ------------------------------------------------

    print("Generating inventory...")

    inventory_df = generate_inventory(
        products_df,
        dates
    )

    # ------------------------------------------------
    # Marketing
    # ------------------------------------------------

    print("Generating marketing...")

    marketing_df = generate_marketing(
        dates
    )

    # ------------------------------------------------
    # Marketing signal
    # ------------------------------------------------

    marketing_daily = (
        create_marketing_daily_signal(
            marketing_df
        )
    )

    # ------------------------------------------------
    # Sales
    # ------------------------------------------------

    print("Generating sales...")

    sales_df = generate_sales(
        products_df,
        customers_df,
        inventory_df,
        marketing_daily,
        dates
    )

    # ------------------------------------------------
    # Save
    # ------------------------------------------------

    save_datasets(
        sales_df,
        marketing_df,
        inventory_df,
        products_df,
        regions_df,
        customers_df
    )

    # ------------------------------------------------
    # Validate
    # ------------------------------------------------

    validate_data(
        sales_df,
        marketing_df,
        inventory_df,
        products_df,
        regions_df,
        customers_df
    )

    print("\n" + "=" * 70)
    print("SUCCESS")
    print("=" * 70)

    print(
        "Synthetic NexaMart datasets "
        "generated and validated."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()