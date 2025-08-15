import asyncio, uuid
from sqlalchemy import text
from app.db.session import AsyncSessionMaker
from app.db.models.organization import Organization
from app.db.models.user import User
from app.db.models.membership import Membership

async def main():
    async with AsyncSessionMaker() as s:
        # 1. Create an organization and a user
        org_id = uuid.uuid4()
        org = Organization(id=org_id, name="Acme Corp")
        user = User(email="alice@example.com", full_name="Alice")
        s.add_all([org, user])
        await s.flush()

        # 2. Set the current tenant (important for RLS)
        await s.execute(
            text("SELECT set_config('app.current_org_id', :org, true)"),
            {"org": str(org_id)},
        )

        # 3. Create a membership (this is tenant-scoped)
        mem = Membership(org_id=org_id, user_id=user.id, role="owner")
        s.add(mem)
        await s.commit()

    # 4. Open a new session with the WRONG tenant id
    async with AsyncSessionMaker() as s2:
        wrong_org = uuid.uuid4()
        await s2.execute(
            text("SELECT set_config('app.current_org_id', :org, true)"),
            {"org": str(wrong_org)},
        )
        rows = (await s2.execute(text("SELECT count(*) FROM memberships"))).scalar_one()
        print("memberships count with wrong tenant:", rows)  # Expect 0

if __name__ == "__main__":
    asyncio.run(main())
