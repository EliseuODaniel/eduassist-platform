from __future__ import annotations

from sqlalchemy import text

from fastapi import FastAPI
from pydantic import BaseModel

from api_core.config import Settings, get_settings
from api_core.db.session import session_scope


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    database: str


app = FastAPI(
    title='EduAssist API Core',
    version='0.1.0',
    summary='Core domain API bootstrap for EduAssist Platform.',
)


@app.get('/healthz', response_model=HealthResponse)
async def healthz() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status='ok',
        service='api-core',
        environment=settings.app_env,
        database='configured',
    )


@app.get('/meta')
async def meta() -> dict[str, str]:
    settings = get_settings()
    return {
        'service': 'api-core',
        'environment': settings.app_env,
        'logLevel': settings.log_level,
        'databaseUrl': settings.database_url,
        'redisUrl': settings.redis_url,
        'opaUrl': settings.opa_url,
    }


@app.get('/v1/status')
async def status() -> dict[str, object]:
    return {
        'service': 'api-core',
        'ready': True,
        'capabilities': [
            'authz-gateway',
            'domain-services',
            'audit-trail',
            'schema-foundation',
        ],
    }


@app.get('/v1/foundation/summary')
async def foundation_summary() -> dict[str, object]:
    counts: dict[str, int] = {}
    queries = {
        'users': 'select count(*) from identity.users',
        'students': 'select count(*) from school.students',
        'guardians': 'select count(*) from school.guardians',
        'teachers': 'select count(*) from school.teachers',
        'classes': 'select count(*) from school.classes',
        'enrollments': 'select count(*) from school.enrollments',
        'grade_items': 'select count(*) from academic.grade_items',
        'grades': 'select count(*) from academic.grades',
        'contracts': 'select count(*) from finance.contracts',
        'invoices': 'select count(*) from finance.invoices',
        'calendar_events': 'select count(*) from calendar.calendar_events',
        'documents': 'select count(*) from documents.documents',
        'document_chunks': 'select count(*) from documents.document_chunks',
    }

    try:
        with session_scope() as session:
            for key, sql in queries.items():
                counts[key] = int(session.execute(text(sql)).scalar_one())
        database = 'reachable'
    except Exception as exc:  # pragma: no cover - bootstrap resilience path
        database = f'unavailable: {exc.__class__.__name__}'

    return {
        'service': 'api-core',
        'database': database,
        'counts': counts,
    }
