from sqlalchemy.orm import Session

from app.models.mission import Mission
from app.schemas.mission import MissionCreate, MissionUpdate


def create_mission(
    db: Session,
    data: MissionCreate,
):
    mission = Mission(
        title=data.title,
        objective=data.objective,
        agent_id=data.agent_id,
    )

    db.add(mission)
    db.commit()
    db.refresh(mission)

    return mission


def get_missions(db: Session):
    return db.query(Mission).all()


def get_mission(
    db: Session,
    mission_id: int,
):
    return (
        db.query(Mission)
        .filter(Mission.id == mission_id)
        .first()
    )


def update_mission(
    db: Session,
    mission_id: int,
    data: MissionUpdate,
):
    mission = get_mission(
        db,
        mission_id,
    )

    if not mission:
        return None

    if data.title is not None:
        mission.title = data.title

    if data.objective is not None:
        mission.objective = data.objective

    if data.status is not None:
        mission.status = data.status

    if data.result is not None:
        mission.result = data.result

    db.commit()
    db.refresh(mission)

    return mission


def delete_mission(
    db: Session,
    mission_id: int,
):
    mission = get_mission(
        db,
        mission_id,
    )

    if not mission:
        return None

    db.delete(mission)
    db.commit()

    return mission