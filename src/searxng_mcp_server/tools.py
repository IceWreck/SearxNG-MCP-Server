from typing import Any
from datetime import datetime

import httpx

from .config import Config
from .log import get_logger
from .models import (
    ImageResult,
    ImageSearchResponse,
    NewsResult,
    NewsSearchResponse,
    SearchResult,
    VideoResult,
    VideoSearchResponse,
    SearchResponse,
)

logger = get_logger(__name__)


class SearxNGClient:
    """Client for interacting with SearxNG API."""

    def __init__(self, config: Config) -> None:
        """Initialize the SearxNG client.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.client = httpx.Client(timeout=config.timeout, headers={"User-Agent": config.user_agent})

    def search(
        self,
        query: str,
        categories: list[str] | None = None,
        engines: list[str] | None = None,
        language: str | None = None,
        time_range: str | None = None,
        safesearch: bool | None = None,
        page: int = 1,
    ) -> dict[str, Any]:
        """Perform a search query on SearxNG.

        Args:
            query: Search query string
            categories: List of categories to search in (e.g., ['general', 'images', 'videos'])
            engines: List of search engines to use
            language: Language code for results (e.g., 'en', 'en-US')
            time_range: Time range filter ('day', 'week', 'month', 'year')
            safesearch: Safe search filtering (default: true)
            page: Page number for pagination

        Returns:
            Search results dictionary

        Raises:
            httpx.HTTPError: If the request fails
        """
        params = {
            "q": query,
            "format": "json",
            "pageno": page,
        }

        if categories:
            params["categories"] = ",".join(categories)
        if engines:
            params["engines"] = ",".join(engines)
        if language:
            params["language"] = language
        if time_range:
            params["time_range"] = time_range
        if safesearch is not None:
            params["safesearch"] = 1 if safesearch else 0
        else:
            params["safesearch"] = 1  # Default to safe search

        try:
            response = self.client.get(
                f"{self.config.searxng_url}/search",
                params=params,  # type: ignore[arg-type]
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("search request failed: %s", e)
            raise

    def _create_search_results(self, raw_results: dict[str, Any]) -> list[SearchResult]:
        """Convert SearxNG raw results to SearchResult models.

        Args:
            raw_results: Raw results from SearxNG API

        Returns:
            List of SearchResult objects
        """
        results = []
        for result in raw_results.get("results", []):
            published_date = None
            if result.get("publishedDate"):
                try:
                    published_date = datetime.fromisoformat(result["publishedDate"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

            search_result = SearchResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("content"),
                engine=result.get("engine", "unknown"),
                score=result.get("score"),
                published_date=published_date,
            )
            results.append(search_result)

        return results

    def _create_image_results(self, raw_results: dict[str, Any]) -> list[ImageResult]:
        """Convert SearxNG raw results to ImageResult models.

        Args:
            raw_results: Raw results from SearxNG API

        Returns:
            List of ImageResult objects
        """
        results = []
        for result in raw_results.get("results", []):
            published_date = None
            if result.get("publishedDate"):
                try:
                    published_date = datetime.fromisoformat(result["publishedDate"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

            image_result = ImageResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("content"),
                engine=result.get("engine", "unknown"),
                score=result.get("score"),
                published_date=published_date,
                thumbnail_url=result.get("thumbnail"),
                image_url=result.get("img_src"),
            )
            results.append(image_result)

        return results

    def _create_video_results(self, raw_results: dict[str, Any]) -> list[VideoResult]:
        """Convert SearxNG raw results to VideoResult models.

        Args:
            raw_results: Raw results from SearxNG API

        Returns:
            List of VideoResult objects
        """
        results = []
        for result in raw_results.get("results", []):
            published_date = None
            if result.get("publishedDate"):
                try:
                    published_date = datetime.fromisoformat(result["publishedDate"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

            video_result = VideoResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("content"),
                engine=result.get("engine", "unknown"),
                score=result.get("score"),
                published_date=published_date,
                thumbnail_url=result.get("thumbnail"),
            )
            results.append(video_result)

        return results

    def _create_news_results(self, raw_results: dict[str, Any]) -> list[NewsResult]:
        """Convert SearxNG raw results to NewsResult models.

        Args:
            raw_results: Raw results from SearxNG API

        Returns:
            List of NewsResult objects
        """
        results = []
        for result in raw_results.get("results", []):
            published_date = None
            if result.get("publishedDate"):
                try:
                    published_date = datetime.fromisoformat(result["publishedDate"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

            news_result = NewsResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("content"),
                engine=result.get("engine", "unknown"),
                score=result.get("score"),
                published_date=published_date,
                source=result.get("engine", "unknown"),
            )
            results.append(news_result)

        return results

    def search_web(
        self,
        query: str,
        categories: list[str] | None = None,
        engines: list[str] | None = None,
        language: str | None = None,
        time_range: str | None = None,
        safesearch: bool | None = None,
        max_results: int | None = None,
    ) -> SearchResponse:
        """Search the web using SearxNG.

        Args:
            query: Search query string
            categories: List of categories to search in
            engines: List of specific search engines to use
            language: Language code for results
            time_range: Time range filter ('day', 'week', 'month', 'year')
            safesearch: Safe search filtering
            max_results: Maximum number of results to return

        Returns:
            SearchResponse with web search results
        """
        try:
            raw_results = self.search(
                query=query,
                categories=categories,
                engines=engines,
                language=language,
                time_range=time_range,
                safesearch=safesearch,
            )

            search_results = self._create_search_results(raw_results)

            # Apply max_results limit if specified
            if max_results is not None and max_results > 0:
                search_results = search_results[:max_results]

            return SearchResponse(
                query=query,
                total_results=raw_results.get("number_of_results", 0),
                results=search_results,
                error=None,
            )
        except Exception as e:
            logger.error("search_web failed: %s", e)
            return SearchResponse(query=query, total_results=0, results=[], error=str(e))

    def search_images(self, query: str, max_results: int | None = None) -> ImageSearchResponse:
        """Search for images using SearxNG.

        Args:
            query: Image search query
            max_results: Maximum number of results to return

        Returns:
            ImageSearchResponse with image search results
        """
        try:
            raw_results = self.search(query=query, categories=["images"])
            image_results = self._create_image_results(raw_results)

            # Apply max_results limit if specified
            if max_results is not None and max_results > 0:
                image_results = image_results[:max_results]

            return ImageSearchResponse(
                query=query,
                total_results=raw_results.get("number_of_results", 0),
                results=image_results,
                error=None,
            )
        except Exception as e:
            logger.error("search_images failed: %s", e)
            return ImageSearchResponse(query=query, total_results=0, results=[], error=str(e))

    def search_videos(self, query: str, max_results: int | None = None) -> VideoSearchResponse:
        """Search for videos using SearxNG.

        Args:
            query: Video search query
            max_results: Maximum number of results to return

        Returns:
            VideoSearchResponse with video search results
        """
        try:
            raw_results = self.search(query=query, categories=["videos"])
            video_results = self._create_video_results(raw_results)

            # Apply max_results limit if specified
            if max_results is not None and max_results > 0:
                video_results = video_results[:max_results]

            return VideoSearchResponse(
                query=query,
                total_results=raw_results.get("number_of_results", 0),
                results=video_results,
                error=None,
            )
        except Exception as e:
            logger.error("search_videos failed: %s", e)
            return VideoSearchResponse(query=query, total_results=0, results=[], error=str(e))

    def search_news(
        self,
        query: str,
        time_range: str | None = None,
        max_results: int | None = None,
    ) -> NewsSearchResponse:
        """Search for news using SearxNG.

        Args:
            query: News search query
            time_range: Time range filter ('day', 'week', 'month', 'year')
            max_results: Maximum number of results to return

        Returns:
            NewsSearchResponse with news search results
        """
        try:
            raw_results = self.search(query=query, categories=["news"], time_range=time_range)
            news_results = self._create_news_results(raw_results)

            # Apply max_results limit if specified
            if max_results is not None and max_results > 0:
                news_results = news_results[:max_results]

            return NewsSearchResponse(
                query=query,
                total_results=raw_results.get("number_of_results", 0),
                results=news_results,
                error=None,
            )
        except Exception as e:
            logger.error("search_news failed: %s", e)
            return NewsSearchResponse(query=query, total_results=0, results=[], error=str(e))
