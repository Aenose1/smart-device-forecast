"""Comprehensive dataset generator: 260+ Smartphones and 260+ Laptops (both normal & gaming)."""
import csv
import math
import random
from datetime import date
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "sample"
END = date(2026, 9, 1)

PHONES = [
    # === Apple (26 models) ===
    ("Apple", "iPhone 16 Pro Max", "2024-09", 144900, 8, 256, 6.9, 4685, 48, "A18 Pro"),
    ("Apple", "iPhone 16 Pro", "2024-09", 119900, 8, 128, 6.3, 3582, 48, "A18 Pro"),
    ("Apple", "iPhone 16 Plus", "2024-09", 89900, 8, 128, 6.7, 4674, 48, "A18"),
    ("Apple", "iPhone 16", "2024-09", 79900, 8, 128, 6.1, 3561, 48, "A18"),
    ("Apple", "iPhone 16e", "2025-02", 59900, 8, 128, 6.1, 4005, 48, "A18"),
    ("Apple", "iPhone 15 Pro Max", "2023-09", 159900, 8, 256, 6.7, 4422, 48, "A17 Pro"),
    ("Apple", "iPhone 15 Pro", "2023-09", 134900, 8, 128, 6.1, 3274, 48, "A17 Pro"),
    ("Apple", "iPhone 15 Plus", "2023-09", 89900, 6, 128, 6.7, 4383, 48, "A16 Bionic"),
    ("Apple", "iPhone 15", "2023-09", 79900, 6, 128, 6.1, 3349, 48, "A16 Bionic"),
    ("Apple", "iPhone 14 Pro Max", "2022-09", 139900, 6, 128, 6.7, 4323, 48, "A16 Bionic"),
    ("Apple", "iPhone 14 Pro", "2022-09", 129900, 6, 128, 6.1, 3200, 48, "A16 Bionic"),
    ("Apple", "iPhone 14 Plus", "2022-09", 79900, 6, 128, 6.7, 4325, 12, "A15 Bionic"),
    ("Apple", "iPhone 14", "2022-09", 69900, 6, 128, 6.1, 3279, 12, "A15 Bionic"),
    ("Apple", "iPhone 13 Pro Max", "2021-09", 129900, 6, 128, 6.7, 4352, 12, "A15 Bionic"),
    ("Apple", "iPhone 13 Pro", "2021-09", 119900, 6, 128, 6.1, 3095, 12, "A15 Bionic"),
    ("Apple", "iPhone 13", "2021-09", 59900, 4, 128, 6.1, 3227, 12, "A15 Bionic"),
    ("Apple", "iPhone 13 mini", "2021-09", 54900, 4, 128, 5.4, 2406, 12, "A15 Bionic"),
    ("Apple", "iPhone 12 Pro Max", "2020-10", 119900, 6, 128, 6.7, 3687, 12, "A14 Bionic"),
    ("Apple", "iPhone 12 Pro", "2020-10", 109900, 6, 128, 6.1, 2815, 12, "A14 Bionic"),
    ("Apple", "iPhone 12", "2020-10", 49900, 4, 64, 6.1, 2815, 12, "A14 Bionic"),
    ("Apple", "iPhone 12 mini", "2020-10", 44900, 4, 64, 5.4, 2227, 12, "A14 Bionic"),
    ("Apple", "iPhone 11 Pro Max", "2019-09", 109900, 4, 64, 6.5, 3969, 12, "A13 Bionic"),
    ("Apple", "iPhone 11 Pro", "2019-09", 99900, 4, 64, 5.8, 3046, 12, "A13 Bionic"),
    ("Apple", "iPhone 11", "2019-09", 43900, 4, 64, 6.1, 3110, 12, "A13 Bionic"),
    ("Apple", "iPhone SE (3rd Gen)", "2022-03", 43900, 4, 64, 4.7, 2018, 12, "A15 Bionic"),
    ("Apple", "iPhone SE (2nd Gen)", "2020-04", 39900, 3, 64, 4.7, 1821, 12, "A13 Bionic"),

    # === Samsung (46 models) ===
    ("Samsung", "Samsung Galaxy S25 Ultra", "2025-02", 129999, 12, 256, 6.9, 5000, 200, "Snapdragon 8 Elite for Galaxy"),
    ("Samsung", "Samsung Galaxy S25+", "2025-02", 99999, 12, 256, 6.7, 4900, 50, "Snapdragon 8 Elite for Galaxy"),
    ("Samsung", "Samsung Galaxy S25", "2025-02", 80999, 12, 256, 6.2, 4000, 50, "Snapdragon 8 Elite for Galaxy"),
    ("Samsung", "Samsung Galaxy S24 Ultra", "2024-01", 129999, 12, 256, 6.8, 5000, 200, "Snapdragon 8 Gen 3 for Galaxy"),
    ("Samsung", "Samsung Galaxy S24+", "2024-01", 99999, 12, 256, 6.7, 4900, 50, "Exynos 2400"),
    ("Samsung", "Samsung Galaxy S24", "2024-01", 79999, 8, 256, 6.2, 4000, 50, "Exynos 2400"),
    ("Samsung", "Samsung Galaxy S24 FE", "2024-10", 59999, 8, 128, 6.7, 4700, 50, "Exynos 2400e"),
    ("Samsung", "Samsung Galaxy S23 Ultra", "2023-02", 124999, 12, 256, 6.8, 5000, 200, "Snapdragon 8 Gen 2 for Galaxy"),
    ("Samsung", "Samsung Galaxy S23+", "2023-02", 94999, 8, 256, 6.6, 4700, 50, "Snapdragon 8 Gen 2 for Galaxy"),
    ("Samsung", "Samsung Galaxy S23", "2023-02", 74999, 8, 128, 6.1, 3900, 50, "Snapdragon 8 Gen 2 for Galaxy"),
    ("Samsung", "Samsung Galaxy S23 FE", "2023-10", 49999, 8, 128, 6.4, 4500, 50, "Exynos 2200"),
    ("Samsung", "Samsung Galaxy S22 Ultra", "2022-02", 109999, 12, 256, 6.8, 5000, 108, "Snapdragon 8 Gen 1"),
    ("Samsung", "Samsung Galaxy S22+", "2022-02", 84999, 8, 128, 6.6, 4500, 50, "Snapdragon 8 Gen 1"),
    ("Samsung", "Samsung Galaxy S22", "2022-02", 72999, 8, 128, 6.1, 3700, 50, "Snapdragon 8 Gen 1"),
    ("Samsung", "Samsung Galaxy S21 Ultra", "2021-01", 105999, 12, 256, 6.8, 5000, 108, "Exynos 2100"),
    ("Samsung", "Samsung Galaxy S21 FE 5G", "2022-01", 49999, 8, 128, 6.4, 4500, 12, "Snapdragon 888"),
    ("Samsung", "Samsung Galaxy S20 FE 5G", "2021-03", 36999, 8, 128, 6.5, 4500, 12, "Snapdragon 865"),
    ("Samsung", "Samsung Galaxy Z Fold6", "2024-07", 164999, 12, 256, 7.6, 4400, 50, "Snapdragon 8 Gen 3 for Galaxy"),
    ("Samsung", "Samsung Galaxy Z Flip6", "2024-07", 109999, 12, 256, 6.7, 4000, 50, "Snapdragon 8 Gen 3 for Galaxy"),
    ("Samsung", "Samsung Galaxy Z Fold5", "2023-07", 154999, 12, 256, 7.6, 4400, 50, "Snapdragon 8 Gen 2 for Galaxy"),
    ("Samsung", "Samsung Galaxy Z Flip5", "2023-07", 99999, 8, 256, 6.7, 3700, 12, "Snapdragon 8 Gen 2 for Galaxy"),
    ("Samsung", "Samsung Galaxy Z Fold4", "2022-08", 144999, 12, 256, 7.6, 4400, 50, "Snapdragon 8+ Gen 1"),
    ("Samsung", "Samsung Galaxy Z Flip4", "2022-08", 89999, 8, 128, 6.7, 3700, 12, "Snapdragon 8+ Gen 1"),
    ("Samsung", "Samsung Galaxy A55 5G", "2024-03", 39999, 8, 128, 6.6, 5000, 50, "Exynos 1480"),
    ("Samsung", "Samsung Galaxy A54 5G", "2023-03", 38999, 8, 128, 6.4, 5000, 50, "Exynos 1380"),
    ("Samsung", "Samsung Galaxy A53 5G", "2022-03", 34499, 6, 128, 6.5, 5000, 64, "Exynos 1280"),
    ("Samsung", "Samsung Galaxy A35 5G", "2024-03", 30999, 8, 128, 6.6, 5000, 50, "Exynos 1380"),
    ("Samsung", "Samsung Galaxy A34 5G", "2023-03", 30999, 8, 128, 6.6, 5000, 48, "Dimensity 1080"),
    ("Samsung", "Samsung Galaxy A33 5G", "2022-04", 28499, 6, 128, 6.4, 5000, 48, "Exynos 1280"),
    ("Samsung", "Samsung Galaxy A25 5G", "2024-01", 26999, 8, 128, 6.5, 5000, 50, "Exynos 1280"),
    ("Samsung", "Samsung Galaxy A24 4G", "2023-04", 18999, 6, 128, 6.5, 5000, 50, "Helio G99"),
    ("Samsung", "Samsung Galaxy A15 5G", "2024-01", 19499, 6, 128, 6.5, 5000, 50, "Dimensity 6100+"),
    ("Samsung", "Samsung Galaxy A14 5G", "2023-01", 16499, 4, 64, 6.6, 5000, 50, "Exynos 1330"),
    ("Samsung", "Samsung Galaxy A05s", "2023-10", 13499, 6, 128, 6.7, 5000, 50, "Snapdragon 680"),
    ("Samsung", "Samsung Galaxy A05", "2023-10", 9999, 4, 64, 6.7, 5000, 50, "Helio G85"),
    ("Samsung", "Samsung Galaxy M55 5G", "2024-04", 26999, 8, 128, 6.7, 5000, 50, "Snapdragon 7 Gen 1"),
    ("Samsung", "Samsung Galaxy M54 5G", "2023-04", 29999, 8, 128, 6.7, 6000, 108, "Exynos 1380"),
    ("Samsung", "Samsung Galaxy M53 5G", "2022-04", 26499, 6, 128, 6.7, 5000, 108, "Dimensity 900"),
    ("Samsung", "Samsung Galaxy M35 5G", "2024-07", 19999, 6, 128, 6.6, 6000, 50, "Exynos 1380"),
    ("Samsung", "Samsung Galaxy M34 5G", "2023-07", 18999, 6, 128, 6.5, 6000, 50, "Exynos 1280"),
    ("Samsung", "Samsung Galaxy M33 5G", "2022-04", 17999, 6, 128, 6.6, 6000, 50, "Exynos 1280"),
    ("Samsung", "Samsung Galaxy M15 5G", "2024-04", 13299, 4, 128, 6.5, 6000, 50, "Dimensity 6100+"),
    ("Samsung", "Samsung Galaxy M14 5G", "2023-04", 14990, 4, 128, 6.6, 6000, 50, "Exynos 1330"),
    ("Samsung", "Samsung Galaxy F55 5G", "2024-05", 26999, 8, 128, 6.7, 5000, 50, "Snapdragon 7 Gen 1"),
    ("Samsung", "Samsung Galaxy F54 5G", "2023-06", 29999, 8, 256, 6.7, 6000, 108, "Exynos 1380"),
    ("Samsung", "Samsung Galaxy F15 5G", "2024-03", 12999, 4, 128, 6.5, 6000, 50, "Dimensity 6100+"),

    # === Google (15 models) ===
    ("Google", "Google Pixel 9 Pro Fold", "2024-08", 172999, 16, 256, 8.0, 4650, 48, "Google Tensor G4"),
    ("Google", "Google Pixel 9 Pro XL", "2024-08", 124999, 16, 256, 6.8, 5060, 50, "Google Tensor G4"),
    ("Google", "Google Pixel 9 Pro", "2024-08", 109999, 16, 128, 6.3, 4700, 50, "Google Tensor G4"),
    ("Google", "Google Pixel 9", "2024-08", 79999, 12, 256, 6.3, 4700, 50, "Google Tensor G4"),
    ("Google", "Google Pixel 9a", "2025-04", 49999, 8, 128, 6.3, 5100, 48, "Google Tensor G4"),
    ("Google", "Google Pixel 8 Pro", "2023-10", 106999, 12, 128, 6.7, 5050, 50, "Google Tensor G3"),
    ("Google", "Google Pixel 8", "2023-10", 75999, 8, 128, 6.2, 4575, 50, "Google Tensor G3"),
    ("Google", "Google Pixel 8a", "2024-05", 52999, 8, 128, 6.1, 4492, 64, "Google Tensor G3"),
    ("Google", "Google Pixel Fold", "2023-05", 149999, 12, 256, 7.6, 4821, 48, "Google Tensor G2"),
    ("Google", "Google Pixel 7 Pro", "2022-10", 84999, 12, 128, 6.7, 5000, 50, "Google Tensor G2"),
    ("Google", "Google Pixel 7", "2022-10", 59999, 8, 128, 6.3, 4355, 50, "Google Tensor G2"),
    ("Google", "Google Pixel 7a", "2023-05", 43999, 8, 128, 6.1, 4385, 64, "Google Tensor G2"),
    ("Google", "Google Pixel 6 Pro", "2021-10", 69999, 12, 128, 6.7, 5003, 50, "Google Tensor"),
    ("Google", "Google Pixel 6", "2021-10", 49999, 8, 128, 6.4, 4614, 50, "Google Tensor"),
    ("Google", "Google Pixel 6a", "2022-07", 43999, 6, 128, 6.1, 4410, 12, "Google Tensor"),

    # === OnePlus (23 models) ===
    ("OnePlus", "OnePlus 13", "2025-01", 69999, 12, 256, 6.82, 6000, 50, "Snapdragon 8 Elite"),
    ("OnePlus", "OnePlus 13R", "2025-01", 42999, 12, 256, 6.78, 6000, 50, "Snapdragon 8 Gen 3"),
    ("OnePlus", "OnePlus 12", "2024-01", 64999, 12, 256, 6.82, 5400, 50, "Snapdragon 8 Gen 3"),
    ("OnePlus", "OnePlus 12R", "2024-02", 39999, 8, 128, 6.78, 5500, 50, "Snapdragon 8 Gen 2"),
    ("OnePlus", "OnePlus Open", "2023-10", 139999, 16, 512, 7.82, 4805, 48, "Snapdragon 8 Gen 2"),
    ("OnePlus", "OnePlus 11 5G", "2023-02", 56999, 8, 128, 6.7, 5000, 50, "Snapdragon 8 Gen 2"),
    ("OnePlus", "OnePlus 11R 5G", "2023-02", 39999, 8, 128, 6.74, 5000, 50, "Snapdragon 8+ Gen 1"),
    ("OnePlus", "OnePlus 10 Pro 5G", "2022-03", 66999, 8, 128, 6.7, 5000, 48, "Snapdragon 8 Gen 1"),
    ("OnePlus", "OnePlus 10T 5G", "2022-08", 49999, 8, 128, 6.7, 4800, 50, "Snapdragon 8+ Gen 1"),
    ("OnePlus", "OnePlus 10R 5G", "2022-04", 38999, 8, 128, 6.7, 5000, 50, "Dimensity 8100-Max"),
    ("OnePlus", "OnePlus 9 Pro 5G", "2021-03", 64999, 8, 128, 6.7, 4500, 48, "Snapdragon 888"),
    ("OnePlus", "OnePlus 9 5G", "2021-03", 49999, 8, 128, 6.55, 4500, 48, "Snapdragon 888"),
    ("OnePlus", "OnePlus 9RT 5G", "2022-01", 42999, 8, 128, 6.62, 4500, 50, "Snapdragon 888"),
    ("OnePlus", "OnePlus Nord 4", "2024-07", 29999, 8, 128, 6.74, 5500, 50, "Snapdragon 7+ Gen 3"),
    ("OnePlus", "OnePlus Nord 3 5G", "2023-07", 33999, 8, 128, 6.74, 5000, 50, "Dimensity 9000"),
    ("OnePlus", "OnePlus Nord 2T 5G", "2022-07", 28999, 8, 128, 6.43, 4500, 50, "Dimensity 1300"),
    ("OnePlus", "OnePlus Nord CE4", "2024-04", 24999, 8, 128, 6.7, 5500, 50, "Snapdragon 7 Gen 3"),
    ("OnePlus", "OnePlus Nord CE4 Lite 5G", "2024-06", 19999, 8, 128, 6.67, 5500, 50, "Snapdragon 695"),
    ("OnePlus", "OnePlus Nord CE 3 5G", "2023-07", 26999, 8, 128, 6.7, 5000, 50, "Snapdragon 782G"),
    ("OnePlus", "OnePlus Nord CE 3 Lite 5G", "2023-04", 19999, 8, 128, 6.72, 5000, 108, "Snapdragon 695"),
    ("OnePlus", "OnePlus Nord CE 2 5G", "2022-02", 23999, 6, 128, 6.43, 4500, 64, "Dimensity 900"),
    ("OnePlus", "OnePlus Nord CE 2 Lite 5G", "2022-04", 19999, 6, 128, 6.59, 5000, 64, "Snapdragon 695"),
    ("OnePlus", "OnePlus Nord", "2020-07", 24999, 6, 64, 6.44, 4115, 48, "Snapdragon 765G"),

    # === Xiaomi (16 models) ===
    ("Xiaomi", "Xiaomi 15 Pro", "2025-03", 74999, 12, 256, 6.73, 6100, 50, "Snapdragon 8 Elite"),
    ("Xiaomi", "Xiaomi 15", "2025-03", 64999, 12, 256, 6.36, 5240, 50, "Snapdragon 8 Elite"),
    ("Xiaomi", "Xiaomi 14 Ultra", "2024-03", 99999, 16, 512, 6.73, 5000, 50, "Snapdragon 8 Gen 3"),
    ("Xiaomi", "Xiaomi 14 Pro", "2023-11", 79999, 12, 256, 6.73, 4880, 50, "Snapdragon 8 Gen 3"),
    ("Xiaomi", "Xiaomi 14", "2024-02", 69999, 12, 256, 6.36, 4610, 50, "Snapdragon 8 Gen 3"),
    ("Xiaomi", "Xiaomi 14 Civi", "2024-06", 42999, 8, 256, 6.55, 4700, 50, "Snapdragon 8s Gen 3"),
    ("Xiaomi", "Xiaomi 13 Pro", "2023-02", 79999, 12, 256, 6.73, 4820, 50, "Snapdragon 8 Gen 2"),
    ("Xiaomi", "Xiaomi 13T Pro", "2023-09", 59999, 12, 256, 6.67, 5000, 50, "Dimensity 9200+"),
    ("Xiaomi", "Xiaomi 13 Ultra", "2023-04", 89999, 12, 256, 6.73, 5000, 50, "Snapdragon 8 Gen 2"),
    ("Xiaomi", "Xiaomi 12 Pro", "2022-04", 62999, 8, 256, 6.73, 4600, 50, "Snapdragon 8 Gen 1"),
    ("Xiaomi", "Xiaomi 12T Pro", "2022-10", 54999, 8, 128, 6.67, 5000, 200, "Snapdragon 8+ Gen 1"),
    ("Xiaomi", "Xiaomi 11T Pro 5G", "2022-01", 39999, 8, 128, 6.67, 5000, 108, "Snapdragon 888"),
    ("Xiaomi", "Xiaomi 11 Lite NE 5G", "2021-09", 26999, 6, 128, 6.55, 4250, 64, "Snapdragon 778G"),
    ("Xiaomi", "Xiaomi 11X Pro 5G", "2021-04", 39999, 8, 128, 6.67, 4520, 108, "Snapdragon 888"),
    ("Xiaomi", "Xiaomi 11X 5G", "2021-04", 29999, 6, 128, 6.67, 4520, 48, "Snapdragon 870"),
    ("Xiaomi", "Xiaomi Mi 10T Pro 5G", "2020-10", 39999, 8, 128, 6.67, 5000, 108, "Snapdragon 865"),

    # === Redmi (25 models) ===
    ("Redmi", "Redmi Note 14 Pro+ 5G", "2024-12", 29999, 8, 256, 6.67, 5110, 50, "Snapdragon 7s Gen 3"),
    ("Redmi", "Redmi Note 14 Pro 5G", "2024-12", 24999, 8, 128, 6.67, 5500, 50, "Dimensity 7300 Ultra"),
    ("Redmi", "Redmi Note 14 5G", "2024-12", 17999, 6, 128, 6.67, 5110, 50, "Dimensity 7025 Ultra"),
    ("Redmi", "Redmi Note 13 Pro+ 5G", "2024-01", 31999, 8, 256, 6.67, 5000, 200, "Dimensity 7200 Ultra"),
    ("Redmi", "Redmi Note 13 Pro 5G", "2024-01", 25999, 8, 128, 6.67, 5100, 200, "Snapdragon 7s Gen 2"),
    ("Redmi", "Redmi Note 13 5G", "2024-01", 17999, 6, 128, 6.67, 5000, 108, "Dimensity 6080"),
    ("Redmi", "Redmi Note 12 Pro+ 5G", "2023-01", 29999, 8, 256, 6.67, 4980, 200, "Dimensity 1080"),
    ("Redmi", "Redmi Note 12 Pro 5G", "2023-01", 24999, 6, 128, 6.67, 5000, 50, "Dimensity 1080"),
    ("Redmi", "Redmi Note 12 5G", "2023-01", 17999, 4, 128, 6.67, 5000, 48, "Snapdragon 4 Gen 1"),
    ("Redmi", "Redmi Note 11 Pro+ 5G", "2022-03", 20999, 6, 128, 6.67, 5000, 108, "Snapdragon 695"),
    ("Redmi", "Redmi Note 11 Pro", "2022-03", 17999, 6, 128, 6.67, 5000, 108, "Helio G96"),
    ("Redmi", "Redmi Note 11", "2022-01", 13499, 4, 64, 6.43, 5000, 50, "Snapdragon 680"),
    ("Redmi", "Redmi Note 10 Pro Max", "2021-03", 18999, 6, 128, 6.67, 5020, 108, "Snapdragon 732G"),
    ("Redmi", "Redmi Note 10 Pro", "2021-03", 15999, 6, 64, 6.67, 5020, 64, "Snapdragon 732G"),
    ("Redmi", "Redmi Note 10", "2021-03", 11999, 4, 64, 6.43, 5000, 48, "Snapdragon 678"),
    ("Redmi", "Redmi 14C", "2024-08", 10999, 4, 128, 6.88, 5160, 50, "Helio G81 Ultra"),
    ("Redmi", "Redmi 13 5G", "2024-07", 13999, 6, 128, 6.79, 5030, 108, "Snapdragon 4 Gen 2 AE"),
    ("Redmi", "Redmi 13C 5G", "2023-12", 10999, 4, 128, 6.74, 5000, 50, "Dimensity 6100+"),
    ("Redmi", "Redmi 13C", "2023-11", 8999, 4, 128, 6.74, 5000, 50, "Helio G85"),
    ("Redmi", "Redmi 12 5G", "2023-08", 11999, 4, 128, 6.79, 5000, 50, "Snapdragon 4 Gen 2"),
    ("Redmi", "Redmi 12", "2023-08", 9999, 4, 128, 6.79, 5000, 50, "Helio G88"),
    ("Redmi", "Redmi 11 Prime 5G", "2022-09", 13999, 4, 64, 6.58, 5000, 50, "Dimensity 700"),
    ("Redmi", "Redmi A3", "2024-02", 7299, 3, 64, 6.71, 5000, 8, "Helio G36"),
    ("Redmi", "Redmi A3x", "2024-05", 6999, 3, 64, 6.71, 5000, 8, "Unisoc T603"),
    ("Redmi", "Redmi A2", "2023-05", 6299, 2, 32, 6.52, 5000, 8, "Helio G36"),

    # === Vivo (30 models) ===
    ("vivo", "vivo X100 Ultra", "2024-05", 99999, 16, 512, 6.78, 5500, 50, "Snapdragon 8 Gen 3"),
    ("vivo", "vivo X100 Pro", "2024-01", 89999, 16, 512, 6.78, 5400, 50, "Dimensity 9300"),
    ("vivo", "vivo X100", "2024-01", 63999, 12, 256, 6.78, 5000, 50, "Dimensity 9300"),
    ("vivo", "vivo X90 Pro", "2023-04", 84999, 12, 256, 6.78, 4870, 50, "Dimensity 9200"),
    ("vivo", "vivo X90", "2023-04", 59999, 8, 256, 6.78, 4810, 50, "Dimensity 9200"),
    ("vivo", "vivo X80 Pro", "2022-05", 79999, 12, 256, 6.78, 4700, 50, "Snapdragon 8 Gen 1"),
    ("vivo", "vivo X Fold3 Pro", "2024-06", 159999, 16, 512, 8.03, 5700, 50, "Snapdragon 8 Gen 3"),
    ("vivo", "vivo V50", "2025-02", 34999, 8, 128, 6.77, 6000, 50, "Snapdragon 7 Gen 3"),
    ("vivo", "vivo V40 Pro", "2024-08", 49999, 8, 256, 6.78, 5500, 50, "Dimensity 9200+"),
    ("vivo", "vivo V40", "2024-08", 34999, 8, 128, 6.78, 5500, 50, "Snapdragon 7 Gen 3"),
    ("vivo", "vivo V40e", "2024-09", 28999, 8, 128, 6.77, 5500, 50, "Dimensity 7300"),
    ("vivo", "vivo V30 Pro", "2024-03", 41999, 8, 256, 6.78, 5000, 50, "Dimensity 8200"),
    ("vivo", "vivo V30", "2024-03", 33999, 8, 128, 6.78, 5000, 50, "Snapdragon 7 Gen 3"),
    ("vivo", "vivo V30e", "2024-05", 27999, 8, 128, 6.78, 5500, 50, "Snapdragon 6 Gen 1"),
    ("vivo", "vivo V29 Pro", "2023-10", 39999, 8, 256, 6.78, 4600, 50, "Dimensity 8200"),
    ("vivo", "vivo V29", "2023-10", 32999, 8, 128, 6.78, 4600, 50, "Snapdragon 778G"),
    ("vivo", "vivo V29e", "2023-08", 26999, 8, 128, 6.78, 5000, 64, "Snapdragon 695"),
    ("vivo", "vivo V27 Pro", "2023-03", 37999, 8, 128, 6.78, 4600, 50, "Dimensity 8200"),
    ("vivo", "vivo V27", "2023-03", 32999, 8, 128, 6.78, 4600, 50, "Dimensity 7200"),
    ("vivo", "vivo T4 5G", "2025-03", 21999, 8, 128, 6.77, 7300, 50, "Snapdragon 7s Gen 3"),
    ("vivo", "vivo T3 Ultra 5G", "2024-09", 31999, 8, 128, 6.78, 5500, 50, "Dimensity 9200+"),
    ("vivo", "vivo T3 Pro 5G", "2024-08", 24999, 8, 128, 6.77, 5500, 50, "Snapdragon 7 Gen 3"),
    ("vivo", "vivo T3 5G", "2024-03", 19999, 8, 128, 6.67, 5000, 50, "Dimensity 7200"),
    ("vivo", "vivo T3x 5G", "2024-04", 13499, 4, 128, 6.72, 6000, 50, "Snapdragon 6 Gen 1"),
    ("vivo", "vivo T2 Pro 5G", "2023-09", 23999, 8, 128, 6.78, 4600, 64, "Dimensity 7200"),
    ("vivo", "vivo T2 5G", "2023-04", 18999, 6, 128, 6.38, 4500, 64, "Snapdragon 695"),
    ("vivo", "vivo Y200 5G", "2023-10", 21999, 8, 128, 6.67, 4800, 64, "Snapdragon 4 Gen 1"),
    ("vivo", "vivo Y200e 5G", "2024-02", 19999, 6, 128, 6.67, 5000, 50, "Snapdragon 4 Gen 2"),
    ("vivo", "vivo Y58 5G", "2024-06", 19499, 8, 128, 6.72, 6000, 50, "Snapdragon 4 Gen 2"),
    ("vivo", "vivo Y28 5G", "2024-01", 13999, 4, 128, 6.56, 5000, 50, "Dimensity 6020"),

    # === iQOO (16 models) ===
    ("vivo", "iQOO 13", "2024-12", 54999, 12, 256, 6.82, 6000, 50, "Snapdragon 8 Elite"),
    ("vivo", "iQOO 12", "2023-12", 52999, 12, 256, 6.78, 5000, 50, "Snapdragon 8 Gen 3"),
    ("vivo", "iQOO 11 5G", "2023-01", 59999, 8, 256, 6.78, 5000, 50, "Snapdragon 8 Gen 2"),
    ("vivo", "iQOO 9 Pro 5G", "2022-02", 64990, 8, 256, 6.78, 4700, 50, "Snapdragon 8 Gen 1"),
    ("vivo", "iQOO 9T 5G", "2022-08", 49999, 8, 128, 6.78, 4700, 50, "Snapdragon 8+ Gen 1"),
    ("vivo", "iQOO Neo 9 Pro", "2024-02", 35999, 8, 128, 6.78, 5160, 50, "Snapdragon 8 Gen 2"),
    ("vivo", "iQOO Neo 7 Pro", "2023-07", 34999, 8, 128, 6.78, 5000, 50, "Snapdragon 8+ Gen 1"),
    ("vivo", "iQOO Neo 7 5G", "2023-02", 29999, 8, 128, 6.78, 5000, 64, "Dimensity 8200"),
    ("vivo", "iQOO Neo 6 5G", "2022-05", 29999, 8, 128, 6.62, 4700, 64, "Snapdragon 870"),
    ("vivo", "iQOO Z9 Turbo", "2024-04", 28999, 12, 256, 6.78, 6000, 50, "Snapdragon 8s Gen 3"),
    ("vivo", "iQOO Z9s Pro 5G", "2024-08", 24999, 8, 128, 6.77, 5500, 50, "Snapdragon 7 Gen 3"),
    ("vivo", "iQOO Z9s 5G", "2024-08", 19999, 8, 128, 6.77, 5500, 50, "Dimensity 7300"),
    ("vivo", "iQOO Z9 5G", "2024-03", 19999, 8, 128, 6.67, 5000, 50, "Dimensity 7200"),
    ("vivo", "iQOO Z9x 5G", "2024-05", 12999, 4, 128, 6.72, 6000, 50, "Snapdragon 6 Gen 1"),
    ("vivo", "iQOO Z7 Pro 5G", "2023-08", 23999, 8, 128, 6.78, 4600, 64, "Dimensity 7200"),
    ("vivo", "iQOO Z7 5G", "2023-03", 18999, 6, 128, 6.38, 4500, 64, "Dimensity 920"),

    # === OPPO (24 models) ===
    ("OPPO", "OPPO Find X8 Pro", "2024-11", 99999, 16, 512, 6.78, 5910, 50, "Dimensity 9400"),
    ("OPPO", "OPPO Find X8", "2024-11", 69999, 12, 256, 6.59, 5630, 50, "Dimensity 9400"),
    ("OPPO", "OPPO Find N3", "2023-10", 149999, 16, 512, 7.82, 4805, 48, "Snapdragon 8 Gen 2"),
    ("OPPO", "OPPO Find N3 Flip", "2023-10", 94999, 12, 256, 6.8, 4303, 50, "Dimensity 9200"),
    ("OPPO", "OPPO Find N2 Flip", "2023-02", 89999, 8, 256, 6.8, 4300, 50, "Dimensity 9000+"),
    ("OPPO", "OPPO Reno13 Pro 5G", "2025-01", 49999, 12, 256, 6.83, 5800, 50, "Dimensity 8350"),
    ("OPPO", "OPPO Reno13 5G", "2025-01", 37999, 8, 256, 6.59, 5600, 50, "Dimensity 8350"),
    ("OPPO", "OPPO Reno12 Pro 5G", "2024-07", 36999, 12, 256, 6.7, 5000, 50, "Dimensity 7300 Energy"),
    ("OPPO", "OPPO Reno12 5G", "2024-07", 32999, 8, 256, 6.7, 5000, 50, "Dimensity 7300 Energy"),
    ("OPPO", "OPPO Reno11 Pro 5G", "2024-01", 39999, 12, 256, 6.7, 4600, 50, "Dimensity 8200"),
    ("OPPO", "OPPO Reno11 5G", "2024-01", 29999, 8, 128, 6.7, 5000, 50, "Dimensity 7050"),
    ("OPPO", "OPPO Reno10 Pro+ 5G", "2023-07", 54999, 12, 256, 6.74, 4700, 50, "Snapdragon 8+ Gen 1"),
    ("OPPO", "OPPO Reno10 Pro 5G", "2023-07", 39999, 12, 256, 6.7, 4600, 50, "Snapdragon 778G"),
    ("OPPO", "OPPO Reno10 5G", "2023-07", 32999, 8, 256, 6.7, 5000, 64, "Dimensity 7050"),
    ("OPPO", "OPPO Reno8 Pro 5G", "2022-07", 45999, 12, 256, 6.7, 4500, 50, "Dimensity 8100-Max"),
    ("OPPO", "OPPO Reno8 5G", "2022-07", 29999, 8, 128, 6.43, 4500, 50, "Dimensity 1300"),
    ("OPPO", "OPPO F27 Pro+ 5G", "2024-06", 27999, 8, 128, 6.7, 5000, 64, "Dimensity 7050"),
    ("OPPO", "OPPO F27 5G", "2024-08", 22999, 8, 128, 6.67, 5000, 50, "Dimensity 6300"),
    ("OPPO", "OPPO F25 Pro 5G", "2024-02", 23999, 8, 128, 6.7, 5000, 64, "Dimensity 7050"),
    ("OPPO", "OPPO F23 5G", "2023-05", 24999, 8, 256, 6.72, 5000, 64, "Snapdragon 695"),
    ("OPPO", "OPPO A3 Pro 5G", "2024-04", 17999, 8, 128, 6.67, 5000, 50, "Dimensity 6300"),
    ("OPPO", "OPPO A3x 5G", "2024-08", 12499, 4, 64, 6.67, 5100, 8, "Dimensity 6300"),
    ("OPPO", "OPPO A79 5G", "2023-10", 19999, 8, 128, 6.72, 5000, 50, "Dimensity 6020"),
    ("OPPO", "OPPO A59 5G", "2023-12", 14999, 4, 128, 6.56, 5000, 13, "Dimensity 6020"),

    # === realme (28 models) ===
    ("realme", "realme GT 7 Pro", "2024-11", 59999, 12, 256, 6.78, 5800, 50, "Snapdragon 8 Elite"),
    ("realme", "realme GT 6", "2024-06", 40999, 12, 256, 6.78, 5500, 50, "Snapdragon 8s Gen 3"),
    ("realme", "realme GT 6T", "2024-05", 30999, 8, 128, 6.78, 5500, 50, "Snapdragon 7+ Gen 3"),
    ("realme", "realme GT 2 Pro", "2022-04", 49999, 8, 128, 6.7, 5000, 50, "Snapdragon 8 Gen 1"),
    ("realme", "realme GT Neo 3", "2022-04", 36999, 8, 128, 6.7, 5000, 50, "Dimensity 8100"),
    ("realme", "realme 14 Pro+ 5G", "2025-01", 29999, 8, 128, 6.83, 6000, 50, "Snapdragon 7s Gen 3"),
    ("realme", "realme 14 Pro 5G", "2025-01", 24999, 8, 128, 6.77, 6000, 50, "Dimensity 7300 Energy"),
    ("realme", "realme 13 Pro+ 5G", "2024-07", 32999, 8, 128, 6.7, 5000, 50, "Snapdragon 7s Gen 2"),
    ("realme", "realme 13 Pro 5G", "2024-07", 26999, 8, 128, 6.7, 5200, 50, "Snapdragon 7s Gen 2"),
    ("realme", "realme 13+ 5G", "2024-08", 22999, 8, 128, 6.67, 5000, 50, "Dimensity 7300 Energy"),
    ("realme", "realme 13 5G", "2024-08", 17999, 6, 128, 6.72, 5000, 50, "Dimensity 6300"),
    ("realme", "realme 12 Pro+ 5G", "2024-01", 29999, 8, 128, 6.7, 5000, 50, "Snapdragon 7s Gen 2"),
    ("realme", "realme 12 Pro 5G", "2024-01", 25999, 8, 128, 6.7, 5000, 50, "Snapdragon 6 Gen 1"),
    ("realme", "realme 12+ 5G", "2024-03", 20999, 8, 128, 6.67, 5000, 50, "Dimensity 7050"),
    ("realme", "realme 12 5G", "2024-03", 16999, 6, 128, 6.72, 5000, 108, "Dimensity 6100+"),
    ("realme", "realme 11 Pro+ 5G", "2023-06", 27999, 8, 256, 6.7, 5000, 200, "Dimensity 7050"),
    ("realme", "realme 11 Pro 5G", "2023-06", 23999, 8, 128, 6.7, 5000, 100, "Dimensity 7050"),
    ("realme", "realme 11 5G", "2023-08", 18999, 8, 128, 6.72, 5000, 108, "Dimensity 6100+"),
    ("realme", "realme 10 Pro+ 5G", "2022-12", 24999, 6, 128, 6.7, 5000, 108, "Dimensity 1080"),
    ("realme", "realme Narzo 80 Pro 5G", "2025-04", 19999, 8, 128, 6.77, 6000, 50, "Dimensity 7400"),
    ("realme", "realme Narzo 70 Pro 5G", "2024-03", 19999, 8, 128, 6.67, 5000, 50, "Dimensity 7050"),
    ("realme", "realme Narzo 70 Turbo 5G", "2024-09", 16999, 6, 128, 6.67, 5000, 50, "Dimensity 7300 Energy"),
    ("realme", "realme Narzo 70x 5G", "2024-04", 11999, 4, 128, 6.72, 5000, 50, "Dimensity 6100+"),
    ("realme", "realme Narzo 60 Pro 5G", "2023-07", 23999, 8, 128, 6.7, 5000, 100, "Dimensity 7050"),
    ("realme", "realme Narzo 60 5G", "2023-07", 17999, 8, 128, 6.43, 5000, 64, "Dimensity 6020"),
    ("realme", "realme P2 Pro 5G", "2024-09", 21999, 8, 128, 6.7, 5200, 50, "Snapdragon 7s Gen 2"),
    ("realme", "realme P1 Pro 5G", "2024-04", 21999, 8, 128, 6.7, 5000, 50, "Snapdragon 6 Gen 1"),
    ("realme", "realme P1 5G", "2024-04", 15999, 6, 128, 6.67, 5000, 50, "Dimensity 7050"),

    # === Motorola (24 models) ===
    ("Motorola", "Motorola Edge 50 Ultra", "2024-06", 59999, 12, 512, 6.7, 4500, 50, "Snapdragon 8s Gen 3"),
    ("Motorola", "Motorola Edge 50 Pro", "2024-04", 31999, 12, 256, 6.7, 4500, 50, "Snapdragon 7 Gen 3"),
    ("Motorola", "Motorola Edge 50 Fusion", "2024-05", 22999, 8, 128, 6.7, 5000, 50, "Snapdragon 7s Gen 2"),
    ("Motorola", "Motorola Edge 50 Neo", "2024-09", 23999, 8, 256, 6.4, 4310, 50, "Dimensity 7300"),
    ("Motorola", "Motorola Edge 40 Pro", "2023-04", 69999, 12, 256, 6.67, 4600, 50, "Snapdragon 8 Gen 2"),
    ("Motorola", "Motorola Edge 40", "2023-05", 29999, 8, 256, 6.55, 4400, 50, "Dimensity 8020"),
    ("Motorola", "Motorola Edge 40 Neo", "2023-09", 23999, 8, 128, 6.55, 5000, 50, "Dimensity 7030"),
    ("Motorola", "Motorola Edge 30 Ultra", "2022-09", 59999, 8, 128, 6.67, 4610, 200, "Snapdragon 8+ Gen 1"),
    ("Motorola", "Motorola Edge 30 Fusion", "2022-09", 42999, 8, 128, 6.55, 4400, 50, "Snapdragon 888+"),
    ("Motorola", "Motorola Edge 30 Pro", "2022-02", 49999, 8, 128, 6.7, 4800, 50, "Snapdragon 8 Gen 1"),
    ("Motorola", "Motorola Edge 30", "2022-05", 27999, 6, 128, 6.5, 4020, 50, "Snapdragon 778G+"),
    ("Motorola", "Motorola Edge 60 Pro", "2025-04", 29999, 8, 256, 6.67, 6000, 50, "Dimensity 8350 Extreme"),
    ("Motorola", "Motorola Razr 50 Ultra", "2024-07", 99999, 12, 512, 6.9, 4000, 50, "Snapdragon 8s Gen 3"),
    ("Motorola", "Motorola Razr 50", "2024-09", 64999, 8, 256, 6.9, 4200, 50, "Dimensity 7300X"),
    ("Motorola", "Motorola Razr 40 Ultra", "2023-07", 89999, 8, 256, 6.9, 3800, 12, "Snapdragon 8+ Gen 1"),
    ("Motorola", "Motorola Razr 40", "2023-07", 59999, 8, 256, 6.9, 4200, 64, "Snapdragon 7 Gen 1"),
    ("Motorola", "Moto G85 5G", "2024-07", 17999, 8, 128, 6.67, 5000, 50, "Snapdragon 6s Gen 3"),
    ("Motorola", "Moto G84 5G", "2023-09", 19999, 12, 256, 6.55, 5000, 50, "Snapdragon 695"),
    ("Motorola", "Moto G64 5G", "2024-04", 14999, 8, 128, 6.5, 6000, 50, "Dimensity 7025"),
    ("Motorola", "Moto G54 5G", "2023-09", 15999, 8, 128, 6.5, 6000, 50, "Dimensity 7020"),
    ("Motorola", "Moto G45 5G", "2024-08", 10999, 4, 128, 6.5, 5000, 50, "Snapdragon 6s Gen 3"),
    ("Motorola", "Moto G34 5G", "2024-01", 10999, 4, 128, 6.5, 5000, 50, "Snapdragon 695"),
    ("Motorola", "Moto G73 5G", "2023-03", 18999, 8, 128, 6.5, 5000, 50, "Dimensity 930"),
    ("Motorola", "Moto G24 Power", "2024-01", 8999, 4, 128, 6.56, 6000, 50, "Helio G85"),

    # === POCO (20 models) ===
    ("POCO", "POCO F7", "2025-06", 31999, 12, 256, 6.83, 6500, 50, "Snapdragon 8s Gen 4"),
    ("POCO", "POCO F6 Pro", "2024-05", 39999, 12, 256, 6.67, 5000, 50, "Snapdragon 8 Gen 2"),
    ("POCO", "POCO F6", "2024-05", 29999, 8, 256, 6.67, 5000, 50, "Snapdragon 8s Gen 3"),
    ("POCO", "POCO F5 Pro", "2023-05", 39999, 8, 256, 6.67, 5160, 64, "Snapdragon 8+ Gen 1"),
    ("POCO", "POCO F5", "2023-05", 29999, 8, 256, 6.67, 5000, 64, "Snapdragon 7+ Gen 2"),
    ("POCO", "POCO F4 GT", "2022-04", 49999, 8, 128, 6.67, 4700, 64, "Snapdragon 8 Gen 1"),
    ("POCO", "POCO F4 5G", "2022-06", 27999, 6, 128, 6.67, 4500, 64, "Snapdragon 870"),
    ("POCO", "POCO X7 Pro 5G", "2025-01", 27999, 8, 256, 6.67, 6550, 50, "Dimensity 8400 Ultra"),
    ("POCO", "POCO X6 Pro 5G", "2024-01", 26999, 8, 256, 6.67, 5000, 64, "Dimensity 8300 Ultra"),
    ("POCO", "POCO X6 5G", "2024-01", 21999, 8, 256, 6.67, 5100, 64, "Snapdragon 7s Gen 2"),
    ("POCO", "POCO X6 Neo 5G", "2024-03", 15999, 8, 128, 6.67, 5000, 108, "Dimensity 6080"),
    ("POCO", "POCO X5 Pro 5G", "2023-02", 22999, 6, 128, 6.67, 5000, 108, "Snapdragon 778G"),
    ("POCO", "POCO X5 5G", "2023-03", 18999, 6, 128, 6.67, 5000, 48, "Snapdragon 695"),
    ("POCO", "POCO M7 Pro 5G", "2024-12", 14999, 6, 128, 6.67, 5110, 50, "Dimensity 7025 Ultra"),
    ("POCO", "POCO M6 Pro 5G", "2024-01", 9999, 4, 128, 6.79, 5000, 50, "Snapdragon 4 Gen 2"),
    ("POCO", "POCO M6 Plus 5G", "2024-08", 13499, 6, 128, 6.79, 5030, 108, "Snapdragon 4 Gen 2 AE"),
    ("POCO", "POCO M6 5G", "2023-12", 10499, 4, 128, 6.74, 5000, 50, "Dimensity 6100+"),
    ("POCO", "POCO M5", "2022-09", 12499, 4, 64, 6.58, 5000, 50, "Helio G99"),
    ("POCO", "POCO C65", "2023-12", 8499, 4, 128, 6.74, 5000, 50, "Helio G85"),
    ("POCO", "POCO C61", "2024-03", 7499, 4, 64, 6.71, 5000, 8, "Helio G36"),

    # === Nothing & CMF (6 models) ===
    ("Nothing", "Nothing Phone (3)", "2025-07", 79999, 12, 256, 6.67, 5150, 50, "Snapdragon 8s Gen 4"),
    ("Nothing", "Nothing Phone (2)", "2023-07", 44999, 8, 128, 6.7, 4700, 50, "Snapdragon 8+ Gen 1"),
    ("Nothing", "Nothing Phone (2a) Plus", "2024-07", 27999, 8, 256, 6.7, 5000, 50, "Dimensity 7350 Pro"),
    ("Nothing", "Nothing Phone (2a)", "2024-03", 23999, 8, 128, 6.7, 5000, 50, "Dimensity 7200 Pro"),
    ("Nothing", "Nothing Phone (1)", "2022-07", 32999, 8, 128, 6.55, 4500, 50, "Snapdragon 778G+"),
    ("Nothing", "CMF Phone 1", "2024-07", 15999, 6, 128, 6.67, 5000, 50, "Dimensity 7300"),

    # === Honor (8 models) ===
    ("Honor", "Honor Magic6 Pro", "2024-01", 89999, 12, 512, 6.8, 5600, 50, "Snapdragon 8 Gen 3"),
    ("Honor", "Honor Magic5 Pro", "2023-03", 79999, 12, 512, 6.81, 5100, 50, "Snapdragon 8 Gen 2"),
    ("Honor", "Honor Magic V3", "2024-07", 149999, 16, 512, 7.92, 5150, 50, "Snapdragon 8 Gen 3"),
    ("Honor", "Honor 200 Pro", "2024-06", 57999, 12, 512, 6.78, 5200, 50, "Snapdragon 8s Gen 3"),
    ("Honor", "Honor 200", "2024-06", 34999, 8, 256, 6.7, 5200, 50, "Snapdragon 7 Gen 3"),
    ("Honor", "Honor 200 Lite", "2024-09", 17999, 8, 256, 6.7, 4500, 108, "Dimensity 6080"),
    ("Honor", "Honor 90 5G", "2023-09", 37999, 8, 256, 6.7, 5000, 200, "Snapdragon 7 Gen 1 Accelerated"),
    ("Honor", "Honor X9b 5G", "2024-02", 25999, 8, 256, 6.78, 5800, 108, "Snapdragon 6 Gen 1"),

    # === ASUS ROG / Zenfone (7 models) ===
    ("ASUS", "ASUS ROG Phone 8 Pro", "2024-01", 94999, 16, 512, 6.78, 5500, 50, "Snapdragon 8 Gen 3"),
    ("ASUS", "ASUS ROG Phone 8", "2024-01", 79999, 12, 256, 6.78, 5500, 50, "Snapdragon 8 Gen 3"),
    ("ASUS", "ASUS ROG Phone 7 Ultimate", "2023-04", 99999, 16, 512, 6.78, 6000, 50, "Snapdragon 8 Gen 2"),
    ("ASUS", "ASUS ROG Phone 7", "2023-04", 74999, 12, 256, 6.78, 6000, 50, "Snapdragon 8 Gen 2"),
    ("ASUS", "ASUS ROG Phone 6", "2022-07", 71999, 12, 256, 6.78, 6000, 50, "Snapdragon 8+ Gen 1"),
    ("ASUS", "ASUS Zenfone 11 Ultra", "2024-03", 79999, 12, 256, 6.78, 5500, 50, "Snapdragon 8 Gen 3"),
    ("ASUS", "ASUS Zenfone 10", "2023-06", 64999, 8, 128, 5.9, 4300, 50, "Snapdragon 8 Gen 2"),
]

LAPTOPS = [
    # === Apple (20 models - Normal/Business/Student) ===
    ("Apple", "Apple MacBook Air 13 (M1)", "Student", "2020-11", 84900, 8, 256, 13.3, "Apple M1 GPU (integrated)", 60, "Apple M1"),
    ("Apple", "Apple MacBook Air 13 (M2)", "General", "2022-07", 99900, 8, 256, 13.6, "Apple M2 GPU (integrated)", 60, "Apple M2"),
    ("Apple", "Apple MacBook Air 15 (M2)", "General", "2023-06", 134900, 8, 256, 15.3, "Apple M2 GPU (integrated)", 60, "Apple M2"),
    ("Apple", "Apple MacBook Air 13 (M3)", "General", "2024-03", 114900, 8, 256, 13.6, "Apple M3 GPU (integrated)", 60, "Apple M3"),
    ("Apple", "Apple MacBook Air 15 (M3)", "General", "2024-03", 134900, 8, 256, 15.3, "Apple M3 GPU (integrated)", 60, "Apple M3"),
    ("Apple", "Apple MacBook Air 13 (M4)", "General", "2025-03", 99900, 16, 256, 13.6, "Apple M4 GPU (integrated)", 60, "Apple M4"),
    ("Apple", "Apple MacBook Pro 13 (M2)", "General", "2022-06", 129900, 8, 256, 13.3, "Apple M2 GPU (integrated)", 60, "Apple M2"),
    ("Apple", "Apple MacBook Pro 14 (M1 Pro)", "Business", "2021-10", 194900, 16, 512, 14.2, "Apple M1 Pro GPU (integrated)", 120, "Apple M1 Pro"),
    ("Apple", "Apple MacBook Pro 16 (M1 Max)", "Business", "2021-10", 329900, 32, 1024, 16.2, "Apple M1 Max GPU (integrated)", 120, "Apple M1 Max"),
    ("Apple", "Apple MacBook Pro 14 (M2 Pro)", "Business", "2023-01", 199900, 16, 512, 14.2, "Apple M2 Pro GPU (integrated)", 120, "Apple M2 Pro"),
    ("Apple", "Apple MacBook Pro 16 (M2 Max)", "Business", "2023-01", 349900, 32, 1024, 16.2, "Apple M2 Max GPU (integrated)", 120, "Apple M2 Max"),
    ("Apple", "Apple MacBook Pro 14 (M3)", "Business", "2023-11", 169900, 8, 512, 14.2, "Apple M3 GPU (integrated)", 120, "Apple M3"),
    ("Apple", "Apple MacBook Pro 14 (M3 Pro)", "Business", "2023-11", 199900, 18, 512, 14.2, "Apple M3 Pro GPU (integrated)", 120, "Apple M3 Pro"),
    ("Apple", "Apple MacBook Pro 14 (M3 Max)", "Business", "2023-11", 319900, 36, 1024, 14.2, "Apple M3 Max GPU (integrated)", 120, "Apple M3 Max"),
    ("Apple", "Apple MacBook Pro 16 (M3 Pro)", "Business", "2023-11", 249900, 18, 512, 16.2, "Apple M3 Pro GPU (integrated)", 120, "Apple M3 Pro"),
    ("Apple", "Apple MacBook Pro 16 (M3 Max)", "Business", "2023-11", 399900, 36, 1024, 16.2, "Apple M3 Max GPU (integrated)", 120, "Apple M3 Max"),
    ("Apple", "Apple MacBook Pro 14 (M4)", "Business", "2024-11", 169900, 16, 512, 14.2, "Apple M4 GPU (integrated)", 120, "Apple M4"),
    ("Apple", "Apple MacBook Pro 14 (M4 Pro)", "Business", "2024-11", 199900, 24, 512, 14.2, "Apple M4 Pro GPU (integrated)", 120, "Apple M4 Pro"),
    ("Apple", "Apple MacBook Pro 16 (M4 Pro)", "Business", "2024-11", 249900, 24, 512, 16.2, "Apple M4 Pro GPU (integrated)", 120, "Apple M4 Pro"),
    ("Apple", "Apple MacBook Pro 16 (M4 Max)", "Business", "2024-11", 349900, 36, 1024, 16.2, "Apple M4 Max GPU (integrated)", 120, "Apple M4 Max"),

    # === Dell (32 models: 22 normal/business + 10 gaming) ===
    ("Dell", "Dell XPS 16 (9640)", "General", "2024-04", 269990, 32, 1024, 16.3, "NVIDIA GeForce RTX 4070", 120, "Intel Core Ultra 9 185H"),
    ("Dell", "Dell XPS 14 (9440)", "General", "2024-04", 199990, 16, 1024, 14.5, "NVIDIA GeForce RTX 4050", 120, "Intel Core Ultra 7 155H"),
    ("Dell", "Dell XPS 13 (9340)", "General", "2024-04", 139990, 16, 512, 13.4, "Intel Arc (integrated)", 120, "Intel Core Ultra 7 155H"),
    ("Dell", "Dell XPS 15 (9530)", "General", "2023-07", 209990, 16, 512, 15.6, "NVIDIA GeForce RTX 4050", 60, "Intel Core i7-13700H"),
    ("Dell", "Dell XPS 17 (9730)", "General", "2023-07", 289990, 32, 1024, 17.0, "NVIDIA GeForce RTX 4070", 60, "Intel Core i9-13900H"),
    ("Dell", "Dell XPS 13 Plus (9320)", "General", "2022-06", 159990, 16, 512, 13.4, "Intel Iris Xe", 60, "Intel Core i7-1260P"),
    ("Dell", "Dell Inspiron 16 Plus (7630)", "General", "2023-09", 119990, 16, 1024, 16.0, "NVIDIA GeForce RTX 4050", 120, "Intel Core i7-13700H"),
    ("Dell", "Dell Inspiron 14 Plus (7440)", "General", "2024-03", 105000, 16, 512, 14.0, "Intel Arc (integrated)", 60, "Intel Core Ultra 7 155H"),
    ("Dell", "Dell Inspiron 16 (5630)", "General", "2023-05", 79990, 16, 512, 16.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Dell", "Dell Inspiron 15 (3530)", "Student", "2023-08", 58990, 16, 512, 15.6, "Intel Iris Xe", 120, "Intel Core i5-1335U"),
    ("Dell", "Dell Inspiron 15 (3520)", "Student", "2023-05", 52990, 8, 512, 15.6, "Intel UHD (integrated)", 120, "Intel Core i5-1235U"),
    ("Dell", "Dell Inspiron 14 (5430)", "Student", "2023-08", 68990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Dell", "Dell Inspiron 13 (5330)", "General", "2023-06", 74990, 16, 512, 13.3, "Intel Iris Xe", 60, "Intel Core i5-1340P"),
    ("Dell", "Dell Inspiron 14 2-in-1 (7430)", "General", "2023-07", 82990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Dell", "Dell Latitude 9440 2-in-1", "Business", "2023-06", 219990, 32, 1024, 14.0, "Intel Iris Xe", 60, "Intel Core i7-1365U"),
    ("Dell", "Dell Latitude 7440", "Business", "2023-06", 149990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i7-1365U"),
    ("Dell", "Dell Latitude 7340", "Business", "2023-06", 139990, 16, 512, 13.3, "Intel Iris Xe", 60, "Intel Core i5-1345U"),
    ("Dell", "Dell Latitude 5540", "Business", "2023-07", 109990, 16, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Dell", "Dell Latitude 5440", "Business", "2023-08", 89990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i7-1355U"),
    ("Dell", "Dell Latitude 3540", "Business", "2023-07", 69990, 8, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Dell", "Dell Latitude 3440", "Business", "2023-07", 62990, 8, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Dell", "Dell Vostro 3520", "Business", "2023-04", 48990, 8, 512, 15.6, "Intel UHD (integrated)", 120, "Intel Core i3-1215U"),
    # Gaming
    ("Dell", "Alienware m18 R2", "Gaming", "2024-04", 359990, 32, 2048, 18.0, "NVIDIA GeForce RTX 4090", 165, "Intel Core i9-14900HX"),
    ("Dell", "Alienware m16 R2", "Gaming", "2024-05", 249990, 32, 1024, 16.0, "NVIDIA GeForce RTX 4070", 240, "Intel Core Ultra 9 185H"),
    ("Dell", "Alienware x16 R2", "Gaming", "2024-06", 289990, 32, 1024, 16.0, "NVIDIA GeForce RTX 4080", 240, "Intel Core Ultra 9 185H"),
    ("Dell", "Alienware x14 R2", "Gaming", "2023-06", 209990, 16, 512, 14.0, "NVIDIA GeForce RTX 4060", 165, "Intel Core i7-13620H"),
    ("Dell", "Alienware m15 R7", "Gaming", "2022-07", 189990, 16, 1024, 15.6, "NVIDIA GeForce RTX 3070 Ti", 240, "Intel Core i7-12700H"),
    ("Dell", "Dell G16 (7630)", "Gaming", "2023-07", 144990, 16, 1024, 16.0, "NVIDIA GeForce RTX 4060", 165, "Intel Core i7-13650HX"),
    ("Dell", "Dell G15 (5530)", "Gaming", "2023-06", 94990, 16, 512, 15.6, "NVIDIA GeForce RTX 3050", 120, "Intel Core i5-13450HX"),
    ("Dell", "Dell G15 5530 RTX 4050", "Gaming", "2023-08", 112990, 16, 1024, 15.6, "NVIDIA GeForce RTX 4050", 120, "Intel Core i7-13650HX"),
    ("Dell", "Dell G15 (5525) AMD", "Gaming", "2022-08", 84990, 16, 512, 15.6, "NVIDIA GeForce RTX 3050", 120, "AMD Ryzen 5 6600H"),
    ("Dell", "Dell G15 (5520) Intel", "Gaming", "2022-06", 79990, 8, 512, 15.6, "NVIDIA GeForce RTX 3050", 120, "Intel Core i5-12500H"),

    # === Lenovo (36 models: 24 normal/business + 12 gaming) ===
    ("Lenovo", "Lenovo ThinkPad X1 Carbon Gen 12", "Business", "2024-04", 214990, 32, 1024, 14.0, "Intel Arc (integrated)", 60, "Intel Core Ultra 7 155U"),
    ("Lenovo", "Lenovo ThinkPad X1 Carbon Gen 11", "Business", "2023-05", 189990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i7-1355U"),
    ("Lenovo", "Lenovo ThinkPad X1 Carbon Gen 10", "Business", "2022-06", 169990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i7-1260P"),
    ("Lenovo", "Lenovo ThinkPad X1 Yoga Gen 8", "Business", "2023-06", 204990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i7-1355U"),
    ("Lenovo", "Lenovo ThinkPad X1 Nano Gen 3", "Business", "2023-07", 179990, 16, 512, 13.0, "Intel Iris Xe", 60, "Intel Core i7-1360P"),
    ("Lenovo", "Lenovo ThinkPad T14 Gen 4", "Business", "2023-08", 109990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1345U"),
    ("Lenovo", "Lenovo ThinkPad T14s Gen 4", "Business", "2023-09", 124990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i7-1355U"),
    ("Lenovo", "Lenovo ThinkPad T16 Gen 2", "Business", "2023-08", 119990, 16, 512, 16.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Lenovo", "Lenovo ThinkPad E14 Gen 5", "Business", "2023-09", 71990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Lenovo", "Lenovo ThinkPad E16 Gen 1", "Business", "2023-09", 74990, 16, 512, 16.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Lenovo", "Lenovo ThinkPad L14 Gen 4", "Business", "2023-07", 68990, 16, 512, 14.0, "AMD Radeon (integrated)", 60, "AMD Ryzen 5 7530U"),
    ("Lenovo", "Lenovo ThinkPad P14s Gen 4", "Business", "2023-10", 134990, 32, 1024, 14.0, "NVIDIA RTX A500", 60, "Intel Core i7-1370P"),
    ("Lenovo", "Lenovo ThinkBook 14 Gen 6", "Business", "2023-11", 64990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Lenovo", "Lenovo ThinkBook 16 Gen 6", "Business", "2023-11", 69990, 16, 512, 16.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Lenovo", "Lenovo Yoga 9i Gen 9", "General", "2024-04", 174990, 16, 1024, 14.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 7 155H"),
    ("Lenovo", "Lenovo Yoga Pro 9i Gen 9", "General", "2024-05", 219990, 32, 1024, 16.0, "NVIDIA GeForce RTX 4060", 165, "Intel Core Ultra 9 185H"),
    ("Lenovo", "Lenovo Yoga 7i Gen 9", "General", "2024-03", 104990, 16, 512, 14.0, "Intel Arc (integrated)", 60, "Intel Core Ultra 7 155H"),
    ("Lenovo", "Lenovo Yoga Slim 7x", "General", "2024-06", 139990, 16, 1024, 14.5, "Qualcomm Adreno (integrated)", 90, "Snapdragon X Elite"),
    ("Lenovo", "Lenovo Yoga Slim 6", "General", "2023-08", 78990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-13500H"),
    ("Lenovo", "Lenovo IdeaPad Slim 5 (16)", "General", "2024-04", 76990, 16, 512, 16.0, "Intel Iris Xe", 60, "Intel Core i5-13500H"),
    ("Lenovo", "Lenovo IdeaPad Slim 5", "General", "2024-03", 71990, 16, 512, 14.0, "AMD Radeon (integrated)", 60, "AMD Ryzen 7 7730U"),
    ("Lenovo", "Lenovo IdeaPad Slim 3", "Student", "2024-01", 52990, 16, 512, 15.6, "Intel UHD (integrated)", 60, "Intel Core i5-13420H"),
    ("Lenovo", "Lenovo IdeaPad Slim 3 (14)", "Student", "2023-06", 45990, 8, 512, 14.0, "AMD Radeon (integrated)", 60, "AMD Ryzen 5 7520U"),
    ("Lenovo", "Lenovo IdeaPad 1", "Student", "2023-04", 36990, 8, 512, 15.6, "AMD Radeon (integrated)", 60, "AMD Ryzen 3 7320U"),
    # Gaming
    ("Lenovo", "Lenovo Legion Pro 7i Gen 9", "Gaming", "2024-05", 279990, 32, 1024, 16.0, "NVIDIA GeForce RTX 4080", 240, "Intel Core i9-14900HX"),
    ("Lenovo", "Lenovo Legion Pro 5i Gen 9", "Gaming", "2024-04", 179990, 16, 1024, 16.0, "NVIDIA GeForce RTX 4070", 240, "Intel Core i7-14700HX"),
    ("Lenovo", "Lenovo Legion 7i Gen 9", "Gaming", "2024-05", 219990, 32, 1024, 16.0, "NVIDIA GeForce RTX 4070", 240, "Intel Core i9-14900HX"),
    ("Lenovo", "Lenovo Legion 5i Gen 9", "Gaming", "2024-06", 159990, 16, 1024, 16.0, "NVIDIA GeForce RTX 4060", 165, "Intel Core i7-14650HX"),
    ("Lenovo", "Lenovo Legion Slim 5 (16)", "Gaming", "2023-09", 129990, 16, 512, 16.0, "NVIDIA GeForce RTX 4060", 165, "AMD Ryzen 7 7840HS"),
    ("Lenovo", "Lenovo Legion Slim 5 (14)", "Gaming", "2023-10", 139990, 16, 1024, 14.5, "NVIDIA GeForce RTX 4060", 120, "AMD Ryzen 7 7840HS"),
    ("Lenovo", "Lenovo Legion 5 Pro (2022)", "Gaming", "2022-07", 134990, 16, 512, 16.0, "NVIDIA GeForce RTX 3060", 165, "AMD Ryzen 7 6800H"),
    ("Lenovo", "Lenovo LOQ 15IRX9", "Gaming", "2024-05", 79990, 12, 512, 15.6, "NVIDIA GeForce RTX 3050", 144, "Intel Core i5-12450HX"),
    ("Lenovo", "Lenovo LOQ 15IRX9 RTX 4050", "Gaming", "2024-05", 89990, 16, 512, 15.6, "NVIDIA GeForce RTX 4050", 144, "Intel Core i5-13450HX"),
    ("Lenovo", "Lenovo LOQ 15ARP9", "Gaming", "2024-06", 84990, 16, 512, 15.6, "NVIDIA GeForce RTX 4050", 144, "AMD Ryzen 7 7435HS"),
    ("Lenovo", "Lenovo LOQ 15IAX9", "Gaming", "2024-03", 69990, 12, 512, 15.6, "NVIDIA GeForce RTX 2050", 144, "Intel Core i5-12450HX"),
    ("Lenovo", "Lenovo IdeaPad Gaming 3", "Gaming", "2022-08", 59990, 8, 512, 15.6, "NVIDIA GeForce RTX 3050", 120, "AMD Ryzen 5 5600H"),

    # === HP (30 models: 20 normal/business + 10 gaming) ===
    ("HP", "HP Spectre x360 16", "General", "2024-03", 189999, 32, 1024, 16.0, "NVIDIA GeForce RTX 4050", 120, "Intel Core Ultra 7 155H"),
    ("HP", "HP Spectre x360 14", "General", "2024-02", 164999, 16, 1024, 14.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 7 155H"),
    ("HP", "HP Spectre x360 13.5", "General", "2022-07", 139999, 16, 512, 13.5, "Intel Iris Xe", 60, "Intel Core i7-1254U"),
    ("HP", "HP Envy x360 16", "General", "2024-04", 124999, 16, 512, 16.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 7 155U"),
    ("HP", "HP Envy x360 14", "General", "2024-02", 109999, 16, 512, 14.0, "Intel Arc (integrated)", 60, "Intel Core Ultra 5 125U"),
    ("HP", "HP Envy 16", "General", "2023-07", 149999, 16, 1024, 16.0, "NVIDIA GeForce RTX 4060", 120, "Intel Core i7-13700H"),
    ("HP", "HP Pavilion Plus 16", "General", "2023-11", 99990, 16, 512, 16.0, "NVIDIA GeForce RTX 3050", 120, "Intel Core i7-13700H"),
    ("HP", "HP Pavilion Plus 14", "General", "2023-11", 84990, 16, 512, 14.0, "Intel Iris Xe", 120, "Intel Core i5-13500H"),
    ("HP", "HP Pavilion 15", "General", "2023-07", 66990, 16, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("HP", "HP Pavilion 14", "General", "2023-06", 62990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("HP", "HP Pavilion Aero 13", "General", "2023-09", 69990, 16, 512, 13.3, "AMD Radeon (integrated)", 60, "AMD Ryzen 5 7535U"),
    ("HP", "HP Pavilion x360 14", "General", "2023-05", 68990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("HP", "HP 15s (Core i5)", "Student", "2023-06", 54990, 16, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("HP", "HP 15s (Ryzen 5)", "Student", "2023-05", 48990, 16, 512, 15.6, "AMD Radeon (integrated)", 60, "AMD Ryzen 5 5500U"),
    ("HP", "HP 14s", "Student", "2023-04", 43990, 8, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i3-1215U"),
    ("HP", "HP EliteBook 1040 G10", "Business", "2023-09", 169000, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i7-1365U"),
    ("HP", "HP EliteBook 840 G10", "Business", "2023-08", 132000, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("HP", "HP EliteBook 640 G10", "Business", "2023-08", 98000, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("HP", "HP ProBook 450 G10", "Business", "2023-07", 78000, 16, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("HP", "HP ProBook 440 G10", "Business", "2023-07", 74000, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    # Gaming
    ("HP", "HP OMEN 17", "Gaming", "2023-06", 249999, 32, 1024, 17.3, "NVIDIA GeForce RTX 4080", 240, "Intel Core i9-13900HX"),
    ("HP", "HP OMEN 16 (2024)", "Gaming", "2024-03", 169999, 16, 1024, 16.1, "NVIDIA GeForce RTX 4070", 165, "Intel Core i7-14700HX"),
    ("HP", "HP OMEN 16", "Gaming", "2023-10", 164999, 16, 1024, 16.1, "NVIDIA GeForce RTX 4060", 165, "Intel Core i7-13700HX"),
    ("HP", "HP OMEN Transcend 16", "Gaming", "2023-08", 189999, 16, 1024, 16.0, "NVIDIA GeForce RTX 4070", 240, "Intel Core i7-13700HX"),
    ("HP", "HP OMEN Transcend 14", "Gaming", "2024-04", 174999, 16, 1024, 14.0, "NVIDIA GeForce RTX 4060", 120, "Intel Core Ultra 7 155H"),
    ("HP", "HP Victus 16 (Ryzen 7)", "Gaming", "2023-09", 89990, 16, 512, 16.1, "NVIDIA GeForce RTX 4050", 144, "AMD Ryzen 7 7840HS"),
    ("HP", "HP Victus 16 (Core i7)", "Gaming", "2023-08", 104990, 16, 1024, 16.1, "NVIDIA GeForce RTX 4060", 144, "Intel Core i7-13700H"),
    ("HP", "HP Victus 15", "Gaming", "2023-08", 76990, 8, 512, 15.6, "NVIDIA GeForce RTX 3050", 144, "Intel Core i5-13420H"),
    ("HP", "HP Victus 15 (Ryzen 5)", "Gaming", "2023-06", 64990, 8, 512, 15.6, "AMD Radeon RX 6500M", 144, "AMD Ryzen 5 5600H"),
    ("HP", "HP Victus 15 RTX 2050", "Gaming", "2023-07", 57990, 8, 512, 15.6, "NVIDIA GeForce RTX 2050", 144, "Intel Core i5-12450H"),

    # === ASUS (35 models: 20 normal/business + 15 gaming) ===
    ("ASUS", "ASUS Zenbook S 16 OLED", "General", "2024-07", 169990, 32, 1024, 16.0, "AMD Radeon 890M (integrated)", 120, "AMD Ryzen AI 9 365"),
    ("ASUS", "ASUS Zenbook S 14", "General", "2024-09", 149990, 32, 1024, 14.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 7 258V"),
    ("ASUS", "ASUS Zenbook 14 OLED (UX3405)", "General", "2024-03", 109990, 16, 512, 14.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 7 155H"),
    ("ASUS", "ASUS Zenbook Duo (2024)", "General", "2024-04", 169990, 32, 1024, 14.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 9 185H"),
    ("ASUS", "ASUS Zenbook Pro 14 OLED", "General", "2023-06", 189990, 16, 1024, 14.5, "NVIDIA GeForce RTX 4060", 120, "Intel Core i9-13900H"),
    ("ASUS", "ASUS Zenbook 14 Flip OLED", "General", "2023-05", 119990, 16, 512, 14.0, "Intel Iris Xe", 90, "Intel Core i7-1360P"),
    ("ASUS", "ASUS Vivobook S 15 OLED (Snapdragon)", "General", "2024-06", 114990, 16, 1024, 15.6, "Qualcomm Adreno (integrated)", 120, "Snapdragon X Elite"),
    ("ASUS", "ASUS Vivobook S 14 OLED", "General", "2024-04", 89990, 16, 1024, 14.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 5 125H"),
    ("ASUS", "ASUS Vivobook Pro 15 OLED", "General", "2023-07", 89990, 16, 512, 15.6, "NVIDIA GeForce RTX 3050", 120, "AMD Ryzen 7 5800H"),
    ("ASUS", "ASUS Vivobook Pro 16 OLED", "General", "2023-08", 124990, 16, 1024, 16.0, "NVIDIA GeForce RTX 4050", 120, "Intel Core i9-13900H"),
    ("ASUS", "ASUS Vivobook 16", "General", "2024-02", 59990, 16, 512, 16.0, "Intel UHD (integrated)", 60, "Intel Core i5-13420H"),
    ("ASUS", "ASUS Vivobook 15 (X1502)", "Student", "2023-06", 44990, 8, 512, 15.6, "Intel UHD (integrated)", 60, "Intel Core i5-1235U"),
    ("ASUS", "ASUS Vivobook 15 (X1504)", "Student", "2023-09", 54990, 16, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("ASUS", "ASUS Vivobook 14 (X1404)", "Student", "2023-08", 49990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("ASUS", "ASUS Vivobook Go 15", "Student", "2023-05", 38990, 8, 512, 15.6, "AMD Radeon (integrated)", 60, "AMD Ryzen 3 7320U"),
    ("ASUS", "ASUS Vivobook Go 14", "Student", "2023-05", 34990, 8, 256, 14.0, "Intel UHD (integrated)", 60, "Intel Core i3-N305"),
    ("ASUS", "ASUS ExpertBook B9 OLED", "Business", "2023-08", 199990, 32, 1024, 14.0, "Intel Iris Xe", 60, "Intel Core i7-1355U"),
    ("ASUS", "ASUS ExpertBook B5", "Business", "2023-07", 119990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i7-1360P"),
    ("ASUS", "ASUS ExpertBook B3 Flip", "Business", "2023-06", 89990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("ASUS", "ASUS ExpertBook B1", "Business", "2023-05", 52990, 8, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1235U"),
    # Gaming
    ("ASUS", "ASUS ROG Strix SCAR 18 (2024)", "Gaming", "2024-02", 349990, 32, 2048, 18.0, "NVIDIA GeForce RTX 4090", 240, "Intel Core i9-14900HX"),
    ("ASUS", "ASUS ROG Strix SCAR 16", "Gaming", "2024-02", 289990, 32, 2048, 16.0, "NVIDIA GeForce RTX 4080", 240, "Intel Core i9-14900HX"),
    ("ASUS", "ASUS ROG Strix G18 (2024)", "Gaming", "2024-03", 189990, 16, 1024, 18.0, "NVIDIA GeForce RTX 4070", 240, "Intel Core i9-14900HX"),
    ("ASUS", "ASUS ROG Strix G16", "Gaming", "2024-02", 139990, 16, 1024, 16.0, "NVIDIA GeForce RTX 4060", 165, "Intel Core i7-13650HX"),
    ("ASUS", "ASUS ROG Zephyrus G16 (2024)", "Gaming", "2024-03", 219990, 32, 1024, 16.0, "NVIDIA GeForce RTX 4070", 240, "Intel Core Ultra 9 185H"),
    ("ASUS", "ASUS ROG Zephyrus G14 (2024)", "Gaming", "2024-03", 174990, 16, 1024, 14.0, "NVIDIA GeForce RTX 4060", 120, "AMD Ryzen 9 8945HS"),
    ("ASUS", "ASUS ROG Zephyrus M16 (2023)", "Gaming", "2023-04", 199990, 16, 1024, 16.0, "NVIDIA GeForce RTX 4070", 240, "Intel Core i9-13900H"),
    ("ASUS", "ASUS ROG Flow X16", "Gaming", "2023-05", 184990, 16, 1024, 16.0, "NVIDIA GeForce RTX 4060", 240, "Intel Core i9-13900H"),
    ("ASUS", "ASUS ROG Flow X13", "Gaming", "2023-05", 154990, 16, 512, 13.4, "NVIDIA GeForce RTX 4050", 165, "AMD Ryzen 9 7940HS"),
    ("ASUS", "ASUS ROG Flow Z13", "Gaming", "2023-04", 149990, 16, 512, 13.4, "NVIDIA GeForce RTX 4050", 165, "Intel Core i9-13900H"),
    ("ASUS", "ASUS TUF Gaming A16 Advantage", "Gaming", "2023-07", 114990, 16, 512, 16.0, "AMD Radeon RX 7600S", 165, "AMD Ryzen 7 7735HS"),
    ("ASUS", "ASUS TUF Gaming A15", "Gaming", "2024-01", 104990, 16, 512, 15.6, "NVIDIA GeForce RTX 4060", 144, "AMD Ryzen 7 7735HS"),
    ("ASUS", "ASUS TUF Gaming F15", "Gaming", "2023-06", 74990, 16, 512, 15.6, "NVIDIA GeForce RTX 3050", 144, "Intel Core i5-11400H"),
    ("ASUS", "ASUS TUF Gaming A17", "Gaming", "2023-05", 89990, 16, 512, 17.3, "NVIDIA GeForce RTX 3050", 144, "AMD Ryzen 7 6800H"),
    ("ASUS", "ASUS TUF Gaming F17", "Gaming", "2023-05", 84990, 16, 512, 17.3, "NVIDIA GeForce RTX 3050", 144, "Intel Core i5-12500H"),

    # === Acer (30 models: 16 normal/business + 14 gaming) ===
    ("Acer", "Acer Swift 14 AI", "General", "2024-09", 109990, 16, 1024, 14.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 7 155H"),
    ("Acer", "Acer Swift Go 16 OLED", "General", "2024-02", 89990, 16, 512, 16.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 5 125H"),
    ("Acer", "Acer Swift Go 14", "General", "2023-09", 74990, 16, 512, 14.0, "Intel Iris Xe", 90, "Intel Core i5-13500H"),
    ("Acer", "Acer Swift X 14", "General", "2023-07", 114990, 16, 1024, 14.5, "NVIDIA GeForce RTX 4050", 120, "Intel Core i7-13700H"),
    ("Acer", "Acer Swift Edge 16", "General", "2023-08", 104990, 16, 1024, 16.0, "AMD Radeon 780M (integrated)", 120, "AMD Ryzen 7 7840U"),
    ("Acer", "Acer Aspire 5 (A515-58M)", "Student", "2023-08", 54990, 16, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Acer", "Acer Aspire 5 (A514)", "Student", "2023-07", 51990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Acer", "Acer Aspire 3 (A315)", "Student", "2023-05", 39990, 8, 512, 15.6, "AMD Radeon (integrated)", 60, "AMD Ryzen 3 7320U"),
    ("Acer", "Acer Aspire 3 Spin 14", "Student", "2023-06", 44990, 8, 256, 14.0, "Intel UHD (integrated)", 60, "Intel Core i3-N305"),
    ("Acer", "Acer Aspire Vero 15", "General", "2023-09", 64990, 16, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Acer", "Acer TravelMate P6", "Business", "2023-11", 129990, 16, 1024, 14.0, "Intel Iris Xe", 60, "Intel Core i7-1355U"),
    ("Acer", "Acer TravelMate P4", "Business", "2023-10", 84990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Acer", "Acer TravelMate P2", "Business", "2023-10", 62990, 16, 512, 14.0, "Intel UHD (integrated)", 60, "Intel Core i5-1335U"),
    ("Acer", "Acer TravelMate Spin B3", "Student", "2023-04", 36990, 8, 256, 11.6, "Intel UHD (integrated)", 60, "Intel Celeron N4500"),
    ("Acer", "Acer One 14", "Student", "2023-05", 29990, 8, 256, 14.0, "AMD Radeon (integrated)", 60, "AMD Ryzen 3 3250U"),
    ("Acer", "Acer Extensa 15", "Student", "2023-04", 34990, 8, 512, 15.6, "Intel UHD (integrated)", 60, "Intel Core i3-N305"),
    # Gaming
    ("Acer", "Acer Predator Helios 18", "Gaming", "2024-03", 299999, 32, 2048, 18.0, "NVIDIA GeForce RTX 4080", 250, "Intel Core i9-14900HX"),
    ("Acer", "Acer Predator Helios 16", "Gaming", "2023-06", 229999, 32, 1024, 16.0, "NVIDIA GeForce RTX 4070", 240, "Intel Core i9-13900HX"),
    ("Acer", "Acer Predator Helios Neo 18", "Gaming", "2024-04", 179999, 16, 1024, 18.0, "NVIDIA GeForce RTX 4070", 165, "Intel Core i7-14700HX"),
    ("Acer", "Acer Predator Helios Neo 16", "Gaming", "2024-03", 139999, 16, 1024, 16.0, "NVIDIA GeForce RTX 4060", 165, "Intel Core i7-14700HX"),
    ("Acer", "Acer Predator Triton 17 X", "Gaming", "2023-07", 349999, 32, 2048, 17.0, "NVIDIA GeForce RTX 4090", 250, "Intel Core i9-13900HX"),
    ("Acer", "Acer Predator Triton 14", "Gaming", "2023-08", 189999, 16, 1024, 14.0, "NVIDIA GeForce RTX 4070", 250, "Intel Core i7-13700H"),
    ("Acer", "Acer Nitro 17", "Gaming", "2024-03", 139990, 16, 1024, 17.3, "NVIDIA GeForce RTX 4060", 165, "Intel Core i7-14700HX"),
    ("Acer", "Acer Nitro 16", "Gaming", "2024-02", 114990, 16, 512, 16.0, "NVIDIA GeForce RTX 4060", 165, "AMD Ryzen 7 7840HS"),
    ("Acer", "Acer Nitro V 16", "Gaming", "2024-04", 89990, 16, 512, 16.0, "NVIDIA GeForce RTX 4050", 165, "AMD Ryzen 7 8845HS"),
    ("Acer", "Acer Nitro V 15", "Gaming", "2024-01", 69990, 16, 512, 15.6, "NVIDIA GeForce RTX 2050", 144, "Intel Core i5-13420H"),
    ("Acer", "Acer Nitro V 15 RTX 4050", "Gaming", "2024-02", 79990, 16, 512, 15.6, "NVIDIA GeForce RTX 4050", 144, "Intel Core i5-13420H"),
    ("Acer", "Acer Nitro 5 (Ryzen 7)", "Gaming", "2022-08", 78990, 16, 512, 15.6, "NVIDIA GeForce RTX 3050", 144, "AMD Ryzen 7 5800H"),
    ("Acer", "Acer Nitro 5 (Core i5)", "Gaming", "2022-06", 67990, 8, 512, 15.6, "NVIDIA GeForce GTX 1650", 144, "Intel Core i5-11400H"),
    ("Acer", "Acer Aspire 7 Gaming", "Gaming", "2023-06", 62990, 16, 512, 15.6, "NVIDIA GeForce RTX 3050", 144, "Intel Core i5-12450H"),

    # === MSI (28 models: 8 normal + 20 gaming) ===
    ("MSI", "MSI Prestige 16 AI Evo", "General", "2024-03", 139990, 32, 1024, 16.0, "Intel Arc (integrated)", 60, "Intel Core Ultra 7 155H"),
    ("MSI", "MSI Prestige 14 AI Evo", "General", "2024-03", 119990, 16, 1024, 14.0, "Intel Arc (integrated)", 60, "Intel Core Ultra 5 125H"),
    ("MSI", "MSI Prestige 13 AI Evo", "General", "2024-04", 124990, 16, 1024, 13.3, "Intel Arc (integrated)", 60, "Intel Core Ultra 7 155H"),
    ("MSI", "MSI Modern 15", "Student", "2023-05", 49990, 16, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1235U"),
    ("MSI", "MSI Modern 14", "Student", "2023-04", 42990, 8, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i3-1215U"),
    ("MSI", "MSI Summit E16 Flip", "Business", "2023-07", 179990, 32, 1024, 16.0, "NVIDIA GeForce RTX 4060", 165, "Intel Core i7-1360P"),
    ("MSI", "MSI Summit E14 Flip", "Business", "2023-06", 149990, 16, 1024, 14.0, "Intel Iris Xe", 60, "Intel Core i7-1360P"),
    ("MSI", "MSI Commercial 14", "Business", "2023-10", 79990, 16, 512, 14.0, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    # Gaming
    ("MSI", "MSI Titan 18 HX", "Gaming", "2024-02", 449990, 64, 4096, 18.0, "NVIDIA GeForce RTX 4090", 120, "Intel Core i9-14900HX"),
    ("MSI", "MSI Raider GE78 HX", "Gaming", "2023-07", 329990, 32, 2048, 17.0, "NVIDIA GeForce RTX 4080", 240, "Intel Core i9-13980HX"),
    ("MSI", "MSI Raider GE68 HX", "Gaming", "2024-03", 249990, 32, 2048, 16.0, "NVIDIA GeForce RTX 4070", 240, "Intel Core i9-14900HX"),
    ("MSI", "MSI Stealth 18 AI Studio", "Gaming", "2024-05", 359990, 32, 2048, 18.0, "NVIDIA GeForce RTX 4080", 120, "Intel Core Ultra 9 185H"),
    ("MSI", "MSI Stealth 16 AI Studio", "Gaming", "2024-04", 299990, 32, 2048, 16.0, "NVIDIA GeForce RTX 4070", 240, "Intel Core Ultra 9 185H"),
    ("MSI", "MSI Stealth 14 AI Studio", "Gaming", "2024-04", 219990, 16, 1024, 14.0, "NVIDIA GeForce RTX 4060", 120, "Intel Core Ultra 7 155H"),
    ("MSI", "MSI Vector 17 HX", "Gaming", "2024-03", 229990, 32, 1024, 17.0, "NVIDIA GeForce RTX 4080", 240, "Intel Core i9-14900HX"),
    ("MSI", "MSI Vector 16 HX", "Gaming", "2024-03", 179990, 16, 1024, 16.0, "NVIDIA GeForce RTX 4070", 240, "Intel Core i7-14700HX"),
    ("MSI", "MSI Crosshair 16 HX", "Gaming", "2024-04", 139990, 16, 1024, 16.0, "NVIDIA GeForce RTX 4060", 144, "Intel Core i7-14700HX"),
    ("MSI", "MSI Pulse 16 AI", "Gaming", "2024-05", 149990, 16, 1024, 16.0, "NVIDIA GeForce RTX 4060", 240, "Intel Core Ultra 7 155H"),
    ("MSI", "MSI Sword 16 HX", "Gaming", "2024-03", 119990, 16, 1024, 16.0, "NVIDIA GeForce RTX 4060", 144, "Intel Core i7-14700HX"),
    ("MSI", "MSI Katana 17", "Gaming", "2024-02", 124990, 16, 1024, 17.3, "NVIDIA GeForce RTX 4060", 144, "Intel Core i7-13620H"),
    ("MSI", "MSI Katana 15", "Gaming", "2024-01", 109990, 16, 1024, 15.6, "NVIDIA GeForce RTX 4060", 144, "Intel Core i7-13620H"),
    ("MSI", "MSI Katana 15 RTX 4050", "Gaming", "2023-06", 89990, 16, 512, 15.6, "NVIDIA GeForce RTX 4050", 144, "Intel Core i7-12650H"),
    ("MSI", "MSI Cyborg 15", "Gaming", "2024-02", 79990, 16, 512, 15.6, "NVIDIA GeForce RTX 4060", 144, "Intel Core i7-12650H"),
    ("MSI", "MSI Cyborg 15 RTX 4050", "Gaming", "2023-05", 69990, 16, 512, 15.6, "NVIDIA GeForce RTX 4050", 144, "Intel Core i5-12450H"),
    ("MSI", "MSI Cyborg 14", "Gaming", "2024-03", 74990, 16, 512, 14.0, "NVIDIA GeForce RTX 4050", 144, "Intel Core i7-13620H"),
    ("MSI", "MSI Thin 15 (B13UC)", "Gaming", "2023-06", 59990, 8, 512, 15.6, "NVIDIA GeForce RTX 3050", 144, "Intel Core i5-13420H"),
    ("MSI", "MSI Thin GF63", "Gaming", "2022-07", 52990, 8, 512, 15.6, "NVIDIA GeForce GTX 1650", 144, "Intel Core i5-11400H"),
    ("MSI", "MSI Bravo 15", "Gaming", "2023-08", 68990, 16, 512, 15.6, "AMD Radeon RX 6550M", 144, "AMD Ryzen 7 7735HS"),

    # === Samsung (12 models) ===
    ("Samsung", "Samsung Galaxy Book4 Ultra", "General", "2024-03", 239990, 32, 1024, 16.0, "NVIDIA GeForce RTX 4070", 120, "Intel Core Ultra 9 185H"),
    ("Samsung", "Samsung Galaxy Book4 Pro 360", "General", "2024-03", 179990, 16, 1024, 16.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 7 155H"),
    ("Samsung", "Samsung Galaxy Book4 Pro", "General", "2024-03", 155990, 16, 512, 14.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 7 155H"),
    ("Samsung", "Samsung Galaxy Book4 360", "General", "2024-02", 114990, 16, 512, 15.6, "Intel Iris Xe", 60, "Intel Core 7 150U"),
    ("Samsung", "Samsung Galaxy Book4", "General", "2024-02", 63990, 16, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Samsung", "Samsung Galaxy Book3 Ultra", "General", "2023-03", 229990, 32, 1024, 16.0, "NVIDIA GeForce RTX 4070", 120, "Intel Core i9-13900H"),
    ("Samsung", "Samsung Galaxy Book3 Pro 360", "General", "2023-03", 159990, 16, 512, 16.0, "Intel Iris Xe", 120, "Intel Core i7-1360P"),
    ("Samsung", "Samsung Galaxy Book3 Pro", "General", "2023-03", 139990, 16, 512, 14.0, "Intel Iris Xe", 120, "Intel Core i7-1360P"),
    ("Samsung", "Samsung Galaxy Book3 360", "General", "2023-03", 99990, 16, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1340P"),
    ("Samsung", "Samsung Galaxy Book3", "Student", "2023-05", 56990, 8, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1335U"),
    ("Samsung", "Samsung Galaxy Book2 Pro", "General", "2022-04", 109990, 16, 512, 13.3, "Intel Iris Xe", 60, "Intel Core i7-1260P"),
    ("Samsung", "Samsung Galaxy Book2", "Student", "2022-04", 49990, 8, 512, 15.6, "Intel Iris Xe", 60, "Intel Core i5-1235U"),

    # === Microsoft (14 models) ===
    ("Microsoft", "Microsoft Surface Laptop Studio 2", "Business", "2023-10", 209999, 16, 512, 14.4, "NVIDIA GeForce RTX 4050", 120, "Intel Core i7-13700H"),
    ("Microsoft", "Microsoft Surface Laptop Studio", "Business", "2021-10", 169999, 16, 512, 14.4, "NVIDIA GeForce RTX 3050 Ti", 120, "Intel Core i7-11370H"),
    ("Microsoft", "Microsoft Surface Laptop 7 (15-inch)", "General", "2024-06", 139999, 16, 512, 15.0, "Qualcomm Adreno (integrated)", 120, "Snapdragon X Elite"),
    ("Microsoft", "Microsoft Surface Laptop 7", "General", "2024-06", 116999, 16, 256, 13.8, "Qualcomm Adreno (integrated)", 120, "Snapdragon X Plus"),
    ("Microsoft", "Microsoft Surface Laptop 6 (15-inch)", "Business", "2024-04", 154999, 16, 512, 15.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 7 165H"),
    ("Microsoft", "Microsoft Surface Laptop 6", "Business", "2024-04", 129999, 16, 256, 13.5, "Intel Arc (integrated)", 120, "Intel Core Ultra 5 135H"),
    ("Microsoft", "Microsoft Surface Laptop 5 (15-inch)", "General", "2022-10", 134999, 16, 512, 15.0, "Intel Iris Xe", 60, "Intel Core i7-1255U"),
    ("Microsoft", "Microsoft Surface Laptop 5", "General", "2022-10", 104999, 8, 256, 13.5, "Intel Iris Xe", 60, "Intel Core i5-1235U"),
    ("Microsoft", "Microsoft Surface Pro 11", "General", "2024-06", 116999, 16, 256, 13.0, "Qualcomm Adreno (integrated)", 120, "Snapdragon X Plus"),
    ("Microsoft", "Microsoft Surface Pro 10", "Business", "2024-04", 129999, 16, 256, 13.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 5 135U"),
    ("Microsoft", "Microsoft Surface Pro 9", "General", "2022-10", 99999, 8, 256, 13.0, "Intel Iris Xe", 120, "Intel Core i5-1235U"),
    ("Microsoft", "Microsoft Surface Laptop Go 3", "Student", "2023-10", 64999, 8, 256, 12.4, "Intel Iris Xe", 60, "Intel Core i5-1235U"),
    ("Microsoft", "Microsoft Surface Laptop Go 2", "Student", "2022-06", 52999, 8, 128, 12.4, "Intel Iris Xe", 60, "Intel Core i5-1135G7"),
    ("Microsoft", "Microsoft Surface Go 4", "Student", "2023-09", 49999, 8, 128, 10.5, "Intel UHD (integrated)", 60, "Intel Processor N200"),

    # === Razer (8 models - Gaming) ===
    ("Razer", "Razer Blade 18 (2024)", "Gaming", "2024-04", 399999, 32, 2048, 18.0, "NVIDIA GeForce RTX 4090", 200, "Intel Core i9-14900HX"),
    ("Razer", "Razer Blade 16 (2024)", "Gaming", "2024-03", 299999, 32, 1024, 16.0, "NVIDIA GeForce RTX 4080", 240, "Intel Core i9-14900HX"),
    ("Razer", "Razer Blade 16 (2023)", "Gaming", "2023-02", 269999, 16, 1024, 16.0, "NVIDIA GeForce RTX 4070", 240, "Intel Core i9-13950HX"),
    ("Razer", "Razer Blade 14 (2024)", "Gaming", "2024-03", 239999, 16, 1024, 14.0, "NVIDIA GeForce RTX 4070", 240, "AMD Ryzen 9 8945HS"),
    ("Razer", "Razer Blade 14 (2023)", "Gaming", "2023-06", 209999, 16, 1024, 14.0, "NVIDIA GeForce RTX 4060", 240, "AMD Ryzen 9 7940HS"),
    ("Razer", "Razer Blade 15 (2023)", "Gaming", "2023-03", 219999, 16, 1024, 15.6, "NVIDIA GeForce RTX 4070", 240, "Intel Core i7-13800H"),
    ("Razer", "Razer Blade 17 (2022)", "Gaming", "2022-04", 279999, 32, 1024, 17.3, "NVIDIA GeForce RTX 3070 Ti", 240, "Intel Core i7-12800H"),
    ("Razer", "Razer Book 13", "General", "2020-11", 119999, 16, 512, 13.4, "Intel Iris Xe", 60, "Intel Core i7-1165G7"),

    # === Gigabyte & AORUS (12 models - Gaming & Creator) ===
    ("Gigabyte", "Gigabyte AORUS 17X (2024)", "Gaming", "2024-03", 319990, 32, 2048, 17.3, "NVIDIA GeForce RTX 4090", 240, "Intel Core i9-14900HX"),
    ("Gigabyte", "Gigabyte AORUS 16X", "Gaming", "2024-04", 209990, 32, 1024, 16.0, "NVIDIA GeForce RTX 4070", 165, "Intel Core i9-14900HX"),
    ("Gigabyte", "Gigabyte AORUS 15 (2024)", "Gaming", "2024-02", 149990, 16, 1024, 15.6, "NVIDIA GeForce RTX 4070", 165, "Intel Core i7-13650HX"),
    ("Gigabyte", "Gigabyte AORUS 15 (BKF)", "Gaming", "2023-05", 129990, 16, 1024, 15.6, "NVIDIA GeForce RTX 4060", 165, "Intel Core i7-13700H"),
    ("Gigabyte", "Gigabyte AORUS 17 (2024)", "Gaming", "2024-02", 169990, 16, 1024, 17.3, "NVIDIA GeForce RTX 4070", 240, "Intel Core i7-13700H"),
    ("Gigabyte", "Gigabyte AERO 16 OLED", "General", "2023-04", 229990, 32, 1024, 16.0, "NVIDIA GeForce RTX 4070", 60, "Intel Core i9-13900H"),
    ("Gigabyte", "Gigabyte AERO 14 OLED", "General", "2023-05", 159990, 16, 1024, 14.0, "NVIDIA GeForce RTX 4050", 90, "Intel Core i7-13700H"),
    ("Gigabyte", "Gigabyte G6X", "Gaming", "2024-03", 105000, 16, 1024, 16.0, "NVIDIA GeForce RTX 4060", 165, "Intel Core i7-13650HX"),
    ("Gigabyte", "Gigabyte G6 (2024)", "Gaming", "2024-02", 94990, 16, 512, 16.0, "NVIDIA GeForce RTX 4050", 165, "Intel Core i7-13620H"),
    ("Gigabyte", "Gigabyte G5 (KF5)", "Gaming", "2023-04", 77990, 8, 512, 15.6, "NVIDIA GeForce RTX 4060", 144, "Intel Core i5-12500H"),
    ("Gigabyte", "Gigabyte G5 (MF)", "Gaming", "2023-04", 66990, 8, 512, 15.6, "NVIDIA GeForce RTX 4050", 144, "Intel Core i5-12500H"),
    ("Gigabyte", "Gigabyte G5 (GE)", "Gaming", "2022-10", 59990, 8, 512, 15.6, "NVIDIA GeForce RTX 3050", 144, "Intel Core i5-12500H"),

    # === LG Gram (8 models - Ultra-light Normal) ===
    ("LG", "LG Gram 17 (2024)", "General", "2024-04", 149990, 16, 1024, 17.0, "Intel Arc (integrated)", 60, "Intel Core Ultra 7 155H"),
    ("LG", "LG Gram Pro 17", "General", "2024-05", 199990, 32, 1024, 17.0, "NVIDIA GeForce RTX 3050", 144, "Intel Core Ultra 7 155H"),
    ("LG", "LG Gram 16 (2024)", "General", "2024-04", 134990, 16, 512, 16.0, "Intel Arc (integrated)", 60, "Intel Core Ultra 7 155H"),
    ("LG", "LG Gram Pro 16", "General", "2024-05", 179990, 32, 1024, 16.0, "Intel Arc (integrated)", 120, "Intel Core Ultra 7 155H"),
    ("LG", "LG Gram 14 (2024)", "General", "2024-04", 119990, 16, 512, 14.0, "Intel Arc (integrated)", 60, "Intel Core Ultra 5 125H"),
    ("LG", "LG Gram Style 16", "General", "2023-06", 144990, 16, 512, 16.0, "Intel Iris Xe", 120, "Intel Core i7-1360P"),
    ("LG", "LG Gram 2-in-1 16", "General", "2023-05", 139990, 16, 512, 16.0, "Intel Iris Xe", 60, "Intel Core i7-1360P"),
    ("LG", "LG Gram 17 (2023)", "General", "2023-04", 129990, 16, 512, 17.0, "Intel Iris Xe", 60, "Intel Core i5-1340P"),
]

PHONE_DECAY = {
    "Apple": 0.006, "Google": 0.014, "Samsung": 0.012, "Nothing": 0.015,
    "OnePlus": 0.014, "Xiaomi": 0.015, "Redmi": 0.017, "realme": 0.017,
    "vivo": 0.016, "OPPO": 0.016, "Motorola": 0.017, "POCO": 0.018,
    "Honor": 0.016, "ASUS": 0.015,
}

LAPTOP_DECAY = {
    "Apple": 0.006, "Gaming": 0.011, "Business": 0.008, "General": 0.009,
    "Student": 0.010, "Razer": 0.009, "LG": 0.009,
}


def ym(s: str) -> date:
    y, m = s.split("-")
    return date(int(y), int(m), 1)


def month_add(d: date, n: int) -> date:
    m = d.month - 1 + n
    return date(d.year + m // 12, m % 12 + 1, 1)


def build_devices():
    out = []
    for i, p in enumerate(PHONES, start=101):
        brand, name, rel, price, ram, sto, disp, bat, cam, cpu = p
        specs = f"RAM={ram} GB;Storage={sto} GB;Display={disp} inch;Battery={bat} mAh;Camera={cam} MP;Processor={cpu}"
        out.append((f"SP{i:03d}", name, brand, "Smartphone", ym(rel), price, specs, PHONE_DECAY.get(brand, 0.017)))
    for i, l in enumerate(LAPTOPS, start=101):
        brand, name, kind, rel, price, ram, sto, disp, gpu, hz, cpu = l
        sto_txt = f"{sto // 1024} TB" if sto >= 1024 else f"{sto} GB"
        specs = f"RAM={ram} GB;Storage={sto_txt};Display={disp} inch;GPU={gpu};Refresh rate={hz} Hz;Processor={cpu};Laptop type={kind}"
        decay = LAPTOP_DECAY.get(brand, LAPTOP_DECAY.get(kind, 0.010))
        out.append((f"LP{i:03d}", name, brand, "Laptop", ym(rel), price, specs, decay))
    return out


def main():
    rng = random.Random(2026)
    OUT.mkdir(parents=True, exist_ok=True)
    devices = build_devices()
    phones = [d for d in devices if d[3] == "Smartphone"]
    laptops = [d for d in devices if d[3] == "Laptop"]
    gaming_laptops = [d for d in laptops if "Laptop type=Gaming" in d[6]]
    normal_laptops = [d for d in laptops if "Laptop type=Gaming" not in d[6]]

    print(f"Total Phones: {len(phones)}")
    print(f"Total Laptops: {len(laptops)} (Normal/Business/Student: {len(normal_laptops)}, Gaming: {len(gaming_laptops)})")
    print(f"Grand Total Devices: {len(devices)}")

    ids = [d[0] for d in devices]
    assert len(ids) == len(set(ids)), f"Duplicate IDs found: {len(ids)} vs {len(set(ids))}"
    names = [d[1] for d in devices]
    assert len(names) == len(set(names)), f"Duplicate names found: {len(names)} vs {len(set(names))}"

    with open(OUT / "sample_devices.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["device_id", "name", "brand", "category", "release_date", "launch_price", "currency", "status", "specs"])
        for did, name, brand, cat, rel, price, specs, _ in devices:
            w.writerow([did, name, brand, cat, rel.isoformat(), price, "INR", "Active", specs])

    rows = 0
    with open(OUT / "sample_price_history_DEMO.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["device_id", "device_name", "category", "date", "price", "source", "currency"])
        for did, name, brand, cat, rel, price, specs, decay in devices:
            months = min(36, (END.year - rel.year) * 12 + END.month - rel.month + 1)
            first = month_add(END, -(months - 1))
            for i in range(months):
                d = month_add(first, i)
                age = (d.year - rel.year) * 12 + d.month - rel.month
                p = price * math.exp(-decay * age) * (1 + rng.gauss(0, 0.012))
                if d.month in (10, 11):  # festive-season discounts
                    p *= 1 - rng.uniform(0.02, 0.05)
                w.writerow([did, name, cat, d.isoformat(), max(500, round(p / 10) * 10), "SAMPLE-DEMO-SYNTHETIC", "INR"])
                rows += 1

    print(f"Successfully wrote {len(devices)} devices and {rows} price history rows to {OUT}")


if __name__ == "__main__":
    main()
