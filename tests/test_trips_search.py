"""
Тесты для поиска и фильтрации поездок.

Содержит тесты для:
- Поиска по городам
- Фильтров по цене
- Фильтров по условиям (pets/smoking)
- Сортировки
- Пагинации
- Пустого результата
- Неверных параметров
"""
import pytest
from datetime import date, time

from app.schemas.trips.schemas import (
    TripSearchFilters,
    PaginatedTripSearchResponse,
    MAX_PAGE_SIZE,
    ALLOWED_SORT_BY,
    ALLOWED_SORT_ORDER,
)


class TestTripSearchFilters:
    """Тесты для схемы фильтров поиска поездок."""

    def test_default_values(self):
        """Тест значений по умолчанию."""
        filters = TripSearchFilters()
        
        assert filters.from_city is None
        assert filters.to_city is None
        assert filters.min_price is None
        assert filters.max_price is None
        assert filters.departure_time_start is None
        assert filters.departure_time_end is None
        assert filters.driver_rating_min is None
        assert filters.smoking_allowed is None
        assert filters.luggage_allowed is None
        assert filters.pets_allowed is None
        assert filters.sort_by == "departure_time"
        assert filters.sort_order == "asc"
        assert filters.page == 1
        assert filters.page_size == 10

    def test_search_by_city(self):
        """Тест поиска по городу."""
        filters = TripSearchFilters(
            from_city="Москва",
            to_city="Санкт-Петербург",
        )
        
        assert filters.from_city == "Москва"
        assert filters.to_city == "Санкт-Петербург"

    def test_search_by_city_partial(self):
        """Тест частичного поиска по городу."""
        filters = TripSearchFilters(
            from_city="мос",
        )
        
        assert filters.from_city == "мос"

    def test_price_filter(self):
        """Тест фильтра по цене."""
        filters = TripSearchFilters(
            min_price=500,
            max_price=2000,
        )
        
        assert filters.min_price == 500
        assert filters.max_price == 2000

    def test_price_filter_invalid(self):
        """Тест ошибки при min_price > max_price."""
        with pytest.raises(ValueError):
            TripSearchFilters(
                min_price=2000,
                max_price=500,
            )

    def test_time_filter(self):
        """Тест фильтра по времени."""
        filters = TripSearchFilters(
            departure_time_start=time(10, 0),
            departure_time_end=time(14, 0),
        )
        
        assert filters.departure_time_start == time(10, 0)
        assert filters.departure_time_end == time(14, 0)

    def test_driver_rating_filter(self):
        """Тест фильтра по рейтингу водителя."""
        filters = TripSearchFilters(
            driver_rating_min=4.0,
        )
        
        assert filters.driver_rating_min == 4.0

    def test_driver_rating_filter_invalid(self):
        """Тест ошибки при рейтинге > 5."""
        with pytest.raises(ValueError):
            TripSearchFilters(
                driver_rating_min=6.0,
            )

    def test_params_filter(self):
        """Тест фильтра по параметрам."""
        filters = TripSearchFilters(
            smoking_allowed=True,
            luggage_allowed=True,
            pets_allowed=False,
        )
        
        assert filters.smoking_allowed is True
        assert filters.luggage_allowed is True
        assert filters.pets_allowed is False

    def test_sort_by_price(self):
        """Тест сортировки по цене."""
        filters = TripSearchFilters(
            sort_by="price",
            sort_order="desc",
        )
        
        assert filters.sort_by == "price"
        assert filters.sort_order == "desc"

    def test_sort_by_invalid(self):
        """Тест fallback на дефолт при неверном sort_by."""
        filters = TripSearchFilters(
            sort_by="invalid_field",
        )
        
        assert filters.sort_by == "departure_time"

    def test_sort_order_invalid(self):
        """Тест fallback на asc при неверном sort_order."""
        filters = TripSearchFilters(
            sort_order="invalid",
        )
        
        assert filters.sort_order == "asc"

    def test_pagination(self):
        """Тест пагинации."""
        filters = TripSearchFilters(
            page=2,
            page_size=20,
        )
        
        assert filters.page == 2
        assert filters.page_size == 20

    def test_pagination_max_page_size(self):
        """Тест ограничения page_size максимумом."""
        filters = TripSearchFilters(
            page_size=100,
        )
        
        assert filters.page_size == MAX_PAGE_SIZE

    def test_pagination_min_page(self):
        """Тест минимального page."""
        filters = TripSearchFilters(
            page=0,
        )
        
        # Pydantic валидирует min=1, так что page станет 1
        # Но эта проверка происходит на уровне модели
        assert filters.page >= 1


class TestTripSearchResponse:
    """Тесты для схемы ответа поиска поездок."""

    def test_response_structure(self):
        """Тест структуры ответа."""
        response = PaginatedTripSearchResponse(
            items=[],
            total=0,
            page=1,
            page_size=10,
            pages=0,
        )
        
        assert response.items == []
        assert response.total == 0
        assert response.page == 1
        assert response.page_size == 10
        assert response.pages == 0


class TestEdgeCases:
    """Тесты для крайних случаев."""

    def test_empty_search(self):
        """Тест пустого поиска (без фильтров)."""
        filters = TripSearchFilters()
        
        # Должен вернуть все опубликованные поездки
        assert filters.from_city is None
        assert filters.to_city is None

    def test_all_filters(self):
        """Тест всех фильтров вместе."""
        filters = TripSearchFilters(
            from_city="Москва",
            to_city="Казань",
            min_price=300,
            max_price=1500,
            departure_time_start=time(8, 0),
            departure_time_end=time(20, 0),
            driver_rating_min=3.5,
            smoking_allowed=False,
            luggage_allowed=True,
            pets_allowed=True,
            sort_by="price",
            sort_order="asc",
            page=1,
            page_size=10,
        )
        
        assert filters.from_city == "Москва"
        assert filters.to_city == "Казань"
        assert filters.min_price == 300
        assert filters.max_price == 1500
        assert filters.departure_time_start == time(8, 0)
        assert filters.departure_time_end == time(20, 0)
        assert filters.driver_rating_min == 3.5
        assert filters.smoking_allowed is False
        assert filters.luggage_allowed is True
        assert filters.pets_allowed is True
        assert filters.sort_by == "price"
        assert filters.sort_order == "asc"
        assert filters.page == 1
        assert filters.page_size == 10

    def test_allowed_sort_by_values(self):
        """Тест допустимых значений сортировки."""
        for sort_value in ALLOWED_SORT_BY:
            filters = TripSearchFilters(sort_by=sort_value)
            assert filters.sort_by == sort_value

    def test_allowed_sort_order_values(self):
        """Тест допустимых направлений сортировки."""
        for order_value in ALLOWED_SORT_ORDER:
            filters = TripSearchFilters(sort_order=order_value)
            assert filters.sort_order == order_value