"""
Admin table editor API with SQL injection protection.

SECURITY NOTE:
- SQLite does not support parameterized table/column identifiers
- All table and column names MUST be validated against the database schema
  before being interpolated into SQL strings
- Only VALUES can use ? placeholders; identifiers require validation + interpolation

TODO: These endpoints are not currently restricted to admin role at the API layer.
No session/auth middleware exists yet. This should be protected once auth middleware is implemented.
"""

from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from db.database import Database
import sqlite3

router = APIRouter()


# ========== Helper Functions for SQL Injection Protection ==========

def get_all_tables() -> list[str]:
    """
    Get list of all user tables from sqlite_master.

    Returns:
        List of table names (excluding sqlite_* system tables)
    """
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)

    tables = [row['name'] for row in cursor.fetchall()]
    conn.close()

    return tables


def validate_table_name(table_name: str) -> bool:
    """
    Validate that a table name exists in the database schema.

    CRITICAL: Must be called before interpolating table_name into any SQL string.
    SQLite does not support ? placeholders for table names.

    Args:
        table_name: The table name to validate

    Returns:
        True if table exists, False otherwise
    """
    all_tables = get_all_tables()
    return table_name in all_tables


def get_table_columns(table_name: str) -> list[dict]:
    """
    Get column information for a validated table.

    Args:
        table_name: Table name (must be pre-validated with validate_table_name)

    Returns:
        List of column definitions with: name, type, notnull, pk, dflt_value

    Raises:
        ValueError: If table_name is not validated
    """
    if not validate_table_name(table_name):
        raise ValueError(f"Invalid table name: {table_name}")

    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()

    # Safe to use table_name here because it's validated
    # Note: PRAGMA table_info doesn't support ? placeholders, but we've validated
    cursor.execute(f"PRAGMA table_info({table_name})")

    columns = []
    for row in cursor.fetchall():
        columns.append({
            "name": row['name'],
            "type": row['type'],
            "notnull": bool(row['notnull']),
            "pk": bool(row['pk']),
            "default_value": row['dflt_value']
        })

    conn.close()
    return columns


def get_primary_keys(table_name: str) -> list[str]:
    """
    Get primary key column names for a validated table.

    Args:
        table_name: Table name (must be pre-validated with validate_table_name)

    Returns:
        List of primary key column names

    Raises:
        ValueError: If table_name is not validated
    """
    columns = get_table_columns(table_name)
    return [col['name'] for col in columns if col['pk']]


def validate_column_names(table_name: str, column_names: list[str]) -> bool:
    """
    Validate that all column names exist in the table schema.

    Args:
        table_name: Table name (must be pre-validated)
        column_names: List of column names to validate

    Returns:
        True if all columns exist, False otherwise
    """
    columns = get_table_columns(table_name)
    valid_columns = {col['name'] for col in columns}
    return all(col in valid_columns for col in column_names)


# ========== Request/Response Models ==========

class TableListResponse(BaseModel):
    """Response model for GET /tables"""
    tables: list[str]


class ColumnInfo(BaseModel):
    """Column information from PRAGMA table_info"""
    name: str
    type: str
    notnull: bool
    pk: bool
    default_value: Optional[str]


class TableSchemaResponse(BaseModel):
    """Response model for GET /tables/{table_name}/schema"""
    table_name: str
    columns: list[ColumnInfo]


class RowsResponse(BaseModel):
    """Response model for GET /tables/{table_name}/rows"""
    table_name: str
    rows: list[dict]
    count: int


class CreateRowRequest(BaseModel):
    """Request model for POST /tables/{table_name}/rows"""
    data: Dict[str, Any]


class DeleteRowRequest(BaseModel):
    """Request model for DELETE /tables/{table_name}/rows"""
    primary_key: Dict[str, Any]


class SubmittedDocsResponse(BaseModel):
    """Response model for GET /submitted-docs"""
    user_id: str
    documents: list[dict]
    count: int


# ========== API Endpoints ==========

@router.get("/admin/tables", response_model=TableListResponse)
async def list_tables():
    """
    Get list of all user tables in the database.

    Returns:
        List of table names (excluding sqlite_* system tables)
    """
    tables = get_all_tables()
    return TableListResponse(tables=tables)


@router.get("/admin/tables/{table_name}/schema", response_model=TableSchemaResponse)
async def get_table_schema(table_name: str):
    """
    Get schema information for a specific table.

    Args:
        table_name: Name of the table

    Returns:
        Column definitions including name, type, nullable, primary key flags

    Raises:
        HTTPException 404: If table does not exist
    """
    # SECURITY: Validate table name before any SQL operations
    if not validate_table_name(table_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table '{table_name}' not found"
        )

    columns = get_table_columns(table_name)

    return TableSchemaResponse(
        table_name=table_name,
        columns=[ColumnInfo(**col) for col in columns]
    )


@router.get("/admin/tables/{table_name}/rows", response_model=RowsResponse)
async def get_table_rows(table_name: str):
    """
    Get all rows from a specific table.

    Args:
        table_name: Name of the table

    Returns:
        All rows as list of dictionaries

    Raises:
        HTTPException 404: If table does not exist
    """
    # SECURITY: Validate table name before any SQL operations
    if not validate_table_name(table_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table '{table_name}' not found"
        )

    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()

    # Safe to interpolate table_name here because it's validated
    cursor.execute(f"SELECT * FROM {table_name}")

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return RowsResponse(
        table_name=table_name,
        rows=rows,
        count=len(rows)
    )


@router.post("/admin/tables/{table_name}/rows")
async def create_row(table_name: str, request: CreateRowRequest):
    """
    Insert a new row into a table.

    Args:
        table_name: Name of the table
        request: Row data as dictionary of column_name: value

    Returns:
        Success message with row ID if applicable

    Raises:
        HTTPException 404: If table does not exist
        HTTPException 400: If column names are invalid or insert fails
    """
    # SECURITY: Validate table name
    if not validate_table_name(table_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table '{table_name}' not found"
        )

    # SECURITY: Validate all column names against schema
    column_names = list(request.data.keys())
    if not validate_column_names(table_name, column_names):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"One or more column names are invalid for table '{table_name}'"
        )

    # Build parameterized INSERT query
    # Column names are validated, so safe to interpolate
    # Values use ? placeholders for SQL injection protection
    columns_str = ", ".join(column_names)
    placeholders = ", ".join(["?" for _ in column_names])
    values = [request.data[col] for col in column_names]

    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()

        row_id = cursor.lastrowid
        conn.close()

        return {
            "success": True,
            "message": f"Row created in table '{table_name}'",
            "row_id": row_id
        }

    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integrity constraint violation: {str(e)}"
        )
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {str(e)}"
        )


@router.get("/submitted-docs", response_model=SubmittedDocsResponse)
async def get_submitted_docs(user_id: str):
    """
    Get all submitted loan documents for a specific user.

    Args:
        user_id: Username of the user (query parameter)

    Returns:
        List of submitted documents with DOC_TYPE and STATUS

    Raises:
        HTTPException 400: If user_id is not provided
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id query parameter is required"
        )

    db = Database()
    documents = db.get_submitted_docs_by_user(user_id)

    return SubmittedDocsResponse(
        user_id=user_id,
        documents=documents,
        count=len(documents)
    )


@router.delete("/admin/tables/{table_name}/rows")
async def delete_row(table_name: str, request: DeleteRowRequest):
    """
    Delete a row from a table by primary key.

    Args:
        table_name: Name of the table
        request: Primary key column(s) and value(s)

    Returns:
        Success message with number of rows deleted

    Raises:
        HTTPException 404: If table does not exist
        HTTPException 400: If primary key columns are invalid
    """
    # SECURITY: Validate table name
    if not validate_table_name(table_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table '{table_name}' not found"
        )

    # Get actual primary key columns for this table
    pk_columns = get_primary_keys(table_name)

    if not pk_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table '{table_name}' has no primary key defined"
        )

    # SECURITY: Validate that provided PK columns match actual schema
    provided_pk_cols = list(request.primary_key.keys())
    if not all(col in pk_columns for col in provided_pk_cols):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid primary key columns. Expected: {pk_columns}"
        )

    # Build WHERE clause with validated column names
    # Column names are validated, so safe to interpolate
    # Values use ? placeholders for SQL injection protection
    where_clauses = [f"{col} = ?" for col in provided_pk_cols]
    where_str = " AND ".join(where_clauses)
    values = [request.primary_key[col] for col in provided_pk_cols]

    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        query = f"DELETE FROM {table_name} WHERE {where_str}"
        cursor.execute(query, values)
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted_count == 0:
            return {
                "success": False,
                "message": f"No rows found matching primary key in table '{table_name}'",
                "deleted_count": 0
            }

        return {
            "success": True,
            "message": f"Deleted {deleted_count} row(s) from table '{table_name}'",
            "deleted_count": deleted_count
        }

    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {str(e)}"
        )
