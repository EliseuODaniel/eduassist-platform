from __future__ import annotations

from sqlalchemy import select

from api_core.db.models import FederatedIdentity, User
from api_core.db.session import session_scope


KEYCLOAK_BINDINGS = [
    {
        'external_code': 'USR-GUARD-001',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b1001',
        'username': 'maria.oliveira',
        'email': 'maria.oliveira@mock.eduassist.local',
    },
    {
        'external_code': 'USR-GUARD-002',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b1002',
        'username': 'paulo.santos',
        'email': 'paulo.santos@mock.eduassist.local',
    },
    {
        'external_code': 'USR-STUD-001',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b2001',
        'username': 'lucas.oliveira',
        'email': 'lucas.oliveira@mock.eduassist.local',
    },
    {
        'external_code': 'USR-STUD-002',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b2002',
        'username': 'ana.oliveira',
        'email': 'ana.oliveira@mock.eduassist.local',
    },
    {
        'external_code': 'USR-STUD-003',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b2003',
        'username': 'bruno.santos',
        'email': 'bruno.santos@mock.eduassist.local',
    },
    {
        'external_code': 'USR-TEACH-001',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b3001',
        'username': 'helena.rocha',
        'email': 'helena.rocha@mock.eduassist.local',
    },
    {
        'external_code': 'USR-TEACH-002',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b3002',
        'username': 'marcos.lima',
        'email': 'marcos.lima@mock.eduassist.local',
    },
    {
        'external_code': 'USR-STAFF-001',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b4001',
        'username': 'beatriz.costa',
        'email': 'beatriz.costa@mock.eduassist.local',
    },
    {
        'external_code': 'USR-FIN-001',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b4002',
        'username': 'carla.nogueira',
        'email': 'carla.nogueira@mock.eduassist.local',
    },
    {
        'external_code': 'USR-GUARD-003',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b1201',
        'username': 'fernanda.souza',
        'email': 'fernanda.souza@mock.eduassist.local',
    },
    {
        'external_code': 'USR-GUARD-004',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b1202',
        'username': 'roberto.araujo',
        'email': 'roberto.araujo@mock.eduassist.local',
    },
    {
        'external_code': 'USR-GUARD-005',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b1203',
        'username': 'juliana.lima',
        'email': 'juliana.lima@mock.eduassist.local',
    },
    {
        'external_code': 'USR-GUARD-006',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b1204',
        'username': 'carla.mendes',
        'email': 'carla.mendes@mock.eduassist.local',
    },
    {
        'external_code': 'USR-STUD-004',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b2201',
        'username': 'gabriel.souza',
        'email': 'gabriel.souza@mock.eduassist.local',
    },
    {
        'external_code': 'USR-STUD-005',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b2202',
        'username': 'sofia.souza',
        'email': 'sofia.souza@mock.eduassist.local',
    },
    {
        'external_code': 'USR-STUD-006',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b2203',
        'username': 'marina.araujo',
        'email': 'marina.araujo@mock.eduassist.local',
    },
    {
        'external_code': 'USR-STUD-007',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b2204',
        'username': 'pedro.lima',
        'email': 'pedro.lima@mock.eduassist.local',
    },
    {
        'external_code': 'USR-STUD-008',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b2205',
        'username': 'isabela.lima',
        'email': 'isabela.lima@mock.eduassist.local',
    },
    {
        'external_code': 'USR-STUD-009',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b2206',
        'username': 'thiago.mendes',
        'email': 'thiago.mendes@mock.eduassist.local',
    },
    {
        'external_code': 'USR-TEACH-003',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b3203',
        'username': 'daniela.campos',
        'email': 'daniela.campos@mock.eduassist.local',
    },
    {
        'external_code': 'USR-TEACH-004',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b3204',
        'username': 'rafael.gomes',
        'email': 'rafael.gomes@mock.eduassist.local',
    },
    {
        'external_code': 'USR-TEACH-005',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b3205',
        'username': 'patricia.neves',
        'email': 'patricia.neves@mock.eduassist.local',
    },
    {
        'external_code': 'USR-TEACH-006',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b3206',
        'username': 'tiago.moura',
        'email': 'tiago.moura@mock.eduassist.local',
    },
    {
        'external_code': 'USR-TEACH-007',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b3207',
        'username': 'luana.ferraz',
        'email': 'luana.ferraz@mock.eduassist.local',
    },
    {
        'external_code': 'USR-COORD-001',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b5201',
        'username': 'murilo.bastos',
        'email': 'murilo.bastos@mock.eduassist.local',
    },
]


def main() -> None:
    created = 0
    updated = 0

    with session_scope() as session:
        for binding in KEYCLOAK_BINDINGS:
            user = session.execute(
                select(User).where(User.external_code == binding['external_code'])
            ).scalar_one_or_none()
            if user is None:
                print(f"skip missing user {binding['external_code']}")
                continue

            existing_by_subject = session.execute(
                select(FederatedIdentity)
                .where(FederatedIdentity.provider == 'keycloak')
                .where(FederatedIdentity.subject == binding['subject'])
            ).scalar_one_or_none()
            if existing_by_subject is not None and existing_by_subject.user_id != user.id:
                raise RuntimeError(
                    f"subject {binding['subject']} already linked to another user {existing_by_subject.user_id}"
                )

            identity = session.execute(
                select(FederatedIdentity)
                .where(FederatedIdentity.user_id == user.id)
                .where(FederatedIdentity.provider == 'keycloak')
            ).scalar_one_or_none()

            if identity is None:
                identity = FederatedIdentity(
                    user_id=user.id,
                    provider='keycloak',
                    subject=binding['subject'],
                    username=binding['username'],
                    email=binding['email'],
                    email_verified=True,
                )
                session.add(identity)
                created += 1
            else:
                identity.subject = binding['subject']
                identity.username = binding['username']
                identity.email = binding['email']
                identity.email_verified = True
                updated += 1

    print(f'auth bindings synced: created={created} updated={updated}')


if __name__ == '__main__':
    main()
