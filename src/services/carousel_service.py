from dataclasses import dataclass, field
from pathlib import Path

from src.platforms.instagram import (
    InstagramPostResult,
    MediaItem,
    download_instagram_item,
)

from src.services.preview_service import (
    PreviewResult,
    create_image_preview,
)


@dataclass
class CarouselSession:
    """
    Maintains the state of an Instagram carousel
    download session.

    Supported in V1:
        - Images

    Detected but not yet supported:
        - Videos
    """

    result: InstagramPostResult
    downloaded_indices: set[int] = field(default_factory=set)

    # --------------------------------------------------
    # BASIC INFORMATION
    # --------------------------------------------------

    @property
    def total_items(self) -> int:
        return len(self.result.items)

    @property
    def downloaded_count(self) -> int:
        return len(self.downloaded_indices)

    # --------------------------------------------------
    # SUPPORTED / UNSUPPORTED ITEMS
    # --------------------------------------------------

    @property
    def supported_items(self) -> list[MediaItem]:
        """
        Items that can currently be downloaded.
        """

        return [
            item
            for item in self.result.items
            if item.download_supported
        ]

    @property
    def unsupported_items(self) -> list[MediaItem]:
        """
        Items detected correctly but not supported yet.
        """

        return [
            item
            for item in self.result.items
            if not item.download_supported
        ]

    @property
    def unsupported_indices(self) -> list[int]:
        return [
            item.index
            for item in self.unsupported_items
        ]

    # --------------------------------------------------
    # REMAINING ITEMS
    # --------------------------------------------------

    @property
    def remaining_items(self) -> list[MediaItem]:
        """
        Supported items that have not been downloaded yet.

        Unsupported items such as carousel videos are
        intentionally excluded.
        """

        return [
            item
            for item in self.supported_items
            if item.index not in self.downloaded_indices
        ]

    @property
    def remaining_indices(self) -> list[int]:
        return [
            item.index
            for item in self.remaining_items
        ]

    # --------------------------------------------------
    # GET ITEM
    # --------------------------------------------------

    def get_item(self, index: int) -> MediaItem:

        for item in self.result.items:

            if item.index == index:
                return item

        raise ValueError(
            f"Instagram carousel item {index} does not exist."
        )

    # --------------------------------------------------
    # VALIDATE SELECTION
    # --------------------------------------------------

    def validate_selection(
        self,
        selected_indices: list[int],
    ) -> None:

        if not selected_indices:

            raise ValueError(
                "No Instagram items were selected."
            )

        if len(selected_indices) != len(
            set(selected_indices)
        ):

            raise ValueError(
                "Duplicate Instagram item indices "
                "are not allowed."
            )

        available_indices = {
            item.index
            for item in self.result.items
        }

        invalid_indices = [
            index
            for index in selected_indices
            if index not in available_indices
        ]

        if invalid_indices:

            raise ValueError(
                "Invalid Instagram item index: "
                f"{invalid_indices}"
            )

        already_downloaded = [
            index
            for index in selected_indices
            if index in self.downloaded_indices
        ]

        if already_downloaded:

            raise ValueError(
                "These Instagram items have already "
                f"been downloaded: {already_downloaded}"
            )

        unsupported_indices = [
            index
            for index in selected_indices
            if not self.get_item(index).download_supported
        ]

        if unsupported_indices:

            raise ValueError(
                "These Instagram carousel items are "
                "currently unsupported because they "
                "contain video: "
                f"{unsupported_indices}\n"
                "Carousel video downloading will be "
                "implemented soon."
            )

    # --------------------------------------------------
    # PREVIEW
    # --------------------------------------------------

    def preview_item(
        self,
        index: int,
    ) -> PreviewResult:

        item = self.get_item(index)

        # ----------------------------------------------
        # VIDEO
        # ----------------------------------------------

        if item.media_type == "video":

            raise ValueError(
                f"Instagram carousel item {index} "
                "is a video.\n"
                "Video preview will be implemented soon."
            )

        # ----------------------------------------------
        # IMAGE
        # ----------------------------------------------

        if item.media_type != "image":

            raise ValueError(
                "Preview is currently supported "
                "only for image carousel items."
            )

        if not item.url:

            raise RuntimeError(
                f"Instagram carousel item {index} "
                "does not have a media URL."
            )

        return create_image_preview(
            item.url
        )

    # --------------------------------------------------
    # DOWNLOAD SELECTED
    # --------------------------------------------------

    def download_selected(
        self,
        selected_indices: list[int],
        choice: str | None = None,
    ) -> list[Path]:

        self.validate_selection(
            selected_indices
        )

        selected_items = [
            self.get_item(index)
            for index in selected_indices
        ]

        downloaded_files: list[Path] = []

        for item in selected_items:

            output_path = download_instagram_item(
                item,
                choice=choice,
            )

            downloaded_files.append(
                output_path
            )

            self.downloaded_indices.add(
                item.index
            )

        return downloaded_files

    # --------------------------------------------------
    # DOWNLOAD ALL SUPPORTED ITEMS
    # --------------------------------------------------

    def download_all(
        self,
        choice: str | None = None,
    ) -> list[Path]:

        remaining_indices = [
            item.index
            for item in self.remaining_items
        ]

        if not remaining_indices:

            raise ValueError(
                "All currently supported Instagram "
                "carousel items have already been "
                "downloaded."
            )

        return self.download_selected(
            remaining_indices,
            choice=choice,
        )

    # --------------------------------------------------
    # DOWNLOAD REMAINING
    # --------------------------------------------------

    def download_remaining(
        self,
        choice: str | None = None,
    ) -> list[Path]:

        return self.download_all(
            choice=choice
        )

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    def status(self) -> dict:

        return {
            "total": self.total_items,
            "downloaded": self.downloaded_count,
            "remaining": len(
                self.remaining_items
            ),
            "downloaded_indices": sorted(
                self.downloaded_indices
            ),
            "remaining_indices": [
                item.index
                for item in self.remaining_items
            ],
            "unsupported_indices": (
                self.unsupported_indices
            ),
        }

    # --------------------------------------------------
    # COMPLETION
    # --------------------------------------------------

    @property
    def is_complete(self) -> bool:
        """
        The carousel session is complete when all
        currently supported items have been downloaded.

        Unsupported video items do not prevent completion.
        """

        return len(
            self.remaining_items
        ) == 0