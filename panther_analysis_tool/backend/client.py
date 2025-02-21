"""
Panther Analysis Tool is a command line interface for writing,
testing, and packaging policies/rules.
Copyright (C) 2020 Panther Labs Inc

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import base64
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, List, TypeVar

ResponseData = TypeVar("ResponseData")


class BackendError(Exception):
    permanent: bool = False


class PermanentBackendError(BackendError):
    permanent: bool = True


@dataclass(frozen=True)
class BulkUploadPayload:
    data: bytes
    user_id: str


@dataclass(frozen=True)
class BackendResponse(Generic[ResponseData]):
    data: ResponseData
    status_code: int


@dataclass(frozen=True)
class BackendCheckResponse:
    success: bool
    message: str


@dataclass(frozen=True)
class BulkUploadParams:
    zip_bytes: bytes

    def encoded_bytes(self) -> str:
        return base64.b64encode(self.zip_bytes).decode("utf-8")


@dataclass(frozen=True)
class DeleteSavedQueriesParams:
    names: List[str]
    dry_run: bool
    include_detections: bool


@dataclass(frozen=True)
class DeleteDetectionsParams:
    ids: List[str]
    dry_run: bool
    include_saved_queries: bool


@dataclass(frozen=True)
class ListSchemasParams:
    is_managed: bool


@dataclass(frozen=True)
class UpdateSchemaParams:
    description: str
    name: str
    reference_url: str
    revision: int
    spec: str


@dataclass(frozen=True)
class BulkUploadStatistics:
    new: int
    total: int
    modified: int


@dataclass(frozen=True)
class BulkUploadResponse:
    rules: BulkUploadStatistics
    queries: BulkUploadStatistics
    policies: BulkUploadStatistics
    data_models: BulkUploadStatistics
    lookup_tables: BulkUploadStatistics
    global_helpers: BulkUploadStatistics


@dataclass(frozen=True)
class DeleteSavedQueriesResponse:
    names: List[str]
    detection_ids: List[str]


@dataclass(frozen=True)
class DeleteDetectionsResponse:
    ids: List[str]
    saved_query_names: List[str]


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class Schema:
    created_at: str
    description: str
    is_managed: bool
    name: str
    reference_url: str
    revision: int
    spec: str
    updated_at: str


@dataclass(frozen=True)
class ListSchemasResponse:
    schemas: List[Schema]


@dataclass(frozen=True)
class UpdateSchemaResponse:
    schema: Schema


@dataclass(frozen=True)
class PantherSDKBulkUploadParams:
    content: str


@dataclass(frozen=True)
class PantherSDKBulkUploadResponse:
    rules: BulkUploadStatistics
    policies: BulkUploadStatistics
    queries: BulkUploadStatistics
    data_models: BulkUploadStatistics


@dataclass(frozen=True)
class TranspileToPythonParams:
    data: List[str]


@dataclass(frozen=True)
class TranspileToPythonResponse:
    transpiled_python: List[str]


class Client(ABC):
    @abstractmethod
    def check(self) -> BackendCheckResponse:
        pass

    @abstractmethod
    def async_bulk_upload(self, params: BulkUploadParams) -> BackendResponse[BulkUploadResponse]:
        pass

    @abstractmethod
    def bulk_upload(self, params: BulkUploadParams) -> BackendResponse[BulkUploadResponse]:
        pass

    @abstractmethod
    def transpile_simple_detection_to_python(
        self, params: TranspileToPythonParams
    ) -> BackendResponse[TranspileToPythonResponse]:
        pass

    @abstractmethod
    def delete_saved_queries(
        self, params: DeleteSavedQueriesParams
    ) -> BackendResponse[DeleteSavedQueriesResponse]:
        pass

    @abstractmethod
    def delete_detections(
        self, params: DeleteDetectionsParams
    ) -> BackendResponse[DeleteDetectionsResponse]:
        pass

    @abstractmethod
    def list_schemas(self, params: ListSchemasParams) -> BackendResponse[ListSchemasResponse]:
        pass

    @abstractmethod
    def update_schema(self, params: UpdateSchemaParams) -> BackendResponse[Any]:
        pass

    @abstractmethod
    def panthersdk_bulk_upload(
        self, params: PantherSDKBulkUploadParams
    ) -> BackendResponse[PantherSDKBulkUploadResponse]:
        pass

    @abstractmethod
    def supports_async_uploads(self) -> bool:
        pass


def backend_response_failed(resp: BackendResponse) -> bool:
    return resp.status_code >= 400 or resp.data.get("statusCode", 0) >= 400


def to_bulk_upload_response(data: Any) -> BackendResponse[BulkUploadResponse]:
    default_stats = dict(total=0, new=0, modified=0)
    return BackendResponse(
        status_code=200,
        data=BulkUploadResponse(
            rules=BulkUploadStatistics(**data.get("rules", default_stats)),
            queries=BulkUploadStatistics(**data.get("queries", default_stats)),
            policies=BulkUploadStatistics(**data.get("policies", default_stats)),
            data_models=BulkUploadStatistics(**data.get("dataModels", default_stats)),
            lookup_tables=BulkUploadStatistics(**data.get("lookupTables", default_stats)),
            global_helpers=BulkUploadStatistics(**data.get("globalHelpers", default_stats)),
        ),
    )
